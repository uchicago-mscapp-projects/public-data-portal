from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset, PartialDataset
from ingestion.utils import make_request
from time import sleep
import json

"""
Ingestion script for Socrata-based Chicago data portal.
"""

# URL below pulls up 100 dataset records at preferred offset
CATALOG = "https://data.cityofchicago.org/api/catalog/v1?explicitly_hidden=false&limit=100&offset={}&order=page_views_total&published=true&q=&search_context=data.cityofchicago.org&show_unsupported_data_federated_assets=false&tags=&approval_status=approved&audience=public"
# url for "download" purposes
ODATA_URL = "https://data.cityofchicago.org/api/odata/v4/{}"

# ids that are known to have errors
KNOWN_BAD = ("uwhj-p95a", "6mep-ry2s")


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
        # currently only City's terms or empty field

        tags = ds["classification"].get("domain_category", "")

        # create list w either domain_category or empty list
        if tags:
            tags = list(tags)
        else:
            tags = []

        # extend tags list with domain_tags if available
        if ds["classification"].get("domain_tags", ""):
            tags.extend(ds["classification"]["domain_tags"])

        uds = UpstreamDataset(
            name=rs["name"],
            description=rs["description"],
            upstream_upload_time=parse_date(rs["updatedAt"]),
            # as far as I can tell, cannot be scraped from catalog or portal html
            # # time range covered by data
            # start_date: date | None = None
            # end_date: date | None = None
            publisher_name=rs["attribution"] or "Chicago",
            publisher_url=rs["attribution_link"],
            publisher_upstream_id=rs["id"],
            region_name="Chicago, IL",
            region_country_code="us",
            source_url=ds["permalink"],
            upstream_id=rs["id"],
            license=license,
            tags=tags,
        )
        # check if odata link exists, use for download
        odata = ODATA_URL.format(uds.upstream_id)
        if uds.upstream_id in KNOWN_BAD:
            continue
        resp = make_request(odata)
        if resp.status_code == 200:
            download_url = odata
        # otherwise just link to portal page
        else:
            download_url = ds["link"]
        uds.add_file(url=download_url, file_type="csv")
        upstream_lst.append(uds)

        return upstream_lst


def get_full_datasets():
    """handles catalog pagination to return complete list of datasets"""
    offset = 0
    url = CATALOG.format(str(offset))
    resp = make_request(url)

    cat = json.loads(resp.text)
    n_results = cat["resultSetSize"]
    upstream_lst = []

    # first json used offset zero, so loop iterates through *next* offsets
    for offset in range(100, n_results, 100):
        sleep(1)
        updata = extract_updata(cat)
        upstream_lst.extend(updata)

        # loads new page from offset
        url = CATALOG.format(str(offset))
        resp = make_request(url)
        cat = json.loads(resp.text)

    return upstream_lst
