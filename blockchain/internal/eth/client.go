package eth

import (
	"context"
	"crypto/ecdsa"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"math/big"
	"os"
	"strings"
	"bytes"
	
	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/common/hexutil"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
	solc "github.com/ethereum/go-ethereum/common/compiler"
	
	"github.com/yourusername/smart-contract-intelligence/pkg/types"
)

// Client represents an Ethereum client
type Client struct {
	client  *ethclient.Client
	chainID *big.Int
}

// DeploymentResult represents the result of a contract deployment
type DeploymentResult struct {
	TxHash         string
	ContractAddress string
	BlockNumber    int
	GasUsed        uint64
	GasPrice       *big.Int
	Cost           float64
}

// TransactionStatus represents the status of a transaction
type TransactionStatus struct {
	Status      string  `json:"status"`       // "pending", "success", "failed"
	BlockNumber uint64  `json:"block_number"` // Block number if mined
	Confirmations uint64 `json:"confirmations"` // Number of confirmations
	GasUsed     uint64  `json:"gas_used"`     // Gas used if mined
	Cost        float64 `json:"cost"`         // Cost in ETH
}

// NewEthClient creates a new Ethereum client
func NewEthClient(rpcURL string) (*Client, error) {
	if rpcURL == "" {
		return nil, errors.New("Ethereum RPC URL is required")
	}

	client, err := ethclient.Dial(rpcURL)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to Ethereum client: %v", err)
	}

	// Get the chain ID
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	
	chainID, err := client.ChainID(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get chain ID: %v", err)
	}

	return &Client{
		client:  client,
		chainID: chainID,
	}, nil
}

// GetPrivateKey retrieves a private key from environment or keystore
func (c *Client) GetPrivateKey() (*ecdsa.PrivateKey, error) {
	// For production, use a secure key management system
	// This is a simplified example that uses an environment variable
	privateKeyHex := os.Getenv("ETH_PRIVATE_KEY")
	if privateKeyHex == "" {
		return nil, errors.New("ETH_PRIVATE_KEY environment variable not set")
	}

	// Remove 0x prefix if present
	if strings.HasPrefix(privateKeyHex, "0x") {
		privateKeyHex = privateKeyHex[2:]
	}

	privateKey, err := crypto.HexToECDSA(privateKeyHex)
	if err != nil {
		return nil, fmt.Errorf("invalid private key: %v", err)
	}

	return privateKey, nil
}

