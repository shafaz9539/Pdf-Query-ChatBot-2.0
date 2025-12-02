from fastapi import APIRouter, Depends, HTTPException, status

from ..models.schema import AuthResponse, UserCreate, UserLogin, UserSignupProjection
from ..models.document import User
from ..core.security import create_access_token, create_refresh_token, get_current_user
from ..utils.generate_hash import generate_hash, verify_hash

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
async def create_user(user_data: UserCreate):
    """
    Create a new user
    """
    existing_user = await User.find_one( User.email == user_data.email ).project(UserSignupProjection)

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = generate_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hashed_password
    )

    await new_user.create()

    access_token = create_access_token(new_user.id)

    return {
        "message": "User created successfully!",
        "user": {
            "email": new_user.email,
            "full_name": new_user.full_name,
            "id": str(new_user.id)
        },
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def login_user(credentials: UserLogin):
    """
    Authenticates a user.
    """
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password."
    )

    user_doc = await User.find_one(User.email == credentials.email)

    if not user_doc:
        raise invalid_credentials

    if not verify_hash(credentials.password, user_doc.password_hash):
        raise invalid_credentials   
    
    access_token = create_access_token(user_doc.id)
    refresh_token = await create_refresh_token(user_doc)
            
    return {
        "message": "Login successful!",
        "user": {
            "email": user_doc.email,
            "full_name": user_doc.full_name,
            "id": str(user_doc.id)
        },  
        "access_token": access_token,
        
        "token_type": "bearer"
    }

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Returns the current logged-in user's data. 
    Requires a valid JWT in the Authorization header.
    """
    return current_user

