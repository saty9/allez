from django.db import models
from django.contrib.postgres.fields import JSONField


class Stage(models.Model):
    POOL = 'POO'
    DE = 'DEL'
    CULL = 'CUL'
    stage_types = ((POOL, "Pool"),
                   (DE, "Direct Elimination"),
                   (CULL, "Cull"))
    next = models.ForeignKey('self', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=stage_types)
    data = JSONField()
