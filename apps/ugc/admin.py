from django.contrib import admin
from .models import Comment, Project, ProjectDataSet

admin.site.register(Comment, Project, ProjectDataSet)