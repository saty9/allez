from django.db import models
from django.contrib.postgres.fields import JSONField
from . import Competitor, StageObject


class StageMember(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.PROTECT)
    stage_object = models.ForeignKey(StageObject, on_delete=models.CASCADE)
    data = JSONField()
