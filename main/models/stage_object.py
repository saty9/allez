from django.db import models
from . import Competition, Stage


class StageObject(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.PROTECT)
