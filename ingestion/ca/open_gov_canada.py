from typing import Generator
from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset, PartialDataset
import httpx
import lxml.html
import json
import csv
import io

SITE_URL = "https://search.open.canada.ca/opendata/"
RECORD_URL = "https://open.canada.ca/data/en/dataset/{}"
CATALOGUE_URL = "https://open.canada.ca/data/en/dataset/c4c5c7f1-bfa6-4ff6-b4a0-c164cb2060f7/resource/b8931c16-0710-4c31-bbda-f60841e98cb4"


def make_request(url):
    """
    Make an HTTP request with logging & error checking.
    """
    resp = httpx.get(url)
    resp.raise_for_status()
    return resp


def list_datasets() -> Generator[PartialDataset, None, None]:
    """
    This method can either return a list or `yield` individual
    items as they're found.

    The version below demonstrates yielding items, but
    """
    data = make_request(CATALOGUE_URL)
    for row in csv.DictReader(io.StringIO(data.text)):
        yield PartialDataset(
            url=RECORD_URL.format(row["datasetid"]),
            last_updated=parse_date(row["default.modified"]),
        )

# TO DO:
# 1. get list of datasets (best format? xml?) with upstream ids
# 2. get url and date_modified/date_uploaded from file