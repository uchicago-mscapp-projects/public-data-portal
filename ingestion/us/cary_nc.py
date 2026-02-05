from typing import Generator
from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset, PartialDataset
from ingestion.utils import make_request, logger
import lxml.html
import json
import csv
import io

"""
The town uses the "OpenDataSoft" platform & API.
"""

CSV_URL = "https://data.townofcary.org/api/explore/v2.1/catalog/exports/csv?delimiter=%2C&lang=en"
RECORD_URL = "https://data.townofcary.org/explore/dataset/{}/"


def list_datasets() -> Generator[PartialDataset, None, None]:
    """
    This method can either return a list or `yield` individual
    items as they're found.

    The version below demonstrates yielding items, but
    """
    data = make_request(CSV_URL)
    for row in csv.DictReader(io.StringIO(data.text)):
        yield PartialDataset(
            url=RECORD_URL.format(row["datasetid"]),
            last_updated=parse_date(row["default.modified"]),
        )


def get_dataset_details(pd: PartialDataset) -> UpstreamDataset:
    # parse HTML from request
    resp = make_request(pd.url)
    root = lxml.html.fromstring(resp.content)

    # main dataset info is tucked away in JSON on this attribute
    dataset_schema = root.xpath("//div[@ctx-dataset-schema]/@ctx-dataset-schema")[0]

    # there is an ld+json microformat embedded on the page with additional information
    ld_json = root.xpath("//script[@type='application/ld+json']/text()")[0]

    # the JSON has improperly escaped data, try to handle but skip if invalid
    dataset_schema = dataset_schema.replace(r"\{", "{").replace(r"\}", "}")
    try:
        data = json.loads(dataset_schema)
        ld_record = json.loads(ld_json)
    except json.JSONDecodeError as e:
        logger.error("invalid JSON", json=dataset_schema, exception=str(e))
        return None

    # TODO: if this microformat is used frequently, we could create
    # automatic extraction for it

    ds = UpstreamDataset(
        name=ld_record["name"].strip(),
        description=ld_record["description"].strip(),
        upstream_id=data["datasetid"].strip(),
        source_url=pd.url,
        upstream_upload_time=parse_date(data["basic_metas"]["default"]["modified"]),
        license=data["basic_metas"]["default"].get("license", ""),
        tags=ld_record.get("keywords", []),
        publisher_name="Town of Cary",
        publisher_url="https://data.townofcary.org",
        region_name="Cary, NC",
        region_country_code="us",
    )
    for dist in ld_record["distribution"]:
        ds.add_file(dist["contentUrl"], file_type=dist["encodingFormat"].lower())
    # also present: field names, geographies

    return ds
