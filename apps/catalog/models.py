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


class DataSet(models.Model):
    """
    Fundamental unit of the catalog, a single data set.

    This will correspond 1:1 to upstream concepts of a dataset,
    typically a release of data with a common metadata.

    TODO: some data sets are static, but some may update periodically
          without creating a new release
    """

class DataSetFile(models.Model):
    """
    A downloadable artifact associated with a dataset.

    Some datasets may consist of multiple related files, and others may
    be offered in multiple formats.
    """


    
class IdentifierKind(models.Model):
    """
    A kind of identifier common across data sets.

    Example: FIPS, ISO-3166
    """


class Identifier(models.Model):
    """
    An instance of a known identifier of an IdentifierKind.

    Example: 06 (FIPS), DK (ISO)
    """


class Crosswalk(models.Model):
    """
    A relationship between two identifiers.
    """


# class GeoProjection(?)


class TemporalCollection(models.Model):
    """
    Represents a collection of DataSet that approximately represents the
    same data across different time periods.

    Example: Quarterly Traffic Tickets or Annual Geographic Boundaries.
    """


class CuratedCollection(models.Model):
    """
    Represents a collection of DataSet that are related in some (non-temporal)
    manner.

    Example: "Midwestern Agriculture" or "Solar Energy"
    """
