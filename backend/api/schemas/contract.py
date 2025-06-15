from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class ContractCreate(BaseModel):
    description: str
    contract_type: str
    parameters: Dict[str, Any]

class ContractResponse(BaseModel):
    status: str
    contract_id: Optional[str] = None
    code: Optional[str] = None
    issues: Optional[List[Dict[str, str]]] = None
    suggestions: Optional[List[str]] = None
    message: Optional[str] = None
    draft_code: Optional[str] = None

class ContractList(BaseModel):
    contracts: List[Dict[str, Any]]
    total: int

class ContractVisualizeRequest(BaseModel):
    contract_code: str
    visualization_type: str = "flowchart"  # flowchart, sequence, interaction

class VisualizationResponse(BaseModel):
    status: str
    visualization_data: Dict[str, Any]
    contract_analysis: Dict[str, Any]