// DeployContract deploys a smart contract to the blockchain
func (c *Client) DeployContract(ctx context.Context, req *types.DeploymentRequest) (*DeploymentResult, error) {
	// Compile the Solidity code
	contracts, err := c.CompileContract(req.ContractCode)
	if err != nil {
		return nil, fmt.Errorf("compilation failed: %v", err)
	}

	if len(contracts) == 0 {
		return nil, errors.New("no contracts found in source code")
	}

	// Find the main contract (usually the last one or the one with matching name)
	var contractName string
	var compiledContract *solc.Contract

	// Try to extract contract name from metadata if available
	if req.Metadata != nil {
		if name, ok := req.Metadata["contractName"].(string); ok {
			contractName = name
		}
	}

	// If we have a contract name, use it to find the contract
	if contractName != "" {
		for name, contract := range contracts {
			if strings.Contains(name, contractName) {
				contractName = name
				compiledContract = contract
				break
			}
		}
	}

	// If we don't have a match by name, just use the first contract
	if compiledContract == nil {
		for name, contract := range contracts {
			contractName = name
			compiledContract = contract
			break
		}
	}

	// Get the contract ABI and bytecode
	contractAbi, err := json.Marshal(compiledContract.Info.AbiDefinition)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal ABI: %v", err)
	}

	parsedAbi, err := abi.JSON(strings.NewReader(string(contractAbi)))
	if err != nil {
		return nil, fmt.Errorf("failed to parse ABI: %v", err)
	}

	bytecode := common.FromHex(compiledContract.Code)
	if len(bytecode) == 0 {
		return nil, errors.New("empty bytecode")
	}

	// Get the private key for transaction signing
	privateKey, err := c.GetPrivateKey()
	if err != nil {
		return nil, fmt.Errorf("failed to get private key: %v", err)
	}

	// Create a new transaction signer
	chainID := big.NewInt(int64(req.ChainID))
	if chainID.Cmp(big.NewInt(0)) == 0 {
		chainID = c.chainID // Use the client's chain ID if not specified
	}

	// Get the deployer's address
	publicKey := privateKey.Public()
	publicKeyECDSA, ok := publicKey.(*ecdsa.PublicKey)
	if !ok {
		return nil, errors.New("error casting public key to ECDSA")
	}
	fromAddress := crypto.PubkeyToAddress(*publicKeyECDSA)

	// Get the nonce for the sender's account
	nonce, err := c.client.PendingNonceAt(ctx, fromAddress)
	if err != nil {
		return nil, fmt.Errorf("failed to get nonce: %v", err)
	}

	// Get gas price
	gasPrice, err := c.client.SuggestGasPrice(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to suggest gas price: %v", err)
	}

	// Set up the transaction options
	auth, err := bind.NewKeyedTransactorWithChainID(privateKey, chainID)
	if err != nil {
		return nil, fmt.Errorf("failed to create transactor: %v", err)
	}
	auth.Nonce = big.NewInt(int64(nonce))
	auth.Value = big.NewInt(0)     // No ether transfer
	auth.GasLimit = req.GasLimit   // Gas limit
	auth.GasPrice = gasPrice       // Gas price

	// Process constructor arguments if provided
	var constructorArgs []interface{}
	if req.ConstructorArguments != "" {
		// This is a simplified approach - in a real application you would need
		// to parse the arguments based on the constructor's parameter types
		if err := json.Unmarshal([]byte(req.ConstructorArguments), &constructorArgs); err != nil {
			return nil, fmt.Errorf("failed to parse constructor arguments: %v", err)
		}
	}

	// Encode the constructor arguments with the contract bytecode
	var data []byte
	var encodingErr error
	
	if len(constructorArgs) > 0 {
		data, encodingErr = parsedAbi.Pack("", constructorArgs...)
		if encodingErr != nil {
			return nil, fmt.Errorf("failed to encode constructor arguments: %v", encodingErr)
		}
		data = append(bytecode, data...)
	} else {
		data = bytecode
	}

	// Create the transaction
	tx := types.NewContractCreation(nonce, big.NewInt(0), auth.GasLimit, gasPrice, data)
	
	// Sign the transaction
	signedTx, err := types.SignTx(tx, types.NewEIP155Signer(chainID), privateKey)
	if err != nil {
		return nil, fmt.Errorf("failed to sign transaction: %v", err)
	}

	// Send the transaction
	err = c.client.SendTransaction(ctx, signedTx)
	if err != nil {
		return nil, fmt.Errorf("failed to send transaction: %v", err)
	}

	// Wait for the transaction receipt
	receipt, err := bind.WaitMined(ctx, c.client, signedTx)
	if err != nil {
		// If we timeout waiting for the receipt, return the tx hash anyway
		// so the status can be checked later
		log.Printf("Warning: Timeout waiting for transaction receipt: %v", err)
		return &DeploymentResult{
			TxHash: signedTx.Hash().Hex(),
		}, nil
	}

	// Calculate the cost in ETH
	gasUsed := receipt.GasUsed
	gasCost := new(big.Float).Mul(
		new(big.Float).SetInt(gasPrice),
		new(big.Float).SetUint64(gasUsed),
	)
	
	// Convert from wei to ETH
	weiPerEth := new(big.Float).SetInt(big.NewInt(1e18))
	costInEth := new(big.Float).Quo(gasCost, weiPerEth)
	
	ethCost, _ := costInEth.Float64()

	return &DeploymentResult{
		TxHash:         signedTx.Hash().Hex(),
		ContractAddress: receipt.ContractAddress.Hex(),
		BlockNumber:    int(receipt.BlockNumber.Int64()),
		GasUsed:        receipt.GasUsed,
		GasPrice:       gasPrice,
		Cost:           ethCost,
	}, nil
}

// CompileContract compiles a Solidity contract
func (c *Client) CompileContract(sourceCode string) (map[string]*solc.Contract, error) {
	// Write the source code to a temporary file
	tmpFile, err := os.CreateTemp("", "solidity-*.sol")
	if err != nil {
		return nil, fmt.Errorf("failed to create temporary file: %v", err)
	}
	defer os.Remove(tmpFile.Name())

	if _, err := tmpFile.WriteString(sourceCode); err != nil {
		return nil, fmt.Errorf("failed to write to temporary file: %v", err)
	}
	
	if err := tmpFile.Close(); err != nil {
		return nil, fmt.Errorf("failed to close temporary file: %v", err)
	}

	// Compile the contract
	contracts, err := solc.CompileSolidity("solc", tmpFile.Name())
	if err != nil {
		return nil, fmt.Errorf("compilation failed: %v", err)
	}

	return contracts, nil
}

// GetTransactionStatus checks the status of a transaction
func (c *Client) GetTransactionStatus(ctx context.Context, txHash string) (*TransactionStatus, error) {
	hash := common.HexToHash(txHash)

	// Try to get transaction receipt
	receipt, err := c.client.TransactionReceipt(ctx, hash)
	if err != nil {
		if err == ethereum.NotFound {
			// Transaction is still pending
			return &TransactionStatus{
				Status:       "pending",
				Confirmations: 0,
			}, nil
		}
		return nil, fmt.Errorf("failed to get transaction receipt: %v", err)
	}

	// Get the current block number to calculate confirmations
	header, err := c.client.HeaderByNumber(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to get current block header: %v", err)
	}

	// Calculate confirmations
	confirmations := header.Number.Uint64() - receipt.BlockNumber.Uint64()

	// Get the transaction to calculate cost
	tx, _, err := c.client.TransactionByHash(ctx, hash)
	if err != nil {
		return nil, fmt.Errorf("failed to get transaction: %v", err)
	}

	// Calculate the transaction cost
	gasPrice := tx.GasPrice()
	gasUsed := receipt.GasUsed
	gasCost := new(big.Float).Mul(
		new(big.Float).SetInt(gasPrice),
		new(big.Float).SetUint64(gasUsed),
	)
	
	// Convert from wei to ETH
	weiPerEth := new(big.Float).SetInt(big.NewInt(1e18))
	costInEth := new(big.Float).Quo(gasCost, weiPerEth)
	
	ethCost, _ := costInEth.Float64()

	// Determine status
	status := "failed"
	if receipt.Status == 1 {
		status = "success"
	}

	return &TransactionStatus{
		Status:       status,
		BlockNumber:  receipt.BlockNumber.Uint64(),
		Confirmations: confirmations,
		GasUsed:      receipt.GasUsed,
		Cost:         ethCost,
	}, nil
}

