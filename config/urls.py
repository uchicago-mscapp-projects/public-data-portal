from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from apps.catalog import views as cat_views

urlpatterns = [
    path("djadmin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    # maps the default "/" URL to our index page
    path("", cat_views.index),
    path("about/", cat_views.about),
    path("random/", cat_views.random_dataset),
    path("dataset/<int:dataset_id>/", cat_views.dataset_detail, name="dataset-detail"),
]

if settings.DEBUG and not settings.IS_TESTING:
    urlpatterns += debug_toolbar_urls()
