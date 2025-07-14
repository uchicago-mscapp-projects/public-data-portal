from django.contrib import admin
from .models import Publisher, DataSet, DataSetFile, IdentifierKind, Identifier, Crosswalk, TemporalCollection, CuratedCollection

admin.site.register(Publisher, DataSet, DataSetFile, IdentifierKind, Identifier, Crosswalk, TemporalCollection, CuratedCollection)