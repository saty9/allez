from django.db import models
from . import Organisation, CompetitionStructure


class Competition(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    structure = models.ForeignKey(CompetitionStructure, on_delete=models.PROTECT)
    date = models.DateField()
    name = models.TextField()
