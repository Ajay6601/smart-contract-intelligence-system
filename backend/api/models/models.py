from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId


# Custom ObjectId field for MongoDB compatibility
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# Base model with ObjectId support
class MongoBaseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


# User Models
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserDB(MongoBaseModel, UserBase):
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    wallet_address: Optional[str] = None


class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    wallet_address: Optional[str] = None


# Contract Models
class ContractBase(BaseModel):
    name: str
    description: str
    contract_type: str
    is_public: bool = False


class ContractCreate(ContractBase):
    owner_id: str
    contract_code: str
    parameters: Dict[str, Any] = {}


class ContractDB(MongoBaseModel, ContractBase):
    owner_id: str
    contract_code: str
    parameters: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deployed_address: Optional[str] = None
    deployment_info: Optional[Dict[str, Any]] = None
    version: int = 1
    audit_results: Optional[Dict[str, Any]] = None


class Contract(ContractBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    deployed_address: Optional[str] = None
    version: int
    parameters: Dict[str, Any] = {}


class ContractDetail(Contract):
    contract_code: str
    deployment_info: Optional[Dict[str, Any]] = None
    audit_results: Optional[Dict[str, Any]] = None


# Template Models
class TemplateBase(BaseModel):
    name: str
    description: str
    contract_type: str
    category: str
    is_public: bool = True


class TemplateCreate(TemplateBase):
    contract_code: str
    default_parameters: Dict[str, Any] = {}
    author_id: str


class TemplateDB(MongoBaseModel, TemplateBase):
    contract_code: str
    default_parameters: Dict[str, Any] = {}
    author_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    usage_count: int = 0
    rating: float = 0.0
    ratings_count: int = 0


class Template(TemplateBase):
    id: str
    author_id: str
    created_at: datetime
    usage_count: int
    rating: float


class TemplateDetail(Template):
    contract_code: str
    default_parameters: Dict[str, Any] = {}


# Audit Models
class AuditCreate(BaseModel):
    contract_id: str
    contract_code: str
    audit_type: str = "security" # security, gas, best_practices


class AuditDB(MongoBaseModel):
    contract_id: str
    audit_type: str
    status: str = "pending" # pending, completed, failed
    results: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    vulnerabilities: List[Dict[str, Any]] = []
    suggestions: List[str] = []
    security_score: Optional[int] = None


class AuditResult(BaseModel):
    id: str
    contract_id: str
    audit_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    vulnerabilities: List[Dict[str, Any]] = []
    suggestions: List[str] = []
    security_score: Optional[int] = None


# Deployment Models
class DeploymentCreate(BaseModel):
    contract_id: str
    deployer_id: str
    chain_id: int = 1  # Default to Ethereum mainnet
    constructor_arguments: Optional[str] = None
    gas_limit: Optional[int] = None


class DeploymentDB(MongoBaseModel):
    contract_id: str
    deployer_id: str
    chain_id: int
    status: str = "pending"  # pending, completed, failed
    tx_hash: Optional[str] = None
    contract_address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    gas_used: Optional[int] = None
    gas_price: Optional[str] = None
    cost: Optional[float] = None
    error_message: Optional[str] = None


class DeploymentResult(BaseModel):
    id: str
    contract_id: str
    status: str
    tx_hash: Optional[str] = None
    contract_address: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    gas_used: Optional[int] = None
    cost: Optional[float] = None
    chain_id: int