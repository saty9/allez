from django.db import models
from django.contrib.postgres.fields import JSONField


class StageMember(models.Model):
    INDEX_POOL_NUMBER = '0'
    INDEX_POINTS = '1'
    INDEX_VICTORIES = '2'
    INDEX_POOL_POSITION = '3'
    competitor = models.ForeignKey('main.Entry', on_delete=models.PROTECT)
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    data = JSONField()
