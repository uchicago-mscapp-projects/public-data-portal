from django.contrib import admin
from .models import (
    Publisher,
    Region,
    DataSet,
    DataSetFile,
    IdentifierKind,
    Identifier,
    Crosswalk,
    TemporalCollection,
    CuratedCollection,
)


class PublisherAdmin(admin.ModelAdmin):
    pass


admin.site.register(Publisher, PublisherAdmin)


class DataSetFileInline(admin.TabularInline):
    model = DataSetFile


class RegionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Region, RegionAdmin)


class DataSetAdmin(admin.ModelAdmin):
    fields = [
        "name",
        "description",
        "scraper",
        ("publisher", "region"),
        ("start_date", "end_date"),
        ("created_at", "updated_at"),
        ("source_url", "upstream_id", "upstream_upload_time"),
        "quality_score",
        "temporal_collection",
        "curated_collections",
    ]
    readonly_fields = ("created_at", "updated_at")
    inlines = [
        DataSetFileInline,
    ]


admin.site.register(DataSet, DataSetAdmin)

"""
class DataSetFileAdmin(admin.ModelAdmin):
    pass

admin.site.register(DataSetFile, DataSetFileAdmin)
"""


class IdentifierKindAdmin(admin.ModelAdmin):
    pass


admin.site.register(IdentifierKind, IdentifierKindAdmin)


class IdentifierAdmin(admin.ModelAdmin):
    pass


admin.site.register(Identifier, IdentifierAdmin)


class CrosswalkAdmin(admin.ModelAdmin):
    pass


admin.site.register(Crosswalk, CrosswalkAdmin)


class DataSetInline(admin.TabularInline):
    model = DataSet


class TemporalCollectionAdmin(admin.ModelAdmin):
    inlines = [
        DataSetInline,
    ]


admin.site.register(TemporalCollection, TemporalCollectionAdmin)


class CuratedCollectionAdmin(admin.ModelAdmin):
    pass


admin.site.register(CuratedCollection, CuratedCollectionAdmin)
