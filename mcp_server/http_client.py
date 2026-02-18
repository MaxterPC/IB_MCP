import logging
from typing import Optional

import httpx
from mcp_server.config import get_ssl_verify

logger = logging.getLogger(__name__)

MAX_ERROR_DETAIL_LENGTH = 500

STATUS_GUIDANCE: dict[int, str] = {
    401: "Session may have expired. Try calling /iserver/reauthenticate or /iserver/auth/status to check.",
    403: (
        "Permission denied by IBKR. This usually means the account lacks permissions"
        " for this operation, or the feature is not enabled for your account type."
        " Verify account permissions in IBKR Account Management."
    ),
    404: "The requested resource was not found. Verify the account ID, contract ID, or other identifiers.",
    429: "Rate limit exceeded. Wait a moment before retrying.",
    500: "IBKR internal server error. This is typically a transient issue — retry after a few seconds.",
    503: "IBKR service temporarily unavailable. The gateway may be restarting or under maintenance.",
}


def create_client() -> httpx.AsyncClient:
    """Create a configured httpx.AsyncClient with proper SSL settings."""
    return httpx.AsyncClient(verify=get_ssl_verify())


def _extract_error_detail(response: httpx.Response) -> Optional[str]:
    """Extract error detail from an IBKR response body.

    Tries JSON first (IBKR often returns structured errors),
    falls back to raw text. Truncates to MAX_ERROR_DETAIL_LENGTH.
    """
    try:
        body = response.json()
        if isinstance(body, dict):
            detail = body.get("error") or body.get("message") or str(body)
        else:
            detail = str(body)
    except Exception:
        detail = response.text

    if not detail:
        return None

    detail = detail.strip()
    if len(detail) > MAX_ERROR_DETAIL_LENGTH:
        detail = detail[:MAX_ERROR_DETAIL_LENGTH] + "..."
    return detail or None


def handle_http_error(exc: httpx.HTTPStatusError) -> dict:
    """Handle HTTP errors from the IBKR API without leaking backend details."""
    status = exc.response.status_code

    logger.error(
        "IBKR API error: status=%d url=%s",
        status,
        exc.request.url,
    )
    logger.debug("IBKR API error detail: %s", exc.response.text)

    result: dict = {
        "error": "IBKR API Error",
        "status_code": status,
    }

    detail = _extract_error_detail(exc.response)
    if detail:
        result["detail"] = detail

    guidance = STATUS_GUIDANCE.get(status)
    if guidance:
        result["guidance"] = guidance

    return result


def handle_request_error(exc: httpx.RequestError) -> dict:
    """Handle connection/request errors without leaking internal details."""
    logger.error("Request error: %s", exc)
    return {
        "error": "Request Error",
        "detail": "Failed to connect to the IBKR gateway. Please check the service status.",
    }
