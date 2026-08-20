"""API routes - Authentication with Authentik OIDC support"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid
import httpx

from app.db.session import get_db
from app.db.models import Contact
from app.api.schemas import ContactCreate, ContactResponse
from app.core.config import settings
from app.services.authentik import authentik_oidc

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# JWT settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password, hashed_password):
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(email: str, password: str, db: Session):
    """Authenticate user by email and password"""
    user = db.query(Contact).filter(Contact.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.custom_fields.get("hashed_password", "")):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token (supports both local and Authentik tokens)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Try local JWT first
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email:
            user = db.query(Contact).filter(Contact.email == email).first()
            if user:
                return user
    except JWTError:
        pass

    # Try Authentik OIDC token
    if settings.AUTHENTIK_CLIENT_ID:
        payload = await authentik_oidc.validate_token(token)
        if payload:
            email = payload.get("email")
            if email:
                user = db.query(Contact).filter(Contact.email == email).first()
                if user:
                    return user
                # Auto-provision user from Authentik
                user_info = await authentik_oidc.get_user_info(token)
                if user_info:
                    return await provision_user_from_authentik(user_info, db)

    raise credentials_exception


async def provision_user_from_authentik(user_info: dict, db: Session) -> Contact:
    """Provision or update user from Authentik user info"""
    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Authentik")

    user = db.query(Contact).filter(Contact.email == email).first()
    if user:
        # Update existing user
        user.first_name = user_info.get("given_name", user.first_name)
        user.last_name = user_info.get("family_name", user.last_name)
        user.custom_fields = {
            **user.custom_fields,
            "authentik_sub": user_info.get("sub"),
            "authentik_groups": user_info.get("groups", []),
            "is_admin": "admin" in user_info.get("groups", []),
        }
    else:
        # Create new user
        user = Contact(
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
            email=email,
            custom_fields={
                "authentik_sub": user_info.get("sub"),
                "authentik_groups": user_info.get("groups", []),
                "is_admin": "admin" in user_info.get("groups", []),
            },
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/authentik/login")
async def authentik_login(
    redirect_uri: str = Query(...),
    state: str = Query("")
):
    """Redirect to Authentik for OIDC login"""
    if not settings.AUTHENTIK_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Authentik not configured"
        )
    auth_url = authentik_oidc.get_authorization_url(redirect_uri, state)
    return RedirectResponse(url=auth_url)


@router.get("/authentik/callback")
async def authentik_callback(
    code: str = Query(...),
    state: str = Query(""),
    redirect_uri: str = Query(...),
    db: Session = Depends(get_db),
):
    """Handle Authentik OIDC callback"""
    if not settings.AUTHENTIK_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Authentik not configured"
        )

    token_data = await authentik_oidc.exchange_code_for_token(code, redirect_uri)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for token"
        )

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access token in response"
        )

    # Get user info and provision
    user_info = await authentik_oidc.get_user_info(access_token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info"
        )

    user = await provision_user_from_authentik(user_info, db)

    # Create local JWT for session
    local_token = create_access_token(data={"sub": user.email})

    # Redirect to frontend with token
    frontend_url = f"{redirect_uri}?token={local_token}&authentik_token={access_token}"
    return RedirectResponse(url=frontend_url)


@router.post("/register", response_model=ContactResponse)
async def register_user(
    contact: ContactCreate,
    password: str,
    db: Session = Depends(get_db)
):
    """Register a new user with email and password (local auth)"""
    # Check for existing user
    if contact.email:
        existing = db.query(Contact).filter(Contact.email == contact.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

    # Hash password and store in custom_fields
    hashed_password = get_password_hash(password)

    # Create user
    db_contact = Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        company=contact.company,
        job_title=contact.job_title,
        custom_fields={"hashed_password": hashed_password, "is_admin": False}
    )

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return ContactResponse.from_orm(db_contact)


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token (local auth)"""
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
async def read_users_me(
    current_user: Contact = Depends(get_current_user)
):
    """Get current user info"""
    return ContactResponse.from_orm(current_user)