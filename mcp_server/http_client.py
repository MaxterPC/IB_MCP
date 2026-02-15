import logging
import httpx
from mcp_server.config import get_ssl_verify

logger = logging.getLogger(__name__)


def create_client() -> httpx.AsyncClient:
    """Create a configured httpx.AsyncClient with proper SSL settings."""
    return httpx.AsyncClient(verify=get_ssl_verify())


def handle_http_error(exc: httpx.HTTPStatusError) -> dict:
    """Handle HTTP errors from the IBKR API without leaking backend details."""
    logger.error(
        "IBKR API error: status=%d url=%s",
        exc.response.status_code,
        exc.request.url,
    )
    logger.debug("IBKR API error detail: %s", exc.response.text)
    return {
        "error": "IBKR API Error",
        "status_code": exc.response.status_code,
    }


def handle_request_error(exc: httpx.RequestError) -> dict:
    """Handle connection/request errors without leaking internal details."""
    logger.error("Request error: %s", exc)
    return {
        "error": "Request Error",
        "detail": "Failed to connect to the IBKR gateway. Please check the service status.",
    }
