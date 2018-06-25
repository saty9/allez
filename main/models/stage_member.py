from django.db import models
from django.contrib.postgres.fields import JSONField


class StageMember(models.Model):
    INDEX_POOL_NUMBER = 0
    competitor = models.ForeignKey('main.Competitor', on_delete=models.PROTECT)
    stage_object = models.ForeignKey('main.StageObject', on_delete=models.CASCADE)
    data = JSONField()
