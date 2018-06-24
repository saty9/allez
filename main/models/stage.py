from django.db import models


class Stage(models.Model):
    stage_types = ()
    next = models.ForeignKey('self', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=stage_types)
