from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.core.config import settings
from src.core import security
from src.api import deps
from src.models.user import User
from src.schemas.user import Token, UserCreate, User as UserSchema, GoogleToken

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    email = form_data.username.lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.user_id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserSchema)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    email = user_in.email.lower()
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="This email is already registered. Please go to the login page to sign in.",
        )
    user = User(
        email=email,
        name=user_in.name,
        phone=user_in.phone,
        hashed_password=security.get_password_hash(user_in.password),
        role="USER",
        is_active=True,
        onboarding_completed=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/google", response_model=Any)
def google_auth(
    *,
    db: Session = Depends(deps.get_db),
    token_in: GoogleToken,
) -> Any:
    """
    Authenticate user via Google ID Token.
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        
        # Verify the token
        if not settings.GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Google Auth is not configured on the server")
            
        idinfo = id_token.verify_oauth2_token(
            token_in.token, requests.Request(), settings.GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="No email provided by Google")
            
        google_id = idinfo.get("sub")
        name = idinfo.get("name")
        picture = idinfo.get("picture")
        
        # Find user by google_id or email
        user = db.query(User).filter((User.google_id == google_id) | (User.email == email)).first()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                google_id=google_id,
                name=name,
                profile_image=picture,
                role="USER",
                is_active=True,
                onboarding_completed=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user if needed (e.g. they had email/pass but now linked google)
            if not user.google_id:
                user.google_id = google_id
            if not user.name and name:
                user.name = name
            if not user.profile_image and picture:
                user.profile_image = picture
            db.commit()

        # Issue JWT
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            user.user_id, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": str(user.user_id),
                "email": user.email,
                "name": user.name,
                "profile_image": user.profile_image,
                "onboarding_completed": user.onboarding_completed,
                "role": user.role
            }
        }
    except ValueError as e:
        # Invalid token
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")
