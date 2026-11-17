
import asyncio
import os
import time

import httpx
from dotenv import load_dotenv

load_dotenv()


AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://localhost:8081"
)

AUTH_LOGIN_PATH = os.getenv(
    "AUTH_LOGIN_PATH",
    "/api/auth/login"
)

WMS_USERNAME = os.getenv("WMS_USERNAME")
WMS_PASSWORD = os.getenv("WMS_PASSWORD")


class AuthClient:

    def __init__(self):
        self._token = None
        self._expires_at = 0.0
        self._lock = asyncio.Lock()

    async def get_token(self) -> str:
        # Reuse the token if it is still valid.
        if self._token and time.time() < self._expires_at:
            return self._token

        async with self._lock:
            if self._token and time.time() < self._expires_at:
                return self._token

            await self._login()

            return self._token

    async def _login(self):
        if not WMS_USERNAME or not WMS_PASSWORD:
            raise RuntimeError(
                "WMS_USERNAME or WMS_PASSWORD is missing"
            )

        url = (
            f"{AUTH_SERVICE_URL.rstrip('/')}/"
            f"{AUTH_LOGIN_PATH.lstrip('/')}"
        )

        payload = {
            "username": WMS_USERNAME,
            "password": WMS_PASSWORD
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=payload
            )

            response.raise_for_status()
            data = response.json()

        token = data.get("accessToken") or data.get("token")

        if not token:
            raise ValueError(
                "Auth Service response does not contain "
                "accessToken or token"
            )

        self._token = token

        # Conservative temporary lifetime.
        # Replace with the real expiresIn value
        # or a verified JWT expiry.
        expires_in = int(data.get("expiresIn", 300))

        self._expires_at = time.time() + max(
            0,
            expires_in - 30
        )

    def invalidate_token(self):
        self._token = None
        self._expires_at = 0.0


auth_client = AuthClient()
