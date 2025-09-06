from typing import Generator
from dateutil.parser import parse as parse_date
from ingestion.data_models import UpstreamDataset, PartialDataset, AltStr
from ingestion.utils import make_request
import lxml.html
import json
import csv
import io
import re
from functools import reduce

SITE_URL = "https://search.open.canada.ca/opendata/"
CSV_URL = "https://open.canada.ca/data/dataset/c4c5c7f1-bfa6-4ff6-b4a0-c164cb2060f7/resource/312a65c5-d0bc-4445-8a24-95b2690cc62b/download/main.csv"
RECORD_URL = "https://open.canada.ca/data/api/action/package_show?id={}"


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
    ld_json = json.loads(resp.content)
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
        subregion=provinces.get(ld_record["organization"]["name"], ""),
        region_country_code="ca",
    )
    for file in ld_record["resources"]:
        ds.add_file(
            url=file["url"], file_type=handle_file_format(file["format"]), name=file["name"]
        )

    return ds


# handle file formats:
# TO DO: complete list of file formats
def handle_file_format(original_format):
    format = original_format.lower()
    if format in APPROVED_FORMATS:
        return format
    elif format in ["sql", "sql lite"]:
        return "sqlite"
    elif format in OTHER_GEO_FORMATS:
        return "other-geo"
    # elif format in ["docx", "edi", "html", "jpg", "kmz", "pdf", "rdf", "rss", "tiff", "zip"]:
    #    return "other"
    else:
        return "other"


# Short codes used in organization->name for provincial govts (and territories)
ALBERTA = "ab"
BRITISH_COLUMBIA = "bc-cb"
MANITOBA = "mb"
NEW_BRUNSWICK = "nb"
NEWFOUNDLAND_LABRADOR = "nl-tnl"
NORTHWEST_TERRITORIES = "nwt-tno"
NOVA_SCOTIA = "ns-ne"
ONTARIO = "on"
PRINCE_EDWARD = "pei-ipe"
QUEBEC = "qc"
SASKATCHEWAN = "sk"
YUKON = "yk"

# Dictionary of Canadian provinces/territories
provinces = {
    ALBERTA: "Alberta",
    BRITISH_COLUMBIA: "British Columbia",
    MANITOBA: "Manitoba",
    NEW_BRUNSWICK: "New Brunswick",
    NEWFOUNDLAND_LABRADOR: "Newfoundland and Labrador",
    NORTHWEST_TERRITORIES: "Northwest Territories",
    NOVA_SCOTIA: "Nova Scotia",
    ONTARIO: "Ontario",
    PRINCE_EDWARD: "Prince Edward Island",
    QUEBEC: "Québec",
    SASKATCHEWAN: "Saskatchewan",
    YUKON: "Yukon",
}


# scrape file formats
def get_file_formats_from_site():
    resp = make_request(SITE_URL)
    tree = lxml.html.fromstring(resp.content)
    list_item_path = (
        "/html/body/main/div/div[3]/aside/div[2]/details[7]/ul/li[{}]/div/div[1]/label/div/text()"
    )
    file_formats = []
    # approx 75 file formats currently listed on site
    # set range 100 on assumption additions to list are relatively rare
    for i in range(100):
        list_item_raw = tree.xpath(list_item_path.format(i))
        if list_item_raw:
            list_item = list_item_raw[0].strip().split("\xa0\xa0")
            file_formats.append(list_item[0].lower())
    return file_formats


ALL_FILE_FORMATS = get_file_formats_from_site()
APPROVED_FORMATS = [
    "csv",
    "fgdb/gdb",
    "geojson",
    "json",
    "kml",
    "other",
    "other-geo",
    "parquet",
    "shp",
    "sqlite",
    "tsv",
    "xls",
    "xlsx",
    "xml",
]
OTHER_GEO_FORMATS = [
    "ascii grid",
    "esri rest",
    "geopdf",
    "geopackage",
    "geosoftdatabases",
    "geosoftgrids",
    "geotif",
    "gpkg",
    "lyr",
    "mxd",
    "segy",
    "wms",
]
