from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from api.services.ai_service import AIService
from api.services.blockchain import BlockchainService
from api.core.security import get_current_user
from api.schemas.user import User
from pydantic import BaseModel

router = APIRouter()

class AuditRequest(BaseModel):
    contract_id: str
    contract_code: Optional[str] = None
    audit_type: str = "security"  # security, gas, best_practices

class AuditResponse(BaseModel):
    id: str
    status: str
    contract_id: str
    audit_type: str
    security_score: Optional[int] = None
    vulnerabilities: list = []
    suggestions: list = []

@router.post("/contract", response_model=AuditResponse)
async def audit_contract(
    audit_request: AuditRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(),
    blockchain_service: BlockchainService = Depends()
):
    """
    Audit a smart contract for security vulnerabilities
    """
    try:
        # Get contract code if not provided
        contract_code = audit_request.contract_code
        if not contract_code:
            contract = await blockchain_service.get_contract(audit_request.contract_id)
            if not contract:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Contract not found"
                )
            
            # Check if user has access to this contract
            if contract.owner_id != current_user.id and not contract.is_public:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to audit this contract"
                )
            
            contract_code = contract.contract_code
        
        # Validate contract code
        validation_result = ai_service.validate_contract(contract_code)
        
        # Create a new audit record
        audit_id = f"audit-{audit_request.contract_id}-{audit_request.audit_type}"
        
        # In a real implementation, this would store the audit in the database
        # and possibly trigger an asynchronous process for deeper analysis
        
        return {
            "id": audit_id,
            "status": "completed",
            "contract_id": audit_request.contract_id,
            "audit_type": audit_request.audit_type,
            "security_score": 85 if validation_result.is_valid else 60,
            "vulnerabilities": [
                {
                    "type": issue.get("type", "unknown"),
                    "severity": issue.get("severity", "low"),
                    "location": issue.get("location", ""),
                    "description": issue.get("description", ""),
                    "suggestion": issue.get("suggestion", "")
                }
                for issue in validation_result.issues
            ],
            "suggestions": validation_result.suggestions
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to audit contract: {str(e)}"
        )

@router.get("/{audit_id}", response_model=AuditResponse)
async def get_audit_result(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    blockchain_service: BlockchainService = Depends()
):
    """
    Get the result of a previous audit
    """
    try:
        # In a real implementation, this would retrieve the audit from the database
        # For demo purposes, we'll return a sample audit result
        
        # Extract contract_id from audit_id
        parts = audit_id.split("-")
        if len(parts) < 3 or parts[0] != "audit":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid audit ID format"
            )
        
        contract_id = parts[1]
        audit_type = parts[2] if len(parts) > 2 else "security"
        
        # Check if contract exists and user has access
        contract = await blockchain_service.get_contract(contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )
        
        if contract.owner_id != current_user.id and not contract.is_public:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this audit"
            )
        
        return {
            "id": audit_id,
            "status": "completed",
            "contract_id": contract_id,
            "audit_type": audit_type,
            "security_score": 85,
            "vulnerabilities": [
                {
                    "type": "security",
                    "severity": "medium",
                    "location": "transfer()",
                    "description": "Missing overflow check in arithmetic operation",
                    "suggestion": "Use SafeMath library or Solidity 0.8+ for automatic overflow checking"
                }
            ],
            "suggestions": [
                "Add more comprehensive event logging",
                "Consider adding a pause mechanism for emergency situations"
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit result: {str(e)}"
        )