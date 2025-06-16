package types

// DeploymentRequest represents a request to deploy a contract
type DeploymentRequest struct {
	ContractCode         string                 `json:"contract_code"`
	ConstructorArguments string                 `json:"constructor_arguments,omitempty"`
	ChainID              int                    `json:"chain_id"`
	GasLimit             uint64                 `json:"gas_limit"`
	Metadata             map[string]interface{} `json:"metadata,omitempty"`
}

// DeploymentResponse represents the response after deploying a contract
type DeploymentResponse struct {
	TxHash          string  `json:"tx_hash"`
	ContractAddress string  `json:"contract_address"`
	BlockNumber     int     `json:"block_number"`
	GasUsed         uint64  `json:"gas_used"`
	Cost            float64 `json:"cost"`
}