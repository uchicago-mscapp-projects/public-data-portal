"""
pydantic data models for data collection
"""

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import NamedTuple


class PartialDataset(NamedTuple):
    """
    Instantiated like `PartialDataset("https://example.com", date(2025, 1, 1))`

    Used to pass pages to fetch from `list_datasets()` to `get_dataset_details`
    """

    url: str
    last_updated: date | None


# NOTE: keep sorted & in sync with catalog.models
class FileFormat(str, Enum):
    """
    Used as a constraint to avoid us having "csv" and "comma-separated", etc.

    Feel free to add to this as needed.
    """

    CSV = "csv"
    FGDB = "fgdb/gdb"
    GEOJSON = "geojson"
    JSON = "json"
    KML = "kml"
    OTHER = "other"
    OTHER_GEO = "other-geo"
    PARQUET = "parquet"
    SHP = "shp"
    SQLITE = "sqlite"
    TSV = "tsv"
    XLS = "xls"
    XLSX = "xlsx"
    XML = "xml"


class UpstreamFile(BaseModel):
    """
    A single file associated with a dataset.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    name: str
    file_type: FileFormat
    file_size_mb: int = 0  # often unknown
    url: str


class AltStr(BaseModel):
    """
    Represents a variation on a string.

    (en, "Hello", "")
    (fr, "Bonjour", "")
    (en, "Hey", "informal")
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    value: str
    lang: str
    note: str = ""


class UpstreamDataset(BaseModel):
    """
    This model represents a scraped dataset, fields should
    roughly correspond to catalog.models.DataSet, but some variation
    will be necessary to allow for flexiblity at scrape time.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    # These will be the default name/description.
    #  We should make a choice: are these in English,
    #  or the language of the source?
    name: str
    description: str

    # time uploaded/updated on source
    upstream_upload_time: datetime

    # time range covered by data
    start_date: date | None = None
    end_date: date | None = None

    publisher_name: str
    publisher_url: str | None = ""
    # Deduplication logic would be to favor pubisher_upstream_id if present, otherwise
    # we'll use publisher_name.
    publisher_upstream_id: str = ""

    region_name: str
    region_country_code: str
    subregion: str | None = ""

    source_url: str
    upstream_id: str

    license: str = ""

    identifier_kinds: list[str] = Field(default_factory=list)

    files: list[UpstreamFile] = Field(default_factory=list)

    # These can be used to store variations & translations.
    alternate_names: list[AltStr] = Field(default_factory=list)
    alternate_descriptions: list[AltStr] = Field(default_factory=list)

    # Collect from source as-is, we'll figure out what to do with them during
    # ingestion.
    tags: list[str] = Field(default_factory=list)

    def add_file(self, url: str, file_type: FileFormat, name: str = "", file_size_mb: int = 0):
        if file_type.lower() == "excel":
            file_type = "xls"
        self.files.append(
            UpstreamFile(url=url, file_type=file_type, name=name, file_size_mb=file_size_mb)
        )

    def add_known_identifier(self, kind: str):
        self.identifier_kinds.append(kind)
