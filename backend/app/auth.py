import uuid
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

SECRET_KEY = "dev-secret-key-change-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class TokenData(BaseModel):
    user_id: str
    organization_id: str


class UserContext(BaseModel):
    user_id: uuid.UUID
    organization_id: uuid.UUID


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: uuid.UUID, organization_id: uuid.UUID) -> str:
    """Create JWT token with user_id and organization_id."""
    data = {
        "user_id": str(user_id),
        "organization_id": str(organization_id),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_user_context(credentials = Depends(security)) -> UserContext:
    """Extract and validate JWT token, return UserContext."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        organization_id = payload.get("organization_id")

        if not user_id or not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return UserContext(
            user_id=uuid.UUID(user_id),
            organization_id=uuid.UUID(organization_id),
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
