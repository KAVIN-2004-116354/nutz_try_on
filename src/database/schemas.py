import uuid
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ==================== User Schemas ====================

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name of user")
    email: EmailStr = Field(..., description="Unique email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="Plaintext password")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None


# ==================== Client Schemas ====================

class ClientBase(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    business_type: Optional[str] = Field(None, max_length=100)


class ClientCreate(ClientBase):
    pass


class ClientStatusUpdate(BaseModel):
    account_status: str = Field(..., pattern="^(pending|approved|suspended)$", description="Target client status")


class ClientResponse(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    account_status: str
    created_at: datetime
    updated_at: datetime


# ==================== API Key Schemas ====================

class ApiKeyCreate(BaseModel):
    name: Optional[str] = Field("Production API Key", max_length=100)
    expires_in_days: Optional[int] = Field(365, ge=1, le=1000)


class ApiKeyCreatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    key_prefix: str
    api_key: str = Field(..., description="Cryptographically secure API key. Shown once only!")
    created_at: datetime
    expires_at: Optional[datetime] = None


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    key_prefix: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None


# ==================== Tryon History Schemas ====================

class TryonHistoryCreate(BaseModel):
    garment_category: Optional[str] = None
    input_image_reference: Optional[str] = None
    output_image_reference: Optional[str] = None
    generation_status: Optional[str] = "completed"


class TryonHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    client_id: Optional[uuid.UUID] = None
    garment_category: Optional[str] = None
    input_image_reference: Optional[str] = None
    output_image_reference: Optional[str] = None
    generation_status: str
    created_at: datetime


# ==================== Usage Record Schemas ====================

class UsageRecordCreate(BaseModel):
    operation_type: str = Field(..., max_length=100)
    usage_count: int = Field(1, ge=1)


class UsageRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    client_id: Optional[uuid.UUID] = None
    operation_type: str
    usage_count: int
    created_at: datetime


# ==================== Token Schemas ====================

class TokenResponse(BaseModel):
    access_token: str
    token: str  # For backwards compatibility with frontend
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: str  # user id (UUID string)
    email: str
    role: str
    jti: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None


# ==================== Auth Flow Action Schemas ====================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10, description="Secret reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., min_length=10, description="Email verification token")


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class GenericMessageResponse(BaseModel):
    status: str = "success"
    message: str
