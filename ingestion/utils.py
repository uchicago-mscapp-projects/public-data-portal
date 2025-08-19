import httpx
import structlog

# shared logger for all ingestors
logger = structlog.get_logger("pdp.ingestion")


def make_request(url, headers=None):
    """
    Make an HTTP request with logging & error checking.
    """
    resp = httpx.get(url, headers=headers)
    logger.debug("request", url=url, status_code=resp.status_code)
    resp.raise_for_status()
    return resp
