from beanie import Document, Link
from pydantic import EmailStr, Field
from datetime import datetime

class User(Document):
    """
    User model representing a user in the system.
    """

    email: EmailStr = Field(..., unique=True)
    full_name: str 
    password_hash: str

    class Settings:
        name = "users"


class RefreshToken(Document):
    """
    Model representing a refresh token associated with a user.
    """
    token_hash: str 
    user: Link[User]
    expires_at: datetime
    created_at: datetime
    
    class Settings:
        name = "refresh_tokens"