from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset
import httpx
import json

"""
Ingestion script for Socrata-based Chicago data portal.
"""

CATALOG = "https://data.cityofchicago.org/api/catalog/v1?explicitly_hidden=false&limit=100&offset={}&order=page_views_total&published=true&q=&search_context=data.cityofchicago.org&show_unsupported_data_federated_assets=false&tags=&approval_status=approved&audience=public"

#to be pulled from new utils
def make_request(url):
    '''ping the catalog url'''
    ping = httpx.get(url)
    ping.raise_for_status()

    return ping

def extract_updata(url):
    '''returns list of upstream datasets using catalog'''
    resp = make_request(CATALOG)
    #load from json
    cat = json.loads(resp.text)
    upstream_lst = []

    #collect details
    for ds in cat["results"]:
        rs = ds["resource"]

        #currently licenses are all either "see terms" or an empty string
        license = ds["metadata"].get("license", "")

        if license == "See Terms of Use":
            license = "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"
        elif license == "":
            pass
        #included this provision in case they ever add a dataset that isn't
        #the City's terms of use
        else:
            license == "Other"

        uds = UpstreamDataset(
            description = rs["description"],

            upstream_upload_time = parse_date(rs["updatedAt"]),

            #as far as I can tell, cannot be scraped from catalog or portal html
            # # time range covered by data
            # start_date: date | None = None
            # end_date: date | None = None

            publisher_name = rs["attribution"],
            publisher_url = rs["attribution_link"],
            publisher_upstream_id = rs["id"],

            region_name = "Chicago, IL",
            region_country_code = "us",

            source_url = ds["permalink"],
            upstream_id = rs["id"],

            license = license,

            ##Authorization issues with various links
            #files= list[UpstreamFile] = Field(default_factory=list),

            tags = ds["classification"].get("domain_tags", []).append(
                ds["classification"]["domain_category"])
            )
        upstream_lst.append(uds)

        return upstream_lst

def extract_catalog():
    '''handles pagination'''
    offset = 0
    url = CATALOG.format(str(offset))
    resp = make_request(CATALOG)
    #load from json
    cat = json.loads(resp.text)
    upstream_lst = []

    while cat["results"]:
        extract_updata(cat)

