from typing import Generator
from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset, PartialDataset, AltStr
from ingestion.utils import make_request, logger
from urllib.parse import urlparse, parse_qs
import lxml.html
import lxml.etree
import time

LIST_URL = "https://aemint-search-client-funcapp-prod.azurewebsites.net/api/faceted-search?siteName=oecd&interfaceLanguage=en&orderBy=mostRelevant&page={}&pageSize=10&hiddenFacets=oecd-content-types%3Adata%2Fdatasets&hiddenFacets=oecd-languages%3Aen"
DATASET_URL = "https://sdmx.oecd.org/public/rest/dataflow/{}/{}/?references=all"
DOWNLOAD_URL = "https://sdmx.oecd.org/public/rest/data/{},{},/all?dimensionAtObservation=AllDimensions&format=csvfile"
SITE_DOMAIN = "https://www.oecd.org/"

headers = {
    "Accept": "application/xml",  # request XML format
    "User-Agent": "Mozilla/5.0",  # avoid bot detection
}
ns = {
    "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "structure": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}


def retrieve_results_count():
    """
    Retrieve total dataset count.
    Useful for iterating through page numbers in list_datasets().
    """
    resp = make_request(LIST_URL.format(0)).json()
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
    try:
        parsed_url = urlparse(pd.url)
        url_params = parse_qs(parsed_url.query)

        df_id = url_params["df[id]"][0]  # retrieve unique DataSet id from url
        df_ag = url_params["df[ag]"][0]  # retrieve prefix from url

    except KeyError:
        logger.warning("missing required query params", url=pd.url)
        return None

    resp = make_request(DATASET_URL.format(df_ag, df_id), headers=headers)
    root = lxml.etree.fromstring(resp.content)

    header_elem = root.xpath(f'//structure:Dataflow[@id="{df_id}"]', namespaces=ns)[0]
    name_en = header_elem.xpath('.//common:Name[@xml:lang="en"]/text()', namespaces=ns)[0]
    name_fr = header_elem.xpath('.//common:Name[@xml:lang="fr"]/text()', namespaces=ns)[0]

    desc_html_en_lst = header_elem.xpath(
        './/common:Description[@xml:lang="en"]/text()', namespaces=ns
    )
    desc_html_fr_lst = header_elem.xpath(
        './/common:Description[@xml:lang="fr"]/text()', namespaces=ns
    )
    desc_en = ""
    desc_fr = ""
    if len(desc_html_en_lst) > 0:
        # strip html from description
        desc_en = lxml.html.fromstring(desc_html_en_lst[0]).text_content().strip()
    if len(desc_html_fr_lst) > 0:
        # strip html from description
        desc_fr = lxml.html.fromstring(desc_html_fr_lst[0]).text_content().strip()

    tags_en = get_dataset_tags(root)

    ds = UpstreamDataset(
        name=name_en,
        description=desc_en,
        upstream_id=df_id,
        source_url=pd.url,
        upstream_upload_time=pd.last_updated,
        license="https://www.oecd.org/en/about/terms-conditions.html",
        tags=tags_en,
        publisher_name="OECD",
        publisher_url=SITE_DOMAIN,
        publisher_upstream_id=df_id,
        region_name="International",
        region_country_code="XX",
        alternate_names=[AltStr(value=name_fr, lang="fr")],
        alternate_descriptions=[AltStr(value=desc_fr, lang="fr")],
    )
    download_url = DOWNLOAD_URL.format(df_ag, df_id)
    ds.add_file(download_url, file_type="csv")

    time.sleep(5)  # avoid '429 Too Many Requests'

    return ds


def get_dataset_tags(root):
    """
    This method retrieves a list of unique categorisations for a specific dataset.

    Each dataset seems to typically have only one categorisation but can occasionally
    have multiple.
    """
    tags = set()
    categorisations = root.xpath("//structure:Categorisation", namespaces=ns)
    categories = root.xpath("//structure:Category", namespaces=ns)

    for categorisation in categorisations:
        target = categorisation.xpath(".//structure:Target", namespaces=ns)[0]
        ref_id = target.xpath(".//Ref")[0].get("id")
        category_ids = ref_id.split(".")

        for category_id in category_ids:
            for category in categories:  # search for category name in category structure provided
                if category.get("id") == category_id:
                    category_name = category.xpath(
                        './/common:Name[@xml:lang="en"]/text()', namespaces=ns
                    )[0]
                    tags.add(category_name)
                    break

    return list(tags)
