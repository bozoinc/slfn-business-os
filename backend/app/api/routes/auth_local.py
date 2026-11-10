"""API routes - Local authentication only (no Authentik OIDC)"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

from app.db.session import get_db
from app.db.models import Contact
from app.api.schemas import ContactCreate, ContactResponse
from app.core.config import Settings, settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter()


def verify_password(plain_password, hashed_password):
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta=None):
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def authenticate_user(email: str, password: str, db):
    """Authenticate user by email and password"""
    user = db.query(Contact).filter(Contact.email == email).first()
    if not user:
        return None
    hashed_password = user.custom_fields.get("hashed_password", "")
    if not hashed_password:
        return None
    if not verify_password(password, hashed_password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db):
    """Get current user from JWT token (local auth only)"""
    from fastapi import HTTPException
    from starlette.status import HTTP_401_UNAUTHORIZED
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email:
            user = db.query(Contact).filter(Contact.email == email).first()
            if user:
                return user
    except Exception:
        pass
    raise credentials_exception


@router.post("/login", response_model=ContactResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Login and get access token (local auth only)"""
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=ContactResponse)
async def read_users_me(current_user):
    """Get current user info"""
    from app.api.schemas import ContactResponse
    return ContactResponse.from_orm(current_user)