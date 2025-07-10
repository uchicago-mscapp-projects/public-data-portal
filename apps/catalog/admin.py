from django.contrib import admin
from .models import Publisher, DataSet, DataSetFile, IdentifierKind, Identifier, Crosswalk, TemporalCollection, CuratedCollection

# Register your models here.

admin.site.register(Publisher, DataSet, DataSetFile, IdentifierKind, Identifier, Crosswalk, TemporalCollection, CuratedCollection)