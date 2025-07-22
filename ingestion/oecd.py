from typing import Generator
from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset, PartialDataset
from urllib.parse import urlparse, parse_qs
import httpx
import lxml.html
import json
import csv
import io

INITIAL_LIST_URL = "https://www.oecd.org/en/data/datasets.html?orderBy=mostRelevant&page=0"
SITE_DOMAIN = "https://www.oecd.org/"


def make_request(url):
    """
    Make an HTTP request with logging & error checking.
    """
    resp = httpx.get(url)
    resp.raise_for_status()
    return resp


def list_datasets(max_pages):
    """
    """
    page = 0
    curr_link = INITIAL_LIST_URL
    pd_list = []
    

    # iterate through pages until we've hit max page limit or there are no next links left
    while page < max_pages and curr_link is not None:
        pd_list = pd_list + list_datasets_page(curr_link)

        curr_link = get_next_page_url(
            curr_link
        )  # use helper method for link to next page (if exists)

        page += 1
    
    return pd_list


def list_datasets_page(page_url) -> list[PartialDataset]:
    
    page_pds = []

    resp = make_request(page_url)
    root = lxml.html.fromstring(resp.text)

    search_results = root.get_element_by_id("oecd-faceted-search-results")
    dataset_rows = search_results.xpath(".//li[@class='cmp-list__item']")

    for row in dataset_rows:
        #extract link
        title_elem = row.xpath(".//div[@class='search-result-list-item__title']")[0]
        url = title_elem.cssselect("a")[0].get("href")

        #extract date
        date_str = row.xpath(".//span[@class='search-result-list-item__date']/text()")[0]

        page_pds.append(
            PartialDataset(
                url=url,
                last_updated=parse_date(date_str)
            )
        )
    
    return page_pds


def get_next_page_url(page_url):
    
    resp = make_request(page_url)
    root = lxml.html.fromstring(resp.text)

    # extract hyperlink tag containing pagination link
    pagination_tag_li = root.xpath("//li[@class='cmp-pagination__next']")[0]	
    
    pagination_url = None

    if pagination_tag_li:  # check that next page pagination link exists
        rel_url = pagination_tag_li.xpath(".//a[@aria-label='Next page']")[0].get("href")  # pull link from next page tag
        pagination_url = SITE_DOMAIN + rel_url  # pass in scraped relative url with current url to construct absolute url

    return pagination_url


def get_dataset_details(pd: PartialDataset) -> UpstreamDataset:
    #xpath('//*[@data-testid="submit-button"]')
    
    resp = make_request(pd.url)
    root = lxml.html.fromstring(resp.text)

    overview_elem = root.get_element_by_id("id_overview_component")
    api_query_elem = root.xpath('//*[@data-testid="apiqueries-test-id"]')

    name = overview_elem.xpath(".//h1/text()")

    description_div = overview_elem.xpath(".//div")[0]
    description = description_div.xpath(".//p")[0].text_content().strip()

    parsed_url = urlparse(pd.url)
    url_params = parse_qs(parsed_url.query)
    upstream_id = url_params.get("df[id]", [None])[0]

    source_url = api_query_elem.xpath(".//textarea[@aria-label='Data query']/text()")[0]



# list_datasets() (compiles list of all datasets in OECD with partial dataset for each dataset present)
#       while page_url is valid / not at limit
#           pd_list.append(list_datasets_page(page_url))
#           page_url = get_next_page_url
#
# list_datasets_page(page_url) (compiles list of datasets on specific page with pd for each dataset)
#       retrieve HTML for page_url, iterate through all dataset <li> compiling partial dataset for each
#
# get_next_page_url(page_url) (retrieves url for next page if any)

# get_dataset_details(PartialDataset) ()
#
#
#
#

    