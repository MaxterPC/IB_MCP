# options_chains.py
from fastapi import APIRouter, Query
from typing import Optional
import httpx
from mcp_server.config import BASE_URL
from mcp_server.http_client import create_client, handle_http_error, handle_request_error

router = APIRouter()

# --- Options Chains Router Endpoints ---

@router.get(
    "/trsrv/secdef/chains",
    tags=["Options Chains"],
    summary="Get Options Chains",
    description="Returns the option chain for a given underlying symbol."
)
async def get_options_chains(
    symbol: str = Query(..., description="The underlying symbol for the option chain."),
    expire: Optional[str] = Query(None, description="The expiration date in YYYYMMDD format."),
    strike: Optional[float] = Query(None, description="The strike price."),
    right: Optional[str] = Query(None, description="The option right: 'C' for Call or 'P' for Put."),
    exchange: Optional[str] = Query(None, description="The exchange to query. Defaults to SMART."),
    chainType: Optional[str] = Query(None, description="The type of chain to return: 'CALL' or 'PUT'.")
):
    """
    Fetches the option chain for a given underlying symbol. You can filter the results by expiration, strike, right, and exchange.
    """
    params = {"symbol": symbol}
    if expire:
        params["expire"] = expire
    if strike:
        params["strike"] = strike
    if right:
        params["right"] = right
    if exchange:
        params["exchange"] = exchange
    if chainType:
        params["chainType"] = chainType

    async with create_client() as client:
        try:
            response = await client.get(f"{BASE_URL}/trsrv/secdef/chains", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return handle_http_error(exc)
        except httpx.RequestError as exc:
            return handle_request_error(exc)
