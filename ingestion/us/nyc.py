from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset
from ingestion.utils import make_request
import json

"""
Simple ingestion script for NYC Open Data portal.
Based on the chicago.py example.
"""

CATALOG = "https://data.cityofnewyork.us/api/catalog/v1?limit=100&offset={}"

ODATA_URL = "https://data.cityofnewyork.us/api/odata/v4/{}"


def extract_datasets(catalog):

    datasets = []

    for ds in catalog["results"]:

        rs = ds["resource"]

        dataset = UpstreamDataset(
            name=rs["name"],
            description=rs.get("description", ""),
            upstream_upload_time=parse_date(rs["updatedAt"]),
            publisher_name=rs.get("attribution") or "NYC Open Data",
            publisher_url=rs.get("attribution_link"),
            publisher_upstream_id=rs["id"],
            region_name="New York City, NY",
            region_country_code="us",
            source_url=ds["permalink"],
            upstream_id=rs["id"],
            license="",
            tags=[],
        )

        download_url = ODATA_URL.format(dataset.upstream_id)

        dataset.add_file(
            url=download_url,
            file_type="csv"
        )

        datasets.append(dataset)

    return datasets


def get_full_datasets():

    offset = 0
    all_datasets = []

    while True:

        url = CATALOG.format(offset)

        resp = make_request(url)

        catalog = json.loads(resp.text)

        new_sets = extract_datasets(catalog)

        if not new_sets:
            break

        all_datasets.extend(new_sets)

        offset += 100

    return all_datasets
