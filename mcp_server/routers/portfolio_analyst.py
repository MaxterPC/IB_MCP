# portfolio_analyst.py
from fastapi import APIRouter, Body
from typing import List, Optional
import httpx
from pydantic import BaseModel, Field
from mcp_server.config import BASE_URL
from mcp_server.http_client import create_client, handle_http_error, handle_request_error

router = APIRouter()

# --- Pydantic Models ---


class PARequest(BaseModel):
    """Request model for Portfolio Analyst performance and periods data."""
    acctIds: List[str] = Field(..., description="List of account IDs to retrieve data for.")
    period: Optional[str] = Field(None, description="Time period for data, e.g., '1D', '1W', '1M', '3M', '1Y'.")


class PATransactionsRequest(BaseModel):
    """Request model for Portfolio Analyst transaction history."""
    acctIds: List[str] = Field(..., description="List of account IDs to retrieve transactions for.")
    days: Optional[int] = Field(None, description="Number of days of transaction history to retrieve.")
    currency: Optional[str] = Field(None, description="Currency filter for transactions.")


# --- Portfolio Analyst Router Endpoints ---

@router.post(
    "/pa/allperiods",
    tags=["Portfolio Analyst"],
    summary="Available Periods",
    description="Returns a list of all available periods for Portfolio Analyst data."
)
async def get_all_periods(body: PARequest = Body(...)):
    """
    Retrieves all available time periods for Portfolio Analyst queries.
    """
    async with create_client() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/pa/allperiods",
                json=body.dict(exclude_none=True),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return handle_http_error(exc)
        except httpx.RequestError as exc:
            return handle_request_error(exc)


@router.post(
    "/pa/performance",
    tags=["Portfolio Analyst"],
    summary="Portfolio Performance",
    description="Returns the performance (NAV) of specified account(s)."
)
async def get_performance(body: PARequest = Body(...)):
    """
    Retrieves portfolio performance data for specified accounts.
    """
    async with create_client() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/pa/performance",
                json=body.dict(exclude_none=True),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return handle_http_error(exc)
        except httpx.RequestError as exc:
            return handle_request_error(exc)


@router.post(
    "/pa/transactions",
    tags=["Portfolio Analyst"],
    summary="Transaction History",
    description="Returns a list of transactions for specified account(s)."
)
async def get_transactions(body: PATransactionsRequest = Body(...)):
    """
    Retrieves transaction history for specified accounts.
    """
    async with create_client() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/pa/transactions",
                json=body.dict(exclude_none=True),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return handle_http_error(exc)
        except httpx.RequestError as exc:
            return handle_request_error(exc)
