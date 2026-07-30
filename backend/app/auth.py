"""
Supabase authentication and ownership helpers.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

from config.settings import settings
from models.database import Content, Document, User, get_db

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: uuid.UUID
    email: str
    role: Optional[str]
    organization_id: Optional[str]
    claims: Dict[str, Any]


def _auth_error(error_code: str, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error_code": error_code,
            "error_message": message,
        },
        headers={"WWW-Authenticate": "Bearer"} if status_code == status.HTTP_401_UNAUTHORIZED else None,
    )


def decode_supabase_jwt(token: str) -> Dict[str, Any]:
    """Validate and decode a Supabase access token."""
    if not settings or not settings.supabase_jwt_secret:
        raise _auth_error("AUTH_NOT_CONFIGURED", "Supabase JWT validation is not configured", status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"require": ["exp", "sub"]},
            audience=settings.supabase_jwt_audience,
            leeway=0,
        )
    except ExpiredSignatureError as exc:
        raise _auth_error("TOKEN_EXPIRED", "Authentication token has expired") from exc
    except InvalidTokenError as exc:
        raise _auth_error("INVALID_TOKEN", "Authentication token is invalid") from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    """FastAPI dependency that rejects missing, invalid, or expired JWTs."""
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise _auth_error("AUTH_REQUIRED", "Authorization bearer token is required")

    claims = decode_supabase_jwt(credentials.credentials)
    subject = claims.get("sub")

    try:
        user_id = uuid.UUID(str(subject))
    except (TypeError, ValueError) as exc:
        raise _auth_error("INVALID_TOKEN_SUBJECT", "Authentication token subject is not a valid user id") from exc

    email = claims.get("email") or claims.get("user_metadata", {}).get("email") or ""
    organization_id = claims.get("organization_id") or claims.get("org_id") or claims.get("app_metadata", {}).get("organization_id")

    return CurrentUser(
        id=user_id,
        email=email,
        role=claims.get("role"),
        organization_id=str(organization_id) if organization_id else None,
        claims=claims,
    )


def ensure_user_profile(db: Session, current_user: CurrentUser) -> User:
    """Create the public user profile row needed by document/content FKs."""
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        return user

    user = User(
        id=current_user.id,
        email=current_user.email or f"{current_user.id}@unknown.local",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_owned_document(db: Session, document_id: str, current_user: CurrentUser) -> Document:
    try:
        doc_uuid = uuid.UUID(document_id)
    except (TypeError, ValueError) as exc:
        raise _auth_error("INVALID_DOCUMENT_ID", "Document id is invalid", status.HTTP_400_BAD_REQUEST) from exc

    document = db.query(Document).filter(Document.id == doc_uuid).first()
    if document is None:
        raise _auth_error("DOCUMENT_NOT_FOUND", "Document not found", status.HTTP_404_NOT_FOUND)

    if document.user_id != current_user.id:
        raise _auth_error("DOCUMENT_FORBIDDEN", "Document belongs to another user", status.HTTP_403_FORBIDDEN)

    return document


def get_owned_content(db: Session, content_id: str, current_user: CurrentUser) -> Content:
    try:
        content_uuid = uuid.UUID(content_id)
    except (TypeError, ValueError) as exc:
        raise _auth_error("INVALID_CONTENT_ID", "Content id is invalid", status.HTTP_400_BAD_REQUEST) from exc

    content = db.query(Content).filter(Content.id == content_uuid).first()
    if content is None:
        raise _auth_error("CONTENT_NOT_FOUND", "Content not found", status.HTTP_404_NOT_FOUND)

    if content.user_id != current_user.id:
        raise _auth_error("CONTENT_FORBIDDEN", "Content belongs to another user", status.HTTP_403_FORBIDDEN)

    return content


def get_db_current_user(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    ensure_user_profile(db, current_user)
    return current_user


def _is_dev_mode() -> bool:
    """Check if running in local development mode (bypass auth)."""
    import os
    return os.environ.get("USE_SQLITE_DEV", "").lower() in ("1", "true", "yes") or \
           os.environ.get("PITCHFLOW_DEV", "").lower() in ("1", "true", "yes")


DEV_USER = CurrentUser(
    id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
    email="dev@pitchflow.local",
    role="authenticated",
    organization_id=None,
    claims={"sub": "00000000-0000-0000-0000-000000000001", "email": "dev@pitchflow.local", "role": "authenticated"},
)


async def get_current_user_or_dev(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    """Like get_current_user, but bypasses auth in local dev mode.
    
    In production: rejects missing/invalid tokens.
    In dev mode (PITCHFLOW_DEV/USE_SQLITE_DEV): returns a dummy dev user.
    """
    if _is_dev_mode():
        return DEV_USER

    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise _auth_error("AUTH_REQUIRED", "Authorization bearer token is required")

    claims = decode_supabase_jwt(credentials.credentials)
    subject = claims.get("sub")

    try:
        user_id = uuid.UUID(str(subject))
    except (TypeError, ValueError) as exc:
        raise _auth_error("INVALID_TOKEN_SUBJECT", "Authentication token subject is not a valid user id") from exc

    email = claims.get("email") or claims.get("user_metadata", {}).get("email") or ""
    organization_id = claims.get("organization_id") or claims.get("org_id") or claims.get("app_metadata", {}).get("organization_id")

    return CurrentUser(
        id=user_id,
        email=email,
        role=claims.get("role"),
        organization_id=str(organization_id) if organization_id else None,
        claims=claims,
    )
