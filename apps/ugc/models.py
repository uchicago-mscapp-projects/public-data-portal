from django.db import models
from apps.accounts.models import User
from catalog.models import DataSet

# class History(models.Model):?

# consistent names for updated/created time
class Comment(models.Model):
    """
    A comment or note left by a user on a dataset to be viewed by other users.

    Note: We talked about pulling comments from all datasets in a temporal collection to show alongside that collection.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="comments")
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    # like/popularity metric?

class Project(models.Model):
    """
    An object created by a user to save datasets relevant to a particular project in one place.
    """
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    created_time = models.DateTimeField(auto_now_add=True)

class ProjectDataSet(models.Model):
    """
    An object to capture the association of a dataset with a project. 

    A lot of project related functionality will live in here.
    """
    project = models.ForeignKey(Project, related_name="datasets")
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name="projects")
    # ordering ?
    created_time = models.DateTimeField(auto_now_add=True)
    note = models.TextField()
