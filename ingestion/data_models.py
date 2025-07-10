"""
pydantic data models for data collection
"""

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from datetime import date

class FileFormat(str, Enum):
    """
    Used as a constraint to avoid us having "csv" and "comma-separated", etc.

    Feel free to add to this as needed.
    """
    CSV = "CSV"
    JSON = "JSON"
    XML = "XML"
    EXCEL = "Excel"
    PDF = "PDF"
    SHAPEFILE = "Shapefile"
    GEOJSON = "GeoJSON"
    KML = "KML"
    OTHER = "Other"



class UpstreamFile(BaseModel):
    """
    A single file associated with a dataset.
    """
    name: str
    type: FileFormat
    size_bytes: int = 0 # often unknown
    url: str


class AltStr(BaseModel):
    """
    Represents a variation on a string.

    (en, "Hello", "")
    (fr, "Bonjour", "")
    (en, "Hey", "informal")
    """

    value: str
    lang: str
    note: str = ""


class UpstreamDataset(BaseModel):
    # required fields ##################

    source_url: str
    upstream_id: str
    pub_date: date
    update_date: date
    publisher_name: str

    # These will be the default name/description.
    #  We should make a choice: are these in English,
    #  or the language of the source?
    name: str
    desscription: str

    # optional fields ##################

    license: str = ""

    files: list[UpstreamFile] = Field(default_factory=list)

    # These can be used to store variations & translations.
    alternate_names: list[AltStr] = Field(default_factory=list)
    alternate_descriptoins: list[AltStr] = Field(default_factory=list)

    # Collect from source as-is, we'll figure out what to do with them during
    # ingestion.
    tags: list[str] = Field(default_factory=list)

    # Deduplication logic would be to favor pubisher_upstream_id if present, otherwise
    # we'll use publisher_name.
    publisher_upstream_id: str = ""
