import httpx
import structlog
from careful.httpx import make_careful_client_from_env

# shared logger for all ingestors
logger = structlog.get_logger("pdp.ingestion")

_client = make_careful_client_from_env(
    requests_per_minute=30,
    retry_attempts=1,
    retry_wait_seconds=10,
)


def make_request(url, headers=None):
    """
    Make an HTTP request with logging & error checking.
    """
    resp = _client.get(url, headers=headers, follow_redirects=True)
    logger.debug("request", url=url, status_code=resp.status_code)
    resp.raise_for_status()
    return resp
