from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset
from time import sleep
import httpx
import json

"""
Ingestion script for Socrata-based Chicago data portal.
"""

# URL below pulls up 100 dataset records at preferred offset
CATALOG = "https://data.cityofchicago.org/api/catalog/v1?explicitly_hidden=false&limit=100&offset={}&order=page_views_total&published=true&q=&search_context=data.cityofchicago.org&show_unsupported_data_federated_assets=false&tags=&approval_status=approved&audience=public"


# to be pulled from new utils
def make_request(url):
    """ping the catalog url"""
    ping = httpx.get(url)
    ping.raise_for_status()

    return ping


def extract_updata(catalog):
    """takes catalog page of 100 datasets, returns list of upstream datasets"""
    upstream_lst = []

    # create UpstreamDatasets
    for ds in catalog["results"]:
        rs = ds["resource"]

        # currently licenses are all either "see terms" or an empty string
        license = ds["metadata"].get("license", "")

        if license == "See Terms of Use":
            license = "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"
        elif license == "":
            pass
        # included this provision in case they ever add a dataset that isn't
        # the City's terms of use
        else:
            license == "Other"

        tags = ds["classification"].get("domain_category", [])

        if ds["classification"].get("domain_tags", ""):
            tags = [tags].extend(ds["classification"]["domain_tags"])

        uds = UpstreamDataset(
            name=rs["name"],
            description=rs["description"],
            upstream_upload_time=parse_date(rs["updatedAt"]),
            # as far as I can tell, cannot be scraped from catalog or portal html
            # # time range covered by data
            # start_date: date | None = None
            # end_date: date | None = None
            publisher_name=rs["attribution"],
            publisher_url=rs["attribution_link"],
            publisher_upstream_id=rs["id"],
            region_name="Chicago, IL",
            region_country_code="us",
            source_url=ds["permalink"],
            upstream_id=rs["id"],
            license=license,
            ##Authorization issues with various links
            # files= list[UpstreamFile] = Field(default_factory=list),
            tags=tags,
        )
        upstream_lst.append(uds)

        return upstream_lst


def extract_catalog():
    """handles catalog pagination to return complete list of datasets"""
    offset = 0
    url = CATALOG.format(str(offset))
    resp = make_request(url)

    cat = json.loads(resp.text)
    upstream_lst = []

    while cat["results"]:
        sleep(1)
        updata = extract_updata(cat)
        upstream_lst.extend(updata)

        # next page
        url = CATALOG.format(str(offset + 100))
        resp = make_request(url)
        cat = json.loads(resp.text)

    return upstream_lst
