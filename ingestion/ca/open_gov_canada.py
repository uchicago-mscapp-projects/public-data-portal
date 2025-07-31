from typing import Generator
from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset, PartialDataset, AltStr
import httpx
import lxml.html
import json
import csv
import io
import re
from functools import reduce

SITE_URL = "https://search.open.canada.ca/opendata/"
CSV_URL = "https://open.canada.ca/data/dataset/c4c5c7f1-bfa6-4ff6-b4a0-c164cb2060f7/resource/312a65c5-d0bc-4445-8a24-95b2690cc62b/download/main.csv"
# RECORD_URL = "https://open.canada.ca/data/en/api/3/action/datastore_search?resource_id={}"
RECORD_URL = "https://open.canada.ca/data/api/action/package_show?id={}"


def make_request(url):
    """
    Make an HTTP request with logging & error checking.
    """
    resp = httpx.get(url, follow_redirects=True)
    resp.raise_for_status()
    return resp


def list_datasets() -> Generator[PartialDataset, None, None]:
    """
    This method can either return a list or `yield` individual
    items as they're found.

    The version below demonstrates yielding items, but
    """
    data = make_request(CSV_URL)
    for row in csv.DictReader(io.StringIO(data.text)):
        # fill last_updated with date_modified if it exists or date_published if not
        if row["date_modified"] == "":
            last_updated = parse_date(row["date_published"])
        else:
            last_updated = parse_date(row["date_modified"])
        yield PartialDataset(
            url=RECORD_URL.format(row["id"]),
            last_updated=last_updated,
        )


def get_dataset_details(pd: PartialDataset) -> UpstreamDataset:
    # parse HTML from request
    resp = make_request(pd.url)
    root = lxml.html.fromstring(resp.content)

    ld_json = json.loads(root.text_content())
    ld_record = ld_json["result"]

    ds = UpstreamDataset(
        name=ld_record["title"],
        description=ld_record["notes"],
        alternate_names=[
            AltStr(value=ld_record["title_translated"][lang], lang=lang)
            for lang in ld_record["title_translated"].keys()
        ],
        alternate_descriptions=[
            AltStr(value=ld_record["notes_translated"][lang], lang=lang)
            for lang in ld_record["notes_translated"].keys()
        ],
        upstream_id=ld_record["id"],
        source_url=pd.url,
        upstream_upload_time=parse_date(ld_record["date_published"]),
        license=ld_record["license_title"],
        # subject & topic_category fields are lists, keywords is dict with lists for each language
        tags=ld_record["subject"]
        + ld_record.get("topic_category", [])
        + reduce(
            lambda x, y: x + y,
            [ld_record["keywords"][lang] for lang in ld_record["keywords"].keys()],
        ),
        publisher_name=ld_record["organization"]["title"],
        publisher_url=SITE_URL,
        region_name="Canada",
        # TO DO: subregion
        region_country_code="ca",
    )
    for file in ld_record["resources"]:
        ds.add_file(url=file["url"], file_type=get_file_format(file["format"]), name=file["name"])

    return ds


# handle file formats:
# TO DO: complete list of file formats
def get_file_format(original_format):
    format = original_format.lower()
    if format in ["ascii grid", "esri rest", "geotif", "gpkg", "mxd", "segy", "wms"]:
        return "other-geo"
    elif format in ["docx", "edi", "html", "kmz", "pdf", "tiff", "zip"]:
        return "other"
    else:
        return format


# ALL CANADIAN PROVINCES:
"""
ALBERTA = "Government of Alberta"
BRITISH_COLUMBIA = "Government of British Columbia"
MANITOBA = "Government of Manitoba"
NEW_BRUNSWICK = "Government of New Brunswick"
NEWFOUNDLAND_LABRADOR
NORTHWEST_TERRITORIES
NOVA_SCOTIA
NUNAVUT
ONTARIO
PRINCE_EDWARD
QUEBEC = "Government and Municipalities of Québec | Gouvernement et municipalités du Québec"
SASKATCHEWAN
YUKON
"""

# fill subregion field, if applicable:
# def get_ca_province():
