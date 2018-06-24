from django.db import models
from . import Competition, Competitor


class Entry(models.Model):
    class Meta:
        unique_together = (('competition', 'competitor'),)

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    competitor = models.ForeignKey(Competitor, on_delete=models.PROTECT)
