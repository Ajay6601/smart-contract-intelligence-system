from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from datetime import timedelta
from api.schemas.user import UserCreate, User, Token, UserLogin
from api.core.security import get_password_hash, verify_password, create_access_token, get_current_user
from api.core.config import settings
from pydantic import BaseModel

router = APIRouter()

# Simulated user database for demonstration
# In a real implementation, this would use a proper database
USERS_DB = {}

class UserDB(BaseModel):
    id: str
    email: str
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    wallet_address: Optional[str] = None
    is_active: bool = True

@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate):
    """
    Register a new user
    """
    # Check if email is already registered
    if any(u.email == user_data.email for u in USERS_DB.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username is already taken
    if any(u.username == user_data.username for u in USERS_DB.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user ID
    user_id = f"user_{len(USERS_DB) + 1}"
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user in database
    user = UserDB(
        id=user_id,
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    USERS_DB[user_id] = user
    
    # Return user data (without password)
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "wallet_address": user.wallet_address
    }

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = None
    
    # Find user by email (in a real app, this would be a database query)
    for u in USERS_DB.values():
        if u.email == form_data.username:
            user = u
            break
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """
    Login endpoint for email/password authentication
    """
    user = None
    
    # Find user by email
    for u in USERS_DB.values():
        if u.email == login_data.email:
            user = u
            break
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user

@router.post("/wallet", response_model=User)
async def connect_wallet(
    wallet_address: str,
    current_user: User = Depends(get_current_user)
):
    """
    Connect a wallet address to user account
    """
    # In a real implementation, this would update the user in the database
    user_id = current_user.id
    if user_id in USERS_DB:
        USERS_DB[user_id].wallet_address = wallet_address
        
        # Return updated user
        user = USERS_DB[user_id]
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "wallet_address": user.wallet_address
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )