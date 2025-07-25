from typing import Generator
from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset, PartialDataset
import httpx
import lxml.html
import json
import csv
import io

SITE_URL = "https://search.open.canada.ca/opendata/"
CSV_URL = "https://open.canada.ca/data/dataset/c4c5c7f1-bfa6-4ff6-b4a0-c164cb2060f7/resource/312a65c5-d0bc-4445-8a24-95b2690cc62b/download/main.csv"
CSV_URL = "https://opencanada.blob.core.windows.net/opengovprod/resources/312a65c5-d0bc-4445-8a24-95b2690cc62b/main.csv?se=2025-07-25T18%3A09%3A01Z&sp=r&sv=2024-08-04&sr=b&sig=7nYn1wABmJ3Lt3STKBdbe7XkCH6m%2BRAM35Wx0v2wiBk%3D"
RECORD_URL = "https://open.canada.ca/data/en/api/3/action/datastore_search?resource_id={}"
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
        #replace this with a better if-else structure
        try:
            last_updated = parse_date(row["date_modified"])
        except: 
            last_updated = parse_date(row["date_published"])
        yield PartialDataset(
            url=RECORD_URL.format(row["id"]),
            last_updated=last_updated,
        )


def get_dataset_details(pd: PartialDataset) -> UpstreamDataset:
    # parse HTML from request
    resp = make_request(pd.url)
    root = lxml.html.fromstring(resp.content)

    # main dataset info is tucked away in JSON on this attribute
    dataset_schema = root.xpath("//div[@ctx-dataset-schema]/@ctx-dataset-schema")[0]
    # the JSON has improperly escaped data
    dataset_schema = dataset_schema.replace(r"\{", "{").replace(r"\}", "}")
    data = json.loads(dataset_schema)

    # there is an ld+json microformat embedded on the page with additional information
    ld_json = root.xpath("//script[@type='application/ld+json']/text()")[0]
    ld_record = json.loads(ld_json)

    # TODO: if this microformat is used frequently, we could create
    # automatic extraction for it
    #
    print(ld_record)

    ds = UpstreamDataset(
        name=ld_record["name"],
        description=ld_record["description"],
        upstream_id=data["datasetid"],
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
