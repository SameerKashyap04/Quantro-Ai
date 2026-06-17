"""
Quantro Personal AI — Auth Service
Handles authentication logic.
"""
from apps.api.config import get_settings
from apps.api.core.security import verify_password, hash_password, create_access_token, create_refresh_token, decode_token
from apps.api.core.exceptions import AuthenticationError

settings = get_settings()


class AuthService:
    """Authentication business logic."""

    @staticmethod
    def authenticate(username: str, password: str) -> dict:
        """Verify credentials and return tokens."""
        # Single-user system: check against env-configured admin credentials
        if username != settings.admin_username:
            raise AuthenticationError("Invalid username or password")

        # On first run, admin_password is the raw password.
        # In production, you'd store a hash in the DB.
        if password != settings.admin_password:
            raise AuthenticationError("Invalid username or password")

        token_data = {"sub": username, "role": "admin"}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60,
        }

    @staticmethod
    def refresh(refresh_token: str) -> dict:
        """Generate new access token from refresh token."""
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")

        token_data = {"sub": payload["sub"], "role": payload.get("role", "admin")}
        new_access_token = create_access_token(token_data)

        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,  # reuse refresh token
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60,
        }
