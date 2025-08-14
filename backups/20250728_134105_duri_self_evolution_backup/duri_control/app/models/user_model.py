from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserInDB(BaseModel):
    id: int
    username: str
    password_hash: str
    role: UserRole
    is_active: bool = True
    created_at: datetime

class UserCreate(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="secret")
    role: UserRole = UserRole.USER

class UserLogin(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="secret")

class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    exp: int
    type: str = "access"

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int 