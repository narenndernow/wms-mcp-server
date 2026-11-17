
"""MCP server exposing tools for WMS microservices."""

import asyncio
import httpx

from fastmcp import FastMCP
from services.inventory_transaction_client import (
    fetch_inventory_transactions
)

from services.product_client import fetch_product

mcp = FastMCP("WMS MCP Server")


@mcp.tool()
async def get_inventory_transactions(product_id: int) -> dict:
    """
    Retrieve inventory IN/OUT transactions
    for a product from Java Inventory Service.
    """

    transactions = await fetch_inventory_transactions(product_id)

    return {
        "product_id": product_id,
        "transactions": transactions
    }

@mcp.tool()
async def get_product_details(product_id: int) -> dict:
    """
    Retrieve product information from the Java WMS
    Product Service, including available quantity
    and reorder level when provided.
    """

    try:
        product = await fetch_product(product_id)

        return {
            "found": True,
            "product_id": product_id,
            "product": product
        }

    except httpx.HTTPStatusError as error:
        return {
            "found": False,
            "product_id": product_id,
            "error": (
                f"Product Service returned HTTP "
                f"{error.response.status_code}"
            )
        }

    except httpx.RequestError as error:
        return {
            "found": False,
            "product_id": product_id,
            "error": f"Product Service unavailable: {error}"
        }



async def main():
    """Start the MCP HTTP server."""

    await mcp.run_http_async(
        host="0.0.0.0",
        port=8001
    )


if __name__ == "__main__":
    asyncio.run(main())
