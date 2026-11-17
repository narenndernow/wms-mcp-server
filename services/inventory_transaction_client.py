
import os
import httpx

from dotenv import load_dotenv
from services.auth_client import auth_client

load_dotenv()

INVENTORY_SERVICE_URL = os.getenv(
    "INVENTORY_SERVICE_URL",
    "http://localhost:8081"
)

INVENTORY_TRANSACTIONS_PATH = os.getenv(
    "INVENTORY_TRANSACTIONS_PATH",
    "/api/inventory/product/{productId}/transactions"
)


async def fetch_inventory_transactions(product_id: int) -> list:

    # Step 1: Get JWT automatically
    token = await auth_client.get_token()

    # Step 2: Replace the path variable
    path = INVENTORY_TRANSACTIONS_PATH.format(
        productId=product_id
    )

    # Step 3: Build the URL
    url = (
        f"{INVENTORY_SERVICE_URL.rstrip('/')}/"
        f"{path.lstrip('/')}"
    )

    print("Calling Inventory Service:", url)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:

        # Step 4: Call Java Inventory Service
        response = await client.get(
            url,
            headers=headers
        )

        # Step 5: Retry once if JWT expired
        if response.status_code == 401:
            auth_client.invalidate_token()

            token = await auth_client.get_token()

            headers["Authorization"] = f"Bearer {token}"

            response = await client.get(
                url,
                headers=headers
            )

        print("HTTP Status:", response.status_code)

        response.raise_for_status()

        # Step 6: Parse response
        data = response.json()

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            if isinstance(data.get("content"), list):
                return data["content"]

        raise ValueError(
            "Unexpected inventory transaction response"
        )
