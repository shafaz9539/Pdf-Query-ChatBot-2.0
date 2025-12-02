# # src/core/security.py

# from datetime import datetime, timedelta, timezone
# from jwt import encode, decode, PyJWTError
# from fastapi.security import OAuth2PasswordBearer
# from fastapi import Depends, HTTPException, status

# from ..core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
# from ..models.document import User 
# from server.src.models.document import RefreshToken
# from src.utils.generate_hash import generate_hash

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")

# def create_access_token(user_id: str) -> str:
#     """Encodes user data (subject) into a JWT using PyJWT."""
#     expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode = {
#         "sub": str(user_id),
#         "exp": expire.timestamp(),
#         "iat": datetime.now(timezone.utc).timestamp()
#         }
        
#     access_token = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return access_token

# # --- Token Verification (Decoding) Dependency ---
# async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
#     """Decodes the JWT and retrieves the User document from MongoDB."""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         # 1. Decode the token using PyJWT
#         payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
#         # 2. Extract the user ID (subject 'sub')
#         user_id: str = payload.get("sub") 
#         if user_id is None:
#             raise credentials_exception
            
#     except PyJWTError:
#         # Catches expired token, invalid signature, etc.
#         raise credentials_exception

#     # 3. Find the user in the database using Beanie
#     # The sub claim holds the user's MongoDB ID string
#     user = await User.get(user_id) 
#     if user is None:
#         raise credentials_exception
        
#     return user

# async def create_refresh_token(user: User) -> str:
#     """Creates a refresh token with a longer expiration time."""
#     try:
#         expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
#         to_encode = {
#             "sub": str(user.id),
#             "exp": expire.timestamp(),
#             "iat": datetime.now(timezone.utc).timestamp()
#         }

#         refresh_token = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#         hash_refresh_token = generate_hash(refresh_token)

#         new_refresh_token = RefreshToken(
#             token_hash=hash_refresh_token,
#             user=user,
#             expires_at=expire,
#             created_at=datetime.now(timezone.utc)
#         )

#         await new_refresh_token.create()
#         return refresh_token
#     except PyJWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not create refresh token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )