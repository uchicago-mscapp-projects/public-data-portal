from typing import Generator
from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset, PartialDataset
from urllib.parse import urlparse, parse_qs
import httpx
import lxml.html
import lxml.etree
import time

INITIAL_URL = "https://aemint-search-client-funcapp-prod.azurewebsites.net/api/faceted-search?siteName=oecd&interfaceLanguage=en&orderBy=mostRelevant&pageSize=10&hiddenFacets=oecd-content-types%3Adata%2Fdatasets&hiddenFacets=oecd-languages%3Aen"
LIST_URL = "https://aemint-search-client-funcapp-prod.azurewebsites.net/api/faceted-search?siteName=oecd&interfaceLanguage=en&orderBy=mostRelevant&page={}&pageSize=10&hiddenFacets=oecd-content-types%3Adata%2Fdatasets&hiddenFacets=oecd-languages%3Aen"
DATASET_URL = "https://sdmx.oecd.org/public/rest/dataflow/{}/{}/?references=all"
DOWNLOAD_URL = "https://sdmx.oecd.org/public/rest/data/{},{},/all?dimensionAtObservation=AllDimensions&format=csvfile"
SITE_DOMAIN = "https://www.oecd.org/"

ns = {
    "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "structure": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"
}


def make_request(url):
    """
    Make an HTTP request with logging & error checking.
    """
    resp = httpx.get(url)
    resp.raise_for_status()
    return resp


def retrieve_results_count():
    """
    Retrieve total dataset count. 
    Useful for iterating through page numbers in list_datasets().
    """
    resp = make_request(INITIAL_URL).json()
    count = int(resp["total"])
    return count


def list_datasets() -> Generator[PartialDataset, None, None]:
    """
    This method can either return a list or `yield` individual
    items as they're found.

    The version below demonstrates yielding items, but
    """
    page_count = retrieve_results_count() // 10
    for i in range(page_count + 1):
        data = make_request(LIST_URL.format(i)).json()
        for row in data["results"]:
            yield PartialDataset(
                url=row["url"],
                last_updated=parse_date(row["publicationDateTime"]),
            )


def get_dataset_details(pd: PartialDataset) -> UpstreamDataset:
    parsed_url = urlparse(pd.url)
    url_params = parse_qs(parsed_url.query)

    df_id = url_params.get('df[id]', [None])[0] # retrieve unique DataSet id from url
    df_ag = url_params.get('df[ag]', [None])[0] # retrieve prefix from url

    if None in (df_id, df_ag):
        return None
    
    resp = make_request(DATASET_URL.format(df_ag, df_id))
    root = lxml.etree.fromstring(resp.content)

    header_elem = root.xpath(f'//structure:Dataflow[@id="{df_id}"]', namespaces=ns)[0]
    name_en = header_elem.xpath('.//common:Name[@xml:lang="en"]/text()', namespaces=ns)[0]
    desc_html_en = header_elem.xpath('.//common:Description[@xml:lang="en"]/text()', namespaces=ns)[0]
    desc_en = ""
    if desc_html_en is not None:
        # strip html from description
        desc_en = lxml.html.fromstring(desc_html_en).text_content().strip()
    tags_en = get_dataset_tags(root)

    ds = UpstreamDataset(
        name=name_en,
        description=desc_en,
        upstream_id=df_id,
        source_url=pd.url,
        upstream_upload_time=pd.last_updated,
        license="", # difficulty finding
        tags=tags_en,
        publisher_name="OECD",
        publisher_url=SITE_DOMAIN,
        publisher_upstream_id=df_id,
        region_name="", # lets talk -> multiple (many) regions per dataset
        region_country_code="",
    )
    download_url = DOWNLOAD_URL.format(df_ag, df_id)
    ds.add_file(download_url, file_type="csv")
    # also present: record frequency, time period, countries referenced
    
    time.sleep(5) # avoid '429 Too Many Requests'

    return ds


def get_dataset_tags(root):
    """
    This method retrieves a list of unique categorisations for a specific dataset.

    Each dataset seems to typically have only one categorisation but can occasionally
    have multiple.
    """
    tags = set()
    categorisations = root.xpath('//structure:Categorisation', namespaces=ns)
    categories = root.xpath('//structure:Category', namespaces=ns)

    for categorisation in categorisations:
        target = categorisation.xpath('.//structure:Target', namespaces=ns)[0]
        ref_id = target.xpath('.//Ref')[0].get("id")
        category_ids = ref_id.split(".")
        category_id = category_ids[-1] # only retrieve lowest / most specific categorisation

        for category in categories: # search for category name in category structure provided
            if category.get("id") == category_id:
                category_name = category.xpath('.//common:Name[@xml:lang="en"]/text()', namespaces=ns)[0]
                tags.add(category_name)
                break
    
    return list(tags)