package contracts

import (
	"context"
	"encoding/json"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"

	"github.com/yourusername/smart-contract-intelligence/internal/eth"
	"github.com/yourusername/smart-contract-intelligence/pkg/types"
)

// Contract represents a smart contract in the system
type Contract struct {
	ID              string                 `bson:"_id" json:"id"`
	OwnerID         string                 `bson:"owner_id" json:"owner_id"`
	ContractCode    string                 `bson:"contract_code" json:"contract_code"`
	Metadata        map[string]interface{} `bson:"metadata" json:"metadata"`
	CreatedAt       time.Time              `bson:"created_at" json:"created_at"`
	UpdatedAt       time.Time              `bson:"updated_at" json:"updated_at"`
	IsPublic        bool                   `bson:"is_public" json:"is_public"`
	DeployedAddress string                 `bson:"deployed_address,omitempty" json:"deployed_address,omitempty"`
	DeploymentInfo  map[string]interface{} `bson:"deployment_info,omitempty" json:"deployment_info,omitempty"`
}

// DeploymentRequest represents a request to deploy a contract
type DeploymentRequest struct {
	ContractID  string `json:"contract_id"`
	DeployerID  string `json:"deployer_id"`
	ChainID     int    `json:"chain_id,omitempty"`
	GasLimit    uint64 `json:"gas_limit,omitempty"`
	Constructor string `json:"constructor_arguments,omitempty"`
}

// DeploymentResponse represents the response from a deployment request
type DeploymentResponse struct {
	TxHash         string  `json:"tx_hash"`
	ContractAddress string `json:"contract_address"`
	Cost           float64 `json:"cost"`
	BlockNumber    int     `json:"block_number"`
}

// Service handles contract operations
type Service struct {
	contracts *mongo.Collection
	ethClient *eth.Client
}

// NewService creates a new contract service
func NewService(contracts *mongo.Collection, ethClient *eth.Client) *Service {
	return &Service{
		contracts: contracts,
		ethClient: ethClient,
	}
}

// CreateContract handles the creation of a new smart contract
func (s *Service) CreateContract(c *gin.Context) {
	var contract Contract
	if err := c.ShouldBindJSON(&contract); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Generate UUID for the contract
	contract.ID = uuid.New().String()
	contract.CreatedAt = time.Now()
	contract.UpdatedAt = time.Now()

	// Insert the contract into the database
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_, err := s.contracts.InsertOne(ctx, contract)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create contract"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"contract_id": contract.ID,
		"message": "Contract created successfully",
	})
}

// GetContract retrieves a contract by ID
func (s *Service) GetContract(c *gin.Context) {
	id := c.Param("id")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var contract Contract
	err := s.contracts.FindOne(ctx, bson.M{"_id": id}).Decode(&contract)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			c.JSON(http.StatusNotFound, gin.H{"error": "Contract not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve contract"})
		return
	}

	c.JSON(http.StatusOK, contract)
}

// ListContracts lists contracts with filtering options
func (s *Service) ListContracts(c *gin.Context) {
	ownerID := c.Query("owner_id")
	isPublic := c.Query("is_public") == "true"
	
	skip := 0
	if skipParam := c.Query("skip"); skipParam != "" {
		if val, err := primitive.ParseInt32(skipParam); err == nil {
			skip = int(val)
		}
	}

	limit := 100
	if limitParam := c.Query("limit"); limitParam != "" {
		if val, err := primitive.ParseInt32(limitParam); err == nil && val > 0 {
			limit = int(val)
		}
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Build the filter
	filter := bson.M{}
	if ownerID != "" {
		filter["owner_id"] = ownerID
	}
	if c.Query("is_public") != "" {
		filter["is_public"] = isPublic
	}

	// Set up options
	findOptions := options.Find()
	findOptions.SetSkip(int64(skip))
	findOptions.SetLimit(int64(limit))
	findOptions.SetSort(bson.M{"created_at": -1}) // Sort by creation time, newest first

	// Execute the query
	cursor, err := s.contracts.Find(ctx, filter, findOptions)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list contracts"})
		return
	}
	defer cursor.Close(ctx)

	// Decode the results
	var contracts []Contract
	if err := cursor.All(ctx, &contracts); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode contracts"})
		return
	}

	// Get total count for pagination
	count, err := s.contracts.CountDocuments(ctx, filter)
	if err != nil {
		count = int64(len(contracts)) // Fallback to length of results if count fails
	}

	c.JSON(http.StatusOK, gin.H{
		"contracts": contracts,
		"total": count,
		"skip": skip,
		"limit": limit,
	})
}

