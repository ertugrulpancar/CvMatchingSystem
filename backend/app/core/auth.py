from functools import lru_cache
from uuid import UUID

import jwt
from fastapi import HTTPException, Request
from jwt import PyJWKClient

from app.core.config import get_settings


@lru_cache
def _get_jwk_client() -> PyJWKClient:
    settings = get_settings()
    return PyJWKClient(f"{settings.supabase_url}/auth/v1/.well-known/jwks.json")


def get_current_user(request: Request) -> UUID:
    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Kimlik doğrulama gerekli")

    try:
        signing_key = _get_jwk_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş oturum") from exc

    return UUID(payload["sub"])
