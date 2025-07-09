from django.db import models
from django.utils.translation import gettext_lazy as _


class PublisherKind(models.TextChoices):
    GOV_NATIONAL = "gn", _("Government - National")
    GOV_STATE = "gs", _("Government - State")
    GOV_LOCAL = "gl", _("Government - Local")
    NGO = "ng", _("Non-Governmental Organization")
    ACADEMIC = "ac", _("Academic")


class Publisher(models.Model):
    name = models.TextField()
    kind = models.CharField(max_length=2, choices=PublisherKind)
    url = models.URLField()


class TemporalCollection(models.Model):
    """
    Represents a collection of DataSet that approximately represents the
    same data across different time periods.

    Example: Quarterly Traffic Tickets or Annual Geographic Boundaries.
    """
    name = models.TextField()


class DataSet(models.Model):
    """
    Fundamental unit of the catalog, a single data set.

    This will correspond 1:1 to upstream concepts of a dataset,
    typically a release of data with a common metadata.

    TODO: some data sets are static, but some may update periodically
          without creating a new release
    """
    name = models.TextField()
    year = models.IntegerField()
    upload_date_time = models.DateTimeField()
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT)
    temporal_collection = models.ForeignKey(TemporalCollection, on_delete=models.SET_NULL, null=True, blank=True)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2)


class CuratedCollection(models.Model):
    """
    Represents a collection of DataSet that are related in some (non-temporal)
    manner.

    Example: "Midwestern Agriculture" or "Solar Energy"
    """
    name = models.TextField()
    datasets = models.ManyToManyField(DataSet, blank=True, related_name="curated_collections")


class DataSetFile(models.Model):
    """
    A downloadable artifact associated with a dataset.

    Some datasets may consist of multiple related files, and others may
    be offered in multiple formats.
    """
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)
    original_url = models.URLField()
    url = models.URLField()


class IdentifierKind(models.Model):
    """
    A kind of identifier common across data sets.

    Example: FIPS, ISO-3166
    """
    kind = models.TextField()


class Identifier(models.Model):
    """
    An instance of a known identifier of an IdentifierKind.

    Example: 06 (FIPS), DK (ISO)
    """
    identifier_kind = models.ForeignKey(IdentifierKind, on_delete=models.CASCADE)
    identifier = models.TextField()


class Crosswalk(models.Model):
    """
    A relationship between two identifiers.
    """
    primary_identifier = models.ForeignKey(Identifier, on_delete=models.CASCADE)
    secondary_identifier = models.ForeignKey(Identifier, on_delete=models.CASCADE)


# class GeoProjection(?)
