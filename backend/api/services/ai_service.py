from typing import Dict, List, Optional, Any
import openai
from pydantic import BaseModel
from api.core.config import settings

class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[Dict[str, str]] = []
    suggestions: List[str] = []

class ContractStructure(BaseModel):
    functions: List[Dict[str, Any]]
    variables: List[Dict[str, Any]]
    events: List[Dict[str, Any]]
    modifiers: List[Dict[str, Any]]
    inheritance: List[str]
    summary: Dict[str, Any]

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_contract_code(
            self,
            description: str,
            contract_type: str,
            params: Dict[str, Any]
    ) -> str:
        """
        Generate Solidity smart contract code from natural language description
        using GPT-4 or equivalent LLM.
        """
        prompt = self._build_contract_generation_prompt(
            description=description,
            contract_type=contract_type,
            params=params
        )

        response = self.client.chat.completions.create(
            model="gpt-4-turbo",  # Or the latest appropriate model
            messages=[
                {"role": "system", "content": "You are an expert Solidity developer specializing in secure, gas-efficient smart contracts. Your task is to generate production-ready smart contract code based on user requirements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Low temperature for more deterministic output
            max_tokens=3000
        )

        # Extract the Solidity code from the response
        contract_code = response.choices[0].message.content.strip()

        # Clean up the response to extract just the code (remove markdown formatting if present)
        if "```solidity" in contract_code:
            contract_code = contract_code.split("```solidity")[1].split("```")[0].strip()
        elif "```" in contract_code:
            contract_code = contract_code.split("```")[1].split("```")[0].strip()

        return contract_code

    def validate_contract(self, contract_code: str) -> ValidationResult:
        """
        Validate the generated smart contract for common security issues,
        best practices, and gas efficiency.
        """
        prompt = f"""
        Please analyze the following Solidity smart contract for:
        1. Security vulnerabilities (reentrancy, overflow/underflow, etc.)
        2. Gas optimization issues
        3. Best practice violations
        4. Logical errors or edge cases
        
        For each issue found, provide:
        - The specific line or function with the issue
        - A description of the problem
        - A suggested fix
        
        Contract code:
        ```solidity
        {contract_code}
        ```
        
        Format your response as JSON with the following structure:
        {{
            "is_valid": true/false,
            "issues": [
                {{
                    "type": "security|gas|best_practice|logical",
                    "severity": "high|medium|low",
                    "location": "function name or line number",
                    "description": "Description of the issue",
                    "suggestion": "Suggested fix"
                }}
            ],
            "suggestions": [
                "General improvement suggestion 1",
                "General improvement suggestion 2"
            ]
        }}
        """

        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert smart contract security auditor. Analyze the given Solidity contract and return a JSON response with your findings."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        try:
            import json
            result = json.loads(response.choices[0].message.content)
            return ValidationResult(**result)
        except Exception as e:
            # Fallback in case of parsing errors
            return ValidationResult(
                is_valid=False,
                issues=[{"type": "system", "severity": "high", "location": "validation",
                         "description": f"Failed to validate contract: {str(e)}",
                         "suggestion": "Please try again or contact support."}]
            )

    def analyze_contract_structure(self, contract_code: str) -> ContractStructure:
        """
        Analyze the structure of a smart contract to extract its components
        for visualization purposes.
        """
        prompt = f"""
        Please analyze the following Solidity smart contract and extract its structural components.
        Return the analysis as a JSON object with the following structure:
        
        ```json
        {{
            "functions": [
                {{
                    "name": "functionName",
                    "visibility": "public|private|internal|external",
                    "modifiers": ["modifier1", "modifier2"],
                    "parameters": [
                        {{"name": "param1", "type": "uint256"}}
                    ],
                    "returns": [
                        {{"type": "bool"}}
                    ],
                    "description": "Brief description of what this function does"
                }}
            ],
            "variables": [
                {{
                    "name": "variableName",
                    "type": "address",
                    "visibility": "public|private|internal",
                    "constant": true/false
                }}
            ],
            "events": [
                {{
                    "name": "EventName",
                    "parameters": [
                        {{"name": "param1", "type": "address", "indexed": true}}
                    ]
                }}
            ],
            "modifiers": [
                {{
                    "name": "modifierName",
                    "parameters": [
                        {{"name": "param1", "type": "uint256"}}
                    ]
                }}
            ],
            "inheritance": ["BaseContract1", "BaseContract2"],
            "summary": {{
                "contractName": "MyContract",
                "description": "A high-level description of what this contract does",
                "main_functionality": "The primary purpose of this contract",
                "security_features": ["Feature1", "Feature2"],
                "data_flow": ["Step 1: User calls function X", "Step 2: Function X updates state Y"]
            }}
        }}
        ```
        
        Contract code:
        ```solidity
        {contract_code}
        ```
        """

        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert Solidity analyzer that extracts structured information from smart contracts."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        try:
            import json
            result = json.loads(response.choices[0].message.content)
            return ContractStructure(**result)
        except Exception as e:
            # Fallback with minimal structure in case of errors
            return ContractStructure(
                functions=[],
                variables=[],
                events=[],
                modifiers=[],
                inheritance=[],
                summary={
                    "contractName": "Unknown",
                    "description": f"Error analyzing contract: {str(e)}",
                    "main_functionality": "Unknown",
                    "security_features": [],
                    "data_flow": []
                }
            )

    def _build_contract_generation_prompt(
            self,
            description: str,
            contract_type: str,
            params: Dict[str, Any]
    ) -> str:
        """
        Build a detailed prompt for contract generation based on user input
        """
        # Template selection based on contract type
        contract_templates = {
            "token": "ERC20 token contract with customizable features",
            "nft": "ERC721 NFT contract with minting and royalties",
            "dao": "Decentralized Autonomous Organization with voting",
            "marketplace": "Marketplace for buying and selling digital assets",
            "escrow": "Escrow service for secure transactions",
            "staking": "Staking contract with rewards distribution",
            "multisig": "Multi-signature wallet",
            # Add more templates as needed
        }

        template_desc = contract_templates.get(
            contract_type,
            "Custom smart contract based on description"
        )

        # Convert parameters to a formatted string
        params_str = "\n".join([f"- {k}: {v}" for k, v in params.items()])

        prompt = f"""
        Generate a secure, gas-efficient, and well-documented Solidity smart contract based on the following requirements:
        
        CONTRACT TYPE: {contract_type}
        TEMPLATE: {template_desc}
        
        DESCRIPTION:
        {description}
        
        PARAMETERS:
        {params_str}
        
        Requirements:
        1. Use the latest stable Solidity version
        2. Follow best security practices and include protection against common vulnerabilities
        3. Optimize for gas efficiency
        4. Include comprehensive NatSpec documentation
        5. Implement appropriate access control mechanisms
        6. Add thorough error handling with custom error messages
        7. Include events for all significant state changes
        
        Return only the Solidity code without any additional explanation.
        """

        return prompt