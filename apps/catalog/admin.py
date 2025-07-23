from django.contrib import admin
from .models import Publisher, DataSet, DataSetFile, IdentifierKind, Identifier, Crosswalk, TemporalCollection, CuratedCollection

class PublisherAdmin(admin.ModelAdmin):
    pass

admin.site.register(Publisher, PublisherAdmin)

class DataSetFileInline(admin.TabularInline):
    model = DataSetFile

class DataSetAdmin(admin.ModelAdmin):
    fields = ["name", "description", ("publisher", "region"), ("created_at", "updated_at"), ("source_url", "upstream_id", "upstream_upload_time")]
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

class TemporalCollectionAdmin(admin.ModelAdmin):
    pass

admin.site.register(TemporalCollection, TemporalCollectionAdmin)

class CuratedCollectionAdmin(admin.ModelAdmin):
    pass

admin.site.register(CuratedCollection, CuratedCollectionAdmin)
