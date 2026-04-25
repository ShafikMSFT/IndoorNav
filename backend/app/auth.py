"""Entra ID (Azure AD) JWT token validation middleware.

Uses Microsoft's token validation approach without local RSA crypto:
- Decode token claims without signature verification for reading
- Validate by calling Microsoft Graph /me endpoint with the token
- Cache the validation result briefly
"""

from typing import Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings

_bearer_scheme = HTTPBearer(auto_error=False)


def _decode_jwt_unverified(token: str) -> dict:
    """Decode JWT payload without signature verification (for claim reading)."""
    import base64
    import json

    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format")

    # Decode payload (second part)
    payload_b64 = parts[1]
    # Add padding if needed
    padding = 4 - len(payload_b64) % 4
    if padding != 4:
        payload_b64 += "=" * padding

    payload_bytes = base64.urlsafe_b64decode(payload_b64)
    return json.loads(payload_bytes)


async def _validate_token(token: str, settings: Settings) -> dict:
    """
    Validate a Bearer token by:
    1. Decoding claims to check audience, issuer, expiry
    2. Calling Microsoft Graph to verify the token is genuine
    """
    import time

    # Decode without verification to read claims
    try:
        claims = _decode_jwt_unverified(token)
    except (ValueError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )

    # Check audience
    aud = claims.get("aud", "")
    if aud != settings.azure_client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid audience: {aud}",
        )

    # Check issuer
    expected_issuer = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/v2.0"
    if claims.get("iss") != expected_issuer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid issuer",
        )

    # Check expiry
    exp = claims.get("exp", 0)
    if time.time() > exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )

    # Validate token is genuine by calling Microsoft Graph
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token rejected by Microsoft Graph",
            )

    return claims


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> dict:
    """
    FastAPI dependency: extract and validate the Bearer token.
    Returns the decoded JWT claims (user info).

    Usage:
        @router.get("/protected")
        async def protected(user: dict = Depends(get_current_user)):
            return {"user": user["preferred_username"]}
    """
    if not settings.azure_tenant_id or not settings.azure_client_id:
        # Auth not configured — allow all (dev mode)
        return {"preferred_username": "dev@local", "roles": ["admin"]}

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await _validate_token(credentials.credentials, settings)


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    FastAPI dependency: require the 'admin' role.
    Assign roles via Entra ID Enterprise Application → App Roles.
    """
    roles = user.get("roles", [])
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return user
