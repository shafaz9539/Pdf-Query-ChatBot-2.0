from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    """
    Model for creating a new user.
    """
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """Model for receiving user credentials during login."""
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserPublic(BaseModel):
    id: str
    email: EmailStr
    full_name: str

class AuthResponse(BaseModel):
    message: str
    user: UserPublic
    access_token: str
    token_type: str = "bearer"


class UserSignupProjection(BaseModel):
    _id: str