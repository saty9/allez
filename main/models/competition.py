from django.db import models
from . import Organisation, Stage


class Competition(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    date = models.DateField()
    name = models.TextField()
