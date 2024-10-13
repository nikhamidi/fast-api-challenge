import logging
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from jwt_services import access_security, refresh_security, current_user
from models.user import User, UserAuth, UserOut
from models.auth import RefreshToken

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/v1/auth')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

@router.post("/register", response_model=UserOut)
async def register(user_auth: UserAuth):
    logger.info(f"Attempting to register user '{user_auth.username}'")
    user = await User.by_username(user_auth.username)
    if user is not None:
        logger.warning(f"Registration failed: User with username '{user_auth.username}' already exists")
        raise HTTPException(status.HTTP_409_CONFLICT, "User with that username already exists")
    
    hashed = hash_password(user_auth.password)
    user = User(username=user_auth.username, password=hashed)
    await user.create()
    logger.info(f"User '{user_auth.username}' registered successfully")
    return user

@router.post("/login")
async def login(user_auth: UserAuth) -> RefreshToken:
    logger.info(f"User '{user_auth.username}' is attempting to log in")
    user = await User.by_username(user_auth.username)
    if user is None or not verify_password(user_auth.password, user.password):
        logger.warning(f"Login failed for user '{user_auth.username}': Invalid username or password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token = access_security.create_access_token(user.jwt_subject)
    refresh_token = refresh_security.create_refresh_token(user.jwt_subject)
    
    logger.info(f"User '{user_auth.username}' logged in successfully")
    return RefreshToken(access_token=access_token, refresh_token=refresh_token)

@router.get("/me", response_model=UserOut)
async def get_user(user: User = Depends(current_user)): 
    logger.info(f"Fetching information for user '{user.username}'")
    return user