// UpdateContract updates an existing contract
func (s *Service) UpdateContract(c *gin.Context) {
	id := c.Param("id")

	var updates map[string]interface{}
	if err := c.ShouldBindJSON(&updates); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Check if the contract exists and user has permission
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var existingContract Contract
	err := s.contracts.FindOne(ctx, bson.M{"_id": id}).Decode(&existingContract)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			c.JSON(http.StatusNotFound, gin.H{"error": "Contract not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve contract"})
		return
	}

	// Verify ownership (in a real app, this would use authentication middleware)
	requestUserID := c.GetHeader("X-User-ID") // Simplified; use proper auth in production
	if existingContract.OwnerID != requestUserID {
		c.JSON(http.StatusForbidden, gin.H{"error": "You don't have permission to update this contract"})
		return
	}

	// Prevent updating critical fields
	delete(updates, "_id")
	delete(updates, "owner_id")
	delete(updates, "created_at")
	
	// Always update the updated_at timestamp
	updates["updated_at"] = time.Now()

	// Perform the update
	updateResult, err := s.contracts.UpdateOne(
		ctx,
		bson.M{"_id": id},
		bson.M{"$set": updates},
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update contract"})
		return
	}

	if updateResult.MatchedCount == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Contract not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Contract updated successfully",
		"modified_count": updateResult.ModifiedCount,
	})
}

// DeleteContract deletes a contract
func (s *Service) DeleteContract(c *gin.Context) {
	id := c.Param("id")

	// Check if the contract exists and user has permission
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var existingContract Contract
	err := s.contracts.FindOne(ctx, bson.M{"_id": id}).Decode(&existingContract)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			c.JSON(http.StatusNotFound, gin.H{"error": "Contract not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve contract"})
		return
	}

	// Verify ownership (in a real app, this would use authentication middleware)
	requestUserID := c.GetHeader("X-User-ID") // Simplified; use proper auth in production
	if existingContract.OwnerID != requestUserID {
		c.JSON(http.StatusForbidden, gin.H{"error": "You don't have permission to delete this contract"})
		return
	}

	// Perform the delete
	deleteResult, err := s.contracts.DeleteOne(ctx, bson.M{"_id": id})
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete contract"})
		return
	}

	if deleteResult.DeletedCount == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Contract not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Contract deleted successfully",
	})
}

// DeployContract deploys a smart contract to the blockchain
func (s *Service) DeployContract(c *gin.Context) {
	var req DeploymentRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Retrieve the contract from the database
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var contract Contract
	err := s.contracts.FindOne(ctx, bson.M{"_id": req.ContractID}).Decode(&contract)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			c.JSON(http.StatusNotFound, gin.H{"error": "Contract not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve contract"})
		return
	}

	// Verify ownership
	if contract.OwnerID != req.DeployerID {
		c.JSON(http.StatusForbidden, gin.H{"error": "You don't have permission to deploy this contract"})
		return
	}

	// Prepare deployment parameters
	chainID := req.ChainID
	if chainID == 0 {
		// Default to Ethereum mainnet
		chainID = 1
	}

	gasLimit := req.GasLimit
	if gasLimit == 0 {
		// Default gas limit
		gasLimit = 4000000
	}

	// Deploy the contract
	deployCtx, deployCancel := context.WithTimeout(context.Background(), 2*time.Minute) // Longer timeout for deployment
	defer deployCancel()

	deployResult, err := s.ethClient.DeployContract(deployCtx, &types.DeploymentRequest{
		ContractCode:          contract.ContractCode,
		ConstructorArguments:  req.Constructor,
		ChainID:               chainID,
		GasLimit:              gasLimit,
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to deploy contract",
			"details": err.Error(),
		})
		return
	}

	// Update the contract in the database with deployment information
	deploymentInfo := map[string]interface{}{
		"tx_hash":         deployResult.TxHash,
		"contract_address": deployResult.ContractAddress,
		"block_number":    deployResult.BlockNumber,
		"chain_id":        chainID,
		"deployer_id":     req.DeployerID,
		"deployed_at":     time.Now(),
		"gas_used":        deployResult.GasUsed,
		"gas_price":       deployResult.GasPrice,
	}

	updateResult, err := s.contracts.UpdateOne(
		ctx,
		bson.M{"_id": req.ContractID},
		bson.M{
			"$set": bson.M{
				"deployed_address": deployResult.ContractAddress,
				"deployment_info":  deploymentInfo,
				"updated_at":       time.Now(),
			},
		},
	)

	if err != nil || updateResult.ModifiedCount == 0 {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Contract deployed but failed to update database",
			"deployment": deploymentInfo,
		})
		return
	}

	c.JSON(http.StatusOK, DeploymentResponse{
		TxHash:         deployResult.TxHash,
		ContractAddress: deployResult.ContractAddress,
		Cost:           deployResult.Cost,
		BlockNumber:    deployResult.BlockNumber,
	})
}

// GetDeploymentStatus checks the status of a deployment transaction
func (s *Service) GetDeploymentStatus(c *gin.Context) {
	txHash := c.Param("txHash")
	if txHash == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Transaction hash is required"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	status, err := s.ethClient.GetTransactionStatus(ctx, txHash)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to get transaction status",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, status)
}