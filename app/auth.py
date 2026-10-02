"""
Password hashing (bcrypt) and JWT creation/verification.

Uses the `bcrypt` library directly rather than passlib, since passlib's
bcrypt backend has version-compatibility issues with bcrypt 4.x.
Uses PyJWT for tokens - simple, well-maintained, no extra native deps.
"""
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours - fine for a student project

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def _require_secret() -> str:
    if not SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY is not set in .env. Generate one with: "
            "python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    return SECRET_KEY


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(user_id: str, username: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "username": username,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, _require_secret(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, _require_secret(), algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token expired, please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """FastAPI dependency: extracts and validates the JWT from the
    Authorization header, returns {"user_id": ..., "username": ...}."""
    payload = decode_access_token(token)
    return {"user_id": payload["sub"], "username": payload["username"]}
