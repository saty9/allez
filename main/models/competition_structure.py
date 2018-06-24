from django.db import models
from . import Stage


class CompetitionStructure(models.Model):
    name = models.CharField(max_length=100)
    stage1 = models.ForeignKey(Stage, on_delete=models.PROTECT)
