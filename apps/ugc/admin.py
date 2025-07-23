from django.contrib import admin
from .models import Comment, Project, ProjectDataSet

class CommentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Comment, CommentAdmin)

class ProjectAdmin(admin.ModelAdmin):
    pass

admin.site.register(Project, ProjectAdmin)

class ProjectDataSetAdmin(admin.ModelAdmin):
    pass

admin.site.register(ProjectDataSet, ProjectDataSetAdmin)