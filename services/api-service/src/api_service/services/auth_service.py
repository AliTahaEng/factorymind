"""JWT authentication and authorization service."""
import logging
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from api_service.config import Settings
from api_service.interfaces.i_token_store import ITokenStore

logger = logging.getLogger(__name__)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, settings: Settings, token_store: ITokenStore):
        self._settings = settings
        self._token_store = token_store

    def hash_password(self, password: str) -> str:
        return _pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return _pwd_context.verify(plain, hashed)

    def create_access_token(self, subject: str, role: str) -> tuple[str, int]:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._settings.jwt_access_token_expire_minutes)
        payload = {"sub": subject, "role": role, "exp": expire, "type": "access"}
        token = jwt.encode(payload, self._settings.jwt_secret_key, algorithm=self._settings.jwt_algorithm)
        return token, self._settings.jwt_access_token_expire_minutes * 60

    def create_refresh_token(self, subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=self._settings.jwt_refresh_token_expire_days)
        payload = {"sub": subject, "exp": expire, "type": "refresh"}
        return jwt.encode(payload, self._settings.jwt_secret_key, algorithm=self._settings.jwt_algorithm)

    async def verify_token(self, token: str) -> dict:
        if await self._token_store.is_blacklisted(token):
            raise JWTError("Token has been revoked")
        payload = jwt.decode(token, self._settings.jwt_secret_key, algorithms=[self._settings.jwt_algorithm])
        return payload

    async def logout(self, token: str) -> None:
        try:
            payload = jwt.decode(token, self._settings.jwt_secret_key, algorithms=[self._settings.jwt_algorithm])
            exp = payload.get("exp", 0)
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = max(exp - now, 1)
        except Exception:
            ttl = self._settings.jwt_access_token_expire_minutes * 60
        await self._token_store.blacklist(token, ttl)
