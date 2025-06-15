from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from api.schemas.contract import (
    ContractCreate,
    ContractResponse,
    ContractList,
    ContractVisualizeRequest,
    VisualizationResponse
)
from api.services.ai_service import AIService
from api.services.blockchain import BlockchainService
from api.services.visualization import VisualizationService
from api.core.security import get_current_user
from api.schemas.user import User

router = APIRouter()

@router.post("/create", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
        contract_request: ContractCreate,
        current_user: User = Depends(get_current_user),
        ai_service: AIService = Depends(),
        blockchain_service: BlockchainService = Depends()
):
    """
    Create a new smart contract from natural language description
    """
    try:
        # Generate smart contract code using AI
        contract_code = ai_service.generate_contract_code(
            description=contract_request.description,
            contract_type=contract_request.contract_type,
            params=contract_request.parameters
        )

        # Validate the generated contract
        validation_result = ai_service.validate_contract(contract_code)
        if not validation_result.is_valid:
            return {
                "status": "error",
                "message": "Generated contract has issues",
                "issues": validation_result.issues,
                "draft_code": contract_code
            }

        # Store contract in blockchain service
        contract_id = await blockchain_service.store_contract(
            owner_id=current_user.id,
            contract_code=contract_code,
            metadata={
                "description": contract_request.description,
                "type": contract_request.contract_type,
                "parameters": contract_request.parameters
            }
        )

        return {
            "status": "success",
            "contract_id": contract_id,
            "code": contract_code,
            "suggestions": validation_result.suggestions
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create contract: {str(e)}"
        )

@router.get("/list", response_model=ContractList)
async def list_contracts(
        current_user: User = Depends(get_current_user),
        blockchain_service: BlockchainService = Depends(),
        skip: int = 0,
        limit: int = 100
):
    """
    List all contracts owned by the current user
    """
    contracts = await blockchain_service.list_user_contracts(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return {"contracts": contracts, "total": len(contracts)}

@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
        contract_id: str,
        current_user: User = Depends(get_current_user),
        blockchain_service: BlockchainService = Depends()
):
    """
    Get a specific contract by ID
    """
    contract = await blockchain_service.get_contract(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check if user has access to this contract
    if contract.owner_id != current_user.id and not contract.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this contract"
        )

    return contract

@router.post("/visualize", response_model=VisualizationResponse)
async def visualize_contract(
        visualization_request: ContractVisualizeRequest,
        visualization_service: VisualizationService = Depends(),
        ai_service: AIService = Depends()
):
    """
    Generate a visual representation of a smart contract
    """
    # Parse the contract to understand its structure
    contract_structure = ai_service.analyze_contract_structure(
        visualization_request.contract_code
    )

    # Generate visualization
    visualization = visualization_service.generate_visualization(
        contract_structure=contract_structure,
        visualization_type=visualization_request.visualization_type
    )

    return {
        "status": "success",
        "visualization_data": visualization,
        "contract_analysis": contract_structure.summary
    }

@router.post("/deploy/{contract_id}")
async def deploy_contract(
        contract_id: str,
        current_user: User = Depends(get_current_user),
        blockchain_service: BlockchainService = Depends()
):
    """
    Deploy a contract to the blockchain
    """
    # Check if contract exists and user has access
    contract = await blockchain_service.get_contract(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to deploy this contract"
        )

    # Deploy the contract
    try:
        deployment_result = await blockchain_service.deploy_contract(
            contract_id=contract_id,
            deployer_id=current_user.id
        )

        return {
            "status": "success",
            "transaction_hash": deployment_result.tx_hash,
            "contract_address": deployment_result.contract_address,
            "deployment_cost": deployment_result.cost
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Contract deployment failed: {str(e)}"
        )