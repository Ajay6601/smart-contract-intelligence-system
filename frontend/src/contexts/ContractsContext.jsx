import React, { createContext, useContext, useState } from 'react';
import { useAuth } from './AuthContext';

// Create context
const ContractsContext = createContext();

// Custom hook to use the contracts context
export const useContracts = () => {
  return useContext(ContractsContext);
};

// Contracts provider component
export const ContractsProvider = ({ children }) => {
  const { currentUser } = useAuth();
  const [userContracts, setUserContracts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // API base URL
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Helper function to make authenticated API requests
  const apiRequest = async (endpoint, method = 'GET', data = null) => {
    try {
      const token = localStorage.getItem('authToken');
      
      if (!token && endpoint !== '/library') {
        throw new Error('Authentication required');
      }
      
      const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      };
      
      const config = {
        method,
        headers,
        ...(data ? { body: JSON.stringify(data) } : {})
      };
      
      const response = await fetch(`${API_URL}${endpoint}`, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API request failed with status: ${response.status}`);
      }
      
      return await response.json();
    } catch (err) {
      setError(err.message || 'An error occurred');
      throw err;
    }
  };

  // Create a new contract
  const createContract = async (contractData) => {
    setLoading(true);
    setError(null);
    
    try {
      // For demo purposes, we'll simulate API call
      return await simulateApiCall('create', contractData);
    } catch (err) {
      setError(err.message || 'Failed to create contract');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get a specific contract
  const getContract = async (contractId) => {
    setLoading(true);
    setError(null);
    
    try {
      // For demo purposes, we'll simulate API call
      return await simulateApiCall('get', { contractId });
    } catch (err) {
      setError(err.message || 'Failed to get contract');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // List user's contracts
  const listContracts = async () => {
    if (!currentUser) return [];
    
    setLoading(true);
    setError(null);
    
    try {
      // For demo purposes, we'll simulate API call
      const response = await simulateApiCall('list');
      setUserContracts(response.contracts);
      return response.contracts;
    } catch (err) {
      setError(err.message || 'Failed to list contracts');
      return [];
    } finally {
      setLoading(false);
    }
  };

  // Deploy a contract
  const deployContract = async (contractId) => {
    setLoading(true);
    setError(null);
    
    try {
      // For demo purposes, we'll simulate API call
      return await simulateApiCall('deploy', { contractId });
    } catch (err) {
      setError(err.message || 'Failed to deploy contract');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Visualize a contract
  const visualizeContract = async (visualizationData) => {
    setLoading(true);
    setError(null);
    
    try {
      // For demo purposes, we'll simulate API call
      return await simulateApiCall('visualize', visualizationData);
    } catch (err) {
      setError(err.message || 'Failed to visualize contract');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Audit a contract
  const auditContract = async (contractId) => {
    setLoading(true);
    setError(null);
    
    try {
      // For demo purposes, we'll simulate API call
      return await simulateApiCall('audit', { contractId });
    } catch (err) {
      setError(err.message || 'Failed to audit contract');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get contract templates
  const getTemplates = async (category = null) => {
    setLoading(true);
    setError(null);
    
    try {
      // For demo purposes, we'll simulate API call
      return await simulateApiCall('templates', { category });
    } catch (err) {
      setError(err.message || 'Failed to get templates');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Helper function to simulate API calls (for demo only)
  const simulateApiCall = (action, data = {}) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        switch (action) {
          case 'create':
            resolve({
              status: "success",
              contract_id: `contract-${Date.now()}`,
              code: `// SPDX-License-Identifier: MIT\npragma solidity ^0.8.17;\n\ncontract ${data.contract_type || 'CustomContract'} {\n    // Generated contract code would go here\n}`,
              suggestions: ["Consider adding more documentation", "Add events for key state changes"]
            });
            break;
            
          case 'get':
            resolve({
              id: data.contractId,
              name: "Sample Contract",
              description: "This is a sample contract for demonstration",
              owner_id: currentUser?.id || "1",
              contract_type: "token",
              contract_code: `// SPDX-License-Identifier: MIT\npragma solidity ^0.8.17;\n\ncontract SampleToken {\n    string public name = "Sample Token";\n    string public symbol = "SMPL";\n    uint8 public decimals = 18;\n    uint256 public totalSupply = 1000000 * (10 ** uint256(decimals));\n    \n    mapping(address => uint256) public balanceOf;\n    mapping(address => mapping(address => uint256)) public allowance;\n    \n    event Transfer(address indexed from, address indexed to, uint256 value);\n    event Approval(address indexed owner, address indexed spender, uint256 value);\n    \n    constructor() {\n        balanceOf[msg.sender] = totalSupply;\n    }\n    \n    function transfer(address to, uint256 value) public returns (bool) {\n        require(balanceOf[msg.sender] >= value, "Insufficient balance");\n        balanceOf[msg.sender] -= value;\n        balanceOf[to] += value;\n        emit Transfer(msg.sender, to, value);\n        return true;\n    }\n    \n    function approve(address spender, uint256 value) public returns (bool) {\n        allowance[msg.sender][spender] = value;\n        emit Approval(msg.sender, spender, value);\n        return true;\n    }\n    \n    function transferFrom(address from, address to, uint256 value) public returns (bool) {\n        require(balanceOf[from] >= value, "Insufficient balance");\n        require(allowance[from][msg.sender] >= value, "Insufficient allowance");\n        balanceOf[from] -= value;\n        balanceOf[to] += value;\n        allowance[from][msg.sender] -= value;\n        emit Transfer(from, to, value);\n        return true;\n    }\n}`,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              is_public: false,
              deployed_address: null,
              parameters: { 
                name: "Sample Token", 
                symbol: "SMPL", 
                decimals: 18,
                initialSupply: 1000000
              }
            });
            break;
            
          case 'list':
            resolve({
              contracts: [
                {
                  id: "contract-1",
                  name: "My Token",
                  description: "ERC20 token with custom features",
                  contract_type: "token",
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                  is_public: false,
                  deployed_address: null
                },
                {
                  id: "contract-2",
                  name: "NFT Collection",
                  description: "ERC721 NFT collection with minting",
                  contract_type: "nft",
                  created_at: new Date(Date.now() - 86400000).toISOString(),
                  updated_at: new Date(Date.now() - 86400000).toISOString(),
                  is_public: true,
                  deployed_address: "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
                }
              ],
              total: 2
            });
            break;
            
          case 'deploy':
            resolve({
              status: "success",
              transaction_hash: "0x" + Math.random().toString(16).substr(2, 40),
              contract_address: "0x" + Math.random().toString(16).substr(2, 40),
              deployment_cost: 0.01245
            });
            break;
            
          case 'visualize':
            resolve({
              status: "success",
              visualization_data: {
                type: data.visualization_type || "flowchart",
                nodes: [
                  {
                    id: "contract",
                    type: "contract",
                    data: {
                      label: "SampleToken",
                      description: "A basic ERC20 token implementation",
                    },
                    position: { x: 0, y: 0 }
                  },
                  {
                    id: "function_transfer",
                    type: "function",
                    data: {
                      label: "transfer",
                      visibility: "public",
                      modifiers: [],
                      parameters: [
                        { name: "to", type: "address" },
                        { name: "value", type: "uint256" }
                      ],
                      returns: [{ type: "bool" }],
                      description: "Transfers tokens to another address"
                    },
                    position: { x: 200, y: 0 }
                  }
                ],
                edges: [
                  {
                    id: "edge_contract_to_transfer",
                    source: "contract",
                    target: "function_transfer",
                    type: "function_call"
                  }
                ],
                mermaid: "flowchart TD\n    Contract[SampleToken]\n    transfer(transfer)\n    Contract --> transfer"
              },
              contract_analysis: {
                contractName: "SampleToken",
                description: "A basic ERC20 token implementation",
                main_functionality: "Token transfers and allowances",
                security_features: ["Balance checks", "Allowance validation"],
                data_flow: ["User calls transfer function", "Contract checks balance", "Contract updates balances", "Contract emits Transfer event"]
              }
            });
            break;
            
          case 'audit':
            resolve({
              id: "audit-1",
              contract_id: data.contractId,
              status: "completed",
              created_at: new Date().toISOString(),
              completed_at: new Date().toISOString(),
              security_score: 85,
              vulnerabilities: [
                {
                  id: "V1",
                  name: "Missing overflow check",
                  severity: "medium",
                  description: "The contract doesn't check for integer overflow in arithmetic operations",
                  location: "transfer()",
                  recommendation: "Use SafeMath library or Solidity 0.8+ for automatic overflow checking"
                }
              ],
              suggestions: [
                "Add more comprehensive event logging",
                "Consider adding a pause mechanism for emergency situations",
                "Implement rate limiting to prevent flash loan attacks"
              ]
            });
            break;
            
          case 'templates':
            resolve([
              {
                id: "template-1",
                name: "Standard ERC20 Token",
                description: "A fully compliant ERC20 token with optional features",
                contract_type: "token",
                category: "tokens",
                created_at: new Date().toISOString(),
                is_public: true,
                author_id: "platform",
                usage_count: 1287,
                rating: 4.8
              },
              {
                id: "template-2",
                name: "NFT Collection (ERC721)",
                description: "Create your own NFT collection with minting",
                contract_type: "nft",
                category: "collectibles",
                created_at: new Date().toISOString(),
                is_public: true,
                author_id: "platform",
                usage_count: 843,
                rating: 4.6
              }
            ]);
            break;
            
          default:
            resolve({ status: "error", message: "Unknown action" });
        }
      }, 1000); // Simulate network delay
    });
  };

  const value = {
    userContracts,
    loading,
    error,
    createContract,
    getContract,
    listContracts,
    deployContract,
    visualizeContract,
    auditContract,
    getTemplates
  };

  return (
    <ContractsContext.Provider value={value}>
      {children}
    </ContractsContext.Provider>
  );
};