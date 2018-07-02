from django.db import models


class Entry(models.Model):
    class Meta:
        unique_together = (('competition', 'competitor'),)

    competition = models.ForeignKey('main.Competition', on_delete=models.CASCADE)
    competitor = models.ForeignKey('main.Competitor', on_delete=models.PROTECT)
