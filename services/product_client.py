import os
import httpx
from dotenv import load_dotenv

from services.auth_client import auth_client

load_dotenv()


PRODUCT_SERVICE_URL = os.getenv(
    "PRODUCT_SERVICE_URL",
    "http://localhost:8081"
)

PRODUCT_API_PATH = os.getenv(
    "PRODUCT_API_PATH",
    "/api/products/{product_id}"
)


async def fetch_product(product_id: int) -> dict:

    path = PRODUCT_API_PATH.format(
        product_id=product_id
    )

    url = (
        f"{PRODUCT_SERVICE_URL.rstrip('/')}/"
        f"{path.lstrip('/')}"
    )

    for attempt in range(2):

        token = await auth_client.get_token()

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers=headers
            )

        # A token may have expired earlier than expected.
        # Invalidate it and retry authentication once.
        if response.status_code == 401 and attempt == 0:
            auth_client.invalidate_token()
            continue

        response.raise_for_status()

        product = response.json()

        if not isinstance(product, dict):
            raise ValueError(
                "Product Service returned invalid JSON"
            )

        return product

    raise RuntimeError("Product authentication failed")
