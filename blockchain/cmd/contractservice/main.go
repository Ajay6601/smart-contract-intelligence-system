package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"golang.org/x/net/context"

	"github.com/Ajay6601/smart-contract-intelligence/internal/audit"
	"github.com/Ajay6601/smart-contract-intelligence/internal/contracts"
	"github.com/Ajay6601/smart-contract-intelligence/internal/eth"
	"github.com/Ajay6601/smart-contract-intelligence/internal/library"
)

func main() {
	// Load environment variables
	err := godotenv.Load()
	if err != nil {
		log.Println("Warning: .env file not found, using environment variables")
	}

	// Set up MongoDB connection
	mongoURI := os.Getenv("MONGODB_URL")
	if mongoURI == "" {
		mongoURI = "mongodb://localhost:27017"
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatalf("Failed to connect to MongoDB: %v", err)
	}
	defer client.Disconnect(ctx)

	// Check the connection
	err = client.Ping(ctx, nil)
	if err != nil {
		log.Fatalf("Failed to ping MongoDB: %v", err)
	}
	log.Println("Connected to MongoDB")

	// Initialize database collections
	db := client.Database("smart_contract_intelligence")
	contractsCollection := db.Collection("contracts")
	templatesCollection := db.Collection("templates")
	auditsCollection := db.Collection("audits")

	// Initialize Ethereum client
	ethClient, err := eth.NewEthClient(os.Getenv("ETH_RPC_URL"))
	if err != nil {
		log.Fatalf("Failed to connect to Ethereum node: %v", err)
	}
	log.Println("Connected to Ethereum node")

	// Initialize services
	contractService := contracts.NewService(contractsCollection, ethClient)
	auditService := audit.NewService(auditsCollection, ethClient)
	libraryService := library.NewService(templatesCollection)

	// Set up Gin router
	router := gin.Default()

	// CORS middleware
	router.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Origin, Authorization, Content-Type")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}

		c.Next()
	})

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":    "up",
			"service":   "blockchain-service",
			"timestamp": time.Now().Format(time.RFC3339),
		})
	})

	// Set up API routes
	setupRoutes(router, contractService, auditService, libraryService)

	// Start the server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Printf("Starting blockchain service on port %s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func setupRoutes(
	router *gin.Engine,
	contractService *contracts.Service,
	auditService *audit.Service,
	libraryService *library.Service,
) {
	// Contract routes
	router.POST("/contracts", contractService.CreateContract)
	router.GET("/contracts", contractService.ListContracts)
	router.GET("/contracts/:id", contractService.GetContract)
	router.PUT("/contracts/:id", contractService.UpdateContract)
	router.DELETE("/contracts/:id", contractService.DeleteContract)

	// Deployment routes
	router.POST("/deploy", contractService.DeployContract)
	router.GET("/deploy/:txHash", contractService.GetDeploymentStatus)

	// Verification routes
	router.POST("/verify", auditService.VerifyContract)
	router.POST("/audit", auditService.AuditContract)
	router.GET("/audit/:id", auditService.GetAuditResult)

	// Library routes
	router.GET("/library", libraryService.ListTemplates)
	router.GET("/library/:id", libraryService.GetTemplate)
	router.POST("/library", libraryService.CreateTemplate)
}
