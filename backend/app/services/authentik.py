"""Authentik OIDC integration service"""

from typing import Optional, Dict, Any
from jose import JWTError, jwt
import httpx
from datetime import datetime, timedelta

from app.core.config import settings


class AuthentikOIDC:
    """Authentik OIDC client for token validation and user info"""

    def __init__(self):
        self.base_url = settings.AUTHENTIK_URL.rstrip("/")
        self.client_id = settings.AUTHENTIK_CLIENT_ID
        self.client_secret = settings.AUTHENTIK_CLIENT_SECRET
        self.realm = settings.AUTHENTIK_REALM
        self._jwks_cache: Optional[Dict] = None
        self._jwks_cache_time: Optional[datetime] = None

    async def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set from Authentik (cached for 1 hour)"""
        now = datetime.utcnow()
        if (
            self._jwks_cache
            and self._jwks_cache_time
            and (now - self._jwks_cache_time).total_seconds() < 3600
        ):
            return self._jwks_cache

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/application/o/{self.realm}/jwks/",
                timeout=10.0,
            )
            response.raise_for_status()
            jwks: Dict[str, Any] = response.json()
            self._jwks_cache = jwks
            self._jwks_cache_time = now
            return jwks

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token from Authentik"""
        try:
            # Get JWKS for signature verification
            jwks = await self.get_jwks()

            # Decode and validate token
            payload = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=f"{self.base_url}/application/o/{self.realm}/",
            )
            return payload
        except JWTError:
            return None
        except Exception:
            return None

    async def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user info from Authentik using access token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/application/o/{self.realm}/userinfo/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0,
            )
            if response.status_code == 200:
                return response.json()
            return None

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/application/o/{self.realm}/token/",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=10.0,
            )
            if response.status_code == 200:
                return response.json()
            return None

    def get_authorization_url(self, redirect_uri: str, state: str = "") -> str:
        """Generate authorization URL for OIDC flow"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.base_url}/application/o/{self.realm}/authorize/?{query}"


# Global instance
authentik_oidc = AuthentikOIDC()