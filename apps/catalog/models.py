from django.db import models
from django.utils.translation import gettext_lazy as _


class PublisherKind(models.TextChoices):
    GOV_NATIONAL = "gn", _("Government - National")
    GOV_STATE = "gs", _("Government - State")
    GOV_LOCAL = "gl", _("Government - Local")
    NGO = "ng", _("Non-Governmental Organization")
    ACADEMIC = "ac", _("Academic")

class FileType(models.TextChoices): # these should be kept in sync manually with the file types in ingestion.data_types
    CSV = "csv", _("Comma-Separated Values")
    TSV = "tsv", _("Tab-Separated Values")
    XLS = "xls", _("Excel Spreadsheet")
    SQLITE = "sqlite", _("SQLite Database")
    PARQUET = "parquet", _("Parquet Database")
    JSON = "json", _("JSON Object")
    XML = "xml", _("XML File")
    GEOJSON = "geojson", _("GeoJSON")
    SHP = "shp", _("Shapefile")
    OTHER = "other", _("Other File Type")

class TimePeriod(models.TextChoices):
    DECENNIAL = "dc", _("Decennial") # every 10 years
    QUINQUENNIAL = "qq", _("Quinquennial") # 5 years
    BIENNIAL = "be", _("Biennial") # 2 years
    ANNUAL = "an", _("Annual")
    SEMIANNUAL = "sa", _("Semi-Annual") # 6 months
    QUARTER = "qu", _("Quarterly")
    MONTH = "mo", _("Monthly")
    WEEK = "wk", _("Weekly")
    DAY = "dy", _("Daily")
    OTHER = "ot", _("Other")


class Publisher(models.Model):
    name = models.TextField()
    kind = models.CharField(max_length=2, choices=PublisherKind)
    url = models.URLField()

    def __str__(self):
        return f"{self.name} - {self.kind}"


class Region(models.Model):
    name = models.TextField()
    country_code = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.name} - {self.country_code}"


class TemporalCollection(models.Model):
    """
    Represents a collection of DataSet that approximately represents the
    same data across different time periods.

    Example: Quarterly Traffic Tickets or Annual Geographic Boundaries.
    """
    name = models.TextField()
    period = models.CharField(max_length=2, choices=TimePeriod)

    def __str__(self):
        return f"{self.name} - {self.period}"


class CuratedCollection(models.Model):
    """
    Represents a collection of DataSet that are related in some (non-temporal)
    manner.

    Example: "Midwestern Agriculture" or "Solar Energy"
    """
    name = models.TextField()

    def __str__(self):
        return self.name


class DataSet(models.Model):
    """
    Fundamental unit of the catalog, a single data set.

    This will correspond 1:1 to upstream concepts of a dataset,
    typically a release of data with a common metadata.

    TODO: some data sets are static, but some may update periodically
          without creating a new release
    """
    name = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    upstream_upload_time = models.DateTimeField()
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    temporal_collection = models.ForeignKey(TemporalCollection, on_delete=models.SET_NULL, null=True, blank=True, related_name="datasets")
    curated_collections = models.ManyToManyField(CuratedCollection, null=True, blank=True, related_name="datasets")
    quality_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.start_date}-{self.end_date}"



class DataSetFile(models.Model):
    """
    A downloadable artifact associated with a dataset.

    Some datasets may consist of multiple related files, and others may
    be offered in multiple formats.
    """
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name="files")
    original_url = models.URLField()
    url = models.URLField()
    file_type = models.CharField(choices=FileType)
    file_size_mb = models.IntegerField() # file size in megabytes

    def __str__(self):
        return f"{self.dataset.name} File: {self.file_type}, {self.file_size_mb} MB"


class IdentifierKind(models.Model):
    """
    A kind of identifier common across data sets.

    Example: FIPS, ISO-3166
    """
    kind = models.TextField()

    def __str__(self):
        return self.kind


class Identifier(models.Model):
    """
    An instance of a known identifier of an IdentifierKind.

    Example: 06 (FIPS), DK (ISO)
    """
    identifier_kind = models.ForeignKey(IdentifierKind, on_delete=models.CASCADE)
    identifier = models.TextField()

    def __str__(self):
        return f"{self.identifier} ({self.identifier_kind})"


class Crosswalk(models.Model):
    """
    A relationship between two identifiers.
    """
    primary = models.ForeignKey(Identifier, on_delete=models.CASCADE)
    secondary = models.ForeignKey(Identifier, on_delete=models.CASCADE)

    def __str__(self):
        return f"Crosswalk: {self.primary} - {self.secondary}"


# class GeoProjection(?)
