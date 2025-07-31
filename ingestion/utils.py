import httpx
import structlog

logger = structlog.get_logger("pdp.ingestion")


def make_request(url):
    """
    Make an HTTP request with logging & error checking.
    """
    resp = httpx.get(url)
    logger.debug("request", url=url, status_code=resp.status_code)
    resp.raise_for_status()
    return resp