// EstimateDeploymentCost estimates the cost of deploying a contract
func (c *Client) EstimateDeploymentCost(ctx context.Context, contractCode string) (float64, error) {
	// Compile the contract
	contracts, err := c.CompileContract(contractCode)
	if err != nil {
		return 0, fmt.Errorf("compilation failed: %v", err)
	}

	if len(contracts) == 0 {
		return 0, errors.New("no contracts found in source code")
	}

	// Get the compiled contract bytecode (use the first contract)
	var bytecode []byte
	for _, contract := range contracts {
		bytecode = common.FromHex(contract.Code)
		break
	}

	// Get the sender's address (we need an address for the estimation)
	privateKey, err := c.GetPrivateKey()
	if err != nil {
		return 0, fmt.Errorf("failed to get private key: %v", err)
	}
	
	publicKey := privateKey.Public()
	publicKeyECDSA, ok := publicKey.(*ecdsa.PublicKey)
	if !ok {
		return 0, errors.New("error casting public key to ECDSA")
	}
	fromAddress := crypto.PubkeyToAddress(*publicKeyECDSA)

	// Estimate gas
	gasLimit, err := c.client.EstimateGas(ctx, ethereum.CallMsg{
		From: fromAddress,
		Data: bytecode,
	})
	if err != nil {
		return 0, fmt.Errorf("failed to estimate gas: %v", err)
	}

	// Get current gas price
	gasPrice, err := c.client.SuggestGasPrice(ctx)
	if err != nil {
		return 0, fmt.Errorf("failed to get gas price: %v", err)
	}

	// Calculate total cost
	gasCost := new(big.Float).Mul(
		new(big.Float).SetInt(gasPrice),
		new(big.Float).SetUint64(gasLimit),
	)
	
	// Convert from wei to ETH
	weiPerEth := new(big.Float).SetInt(big.NewInt(1e18))
	costInEth := new(big.Float).Quo(gasCost, weiPerEth)
	
	ethCost, _ := costInEth.Float64()
	
	return ethCost, nil
}

// VerifyContractSource verifies a deployed contract's source code
func (c *Client) VerifyContractSource(
	ctx context.Context,
	contractAddress string,
	sourceCode string,
	constructorArgs string,
) (bool, error) {
	// This is a simplified implementation
	// In a production environment, you would interact with Etherscan API
	// or another block explorer's API to verify the contract

	// Compile the provided source code
	contracts, err := c.CompileContract(sourceCode)
	if err != nil {
		return false, fmt.Errorf("compilation failed: %v", err)
	}

	// Get the bytecode of the deployed contract
	address := common.HexToAddress(contractAddress)
	deployedBytecode, err := c.client.CodeAt(ctx, address, nil)
	if err != nil {
		return false, fmt.Errorf("failed to get deployed bytecode: %v", err)
	}

	// Compare bytecodes (with some simplifications)
	// Note: In reality, this comparison is more complex due to constructor arguments,
	// optimizations, and metadata differences
	for _, contract := range contracts {
		compiledBytecode := common.FromHex(contract.Code)
		
		// This is a simplified comparison
		// In a real implementation, you would need to handle constructor arguments,
		// compiler metadata, and other differences
		if len(deployedBytecode) > 0 && bytes.HasPrefix(deployedBytecode, compiledBytecode) {
			return true, nil
		}
	}

	return false, nil
}

// InteractWithContract interacts with a deployed contract
func (c *Client) InteractWithContract(
	ctx context.Context,
	contractAddress string,
	abiJSON string,
	methodName string,
	params []interface{},
) (string, error) {
	// Parse the ABI
	parsedABI, err := abi.JSON(strings.NewReader(abiJSON))
	if err != nil {
		return "", fmt.Errorf("failed to parse ABI: %v", err)
	}

	// Encode the function call
	data, err := parsedABI.Pack(methodName, params...)
	if err != nil {
		return "", fmt.Errorf("failed to encode function call: %v", err)
	}

	// Create the call message
	msg := ethereum.CallMsg{
		To:   &common.HexToAddress(contractAddress),
		Data: data,
	}

	// Execute the call
	result, err := c.client.CallContract(ctx, msg, nil)
	if err != nil {
		return "", fmt.Errorf("contract call failed: %v", err)
	}

	// Return the raw result
	return hexutil.Encode(result), nil
}