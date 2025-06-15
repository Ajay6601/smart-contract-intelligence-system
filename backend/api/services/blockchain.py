from typing import Dict, List, Optional, Any
import httpx
from pydantic import BaseModel
from api.core.config import settings

class DeploymentResult(BaseModel):
    tx_hash: str
    contract_address: str
    cost: float
    block_number: int

class Contract(BaseModel):
    id: str
    owner_id: str
    contract_code: str
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    is_public: bool = False
    deployed_address: Optional[str] = None
    deployment_info: Optional[Dict[str, Any]] = None

class BlockchainService:
    """
    Python service that interfaces with the Go blockchain service
    via HTTP API calls.
    """

    def __init__(self):
        self.base_url = settings.BLOCKCHAIN_SERVICE_URL
        self.http_client = httpx.AsyncClient(timeout=30.0)  # Longer timeout for blockchain operations

    async def store_contract(
            self,
            owner_id: str,
            contract_code: str,
            metadata: Dict[str, Any]
    ) -> str:
        """Store a contract in the platform's database"""

        response = await self.http_client.post(
            f"{self.base_url}/contracts",
            json={
                "owner_id": owner_id,
                "contract_code": contract_code,
                "metadata": metadata
            }
        )

        response.raise_for_status()
        data = response.json()
        return data["contract_id"]

    async def get_contract(self, contract_id: str) -> Optional[Contract]:
        """Retrieve a contract by its ID"""

        response = await self.http_client.get(
            f"{self.base_url}/contracts/{contract_id}"
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        data = response.json()
        return Contract(**data)

    async def list_user_contracts(
            self,
            user_id: str,
            skip: int = 0,
            limit: int = 100
    ) -> List[Contract]:
        """List all contracts owned by a specific user"""

        response = await self.http_client.get(
            f"{self.base_url}/contracts",
            params={
                "owner_id": user_id,
                "skip": skip,
                "limit": limit
            }
        )

        response.raise_for_status()
        data = response.json()
        return [Contract(**item) for item in data["contracts"]]

    async def deploy_contract(
            self,
            contract_id: str,
            deployer_id: str
    ) -> DeploymentResult:
        """Deploy a contract to the blockchain"""

        response = await self.http_client.post(
            f"{self.base_url}/deploy",
            json={
                "contract_id": contract_id,
                "deployer_id": deployer_id
            }
        )

        response.raise_for_status()
        data = response.json()
        return DeploymentResult(**data)

    async def verify_contract(
            self,
            contract_address: str,
            contract_code: str,
            constructor_arguments: str = ""
    ) -> bool:
        """Verify a deployed contract's source code on Etherscan or similar explorer"""

        response = await self.http_client.post(
            f"{self.base_url}/verify",
            json={
                "contract_address": contract_address,
                "contract_code": contract_code,
                "constructor_arguments": constructor_arguments
            }
        )

        response.raise_for_status()
        data = response.json()
        return data["verified"]

    async def get_contract_library(
            self,
            category: Optional[str] = None,
            skip: int = 0,
            limit: int = 20
    ) -> Dict[str, Any]:
        """Get templates from the contract library"""

        params = {"skip": skip, "limit": limit}
        if category:
            params["category"] = category

        response = await self.http_client.get(
            f"{self.base_url}/library",
            params=params
        )

        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client session"""
        await self.http_client.aclose()