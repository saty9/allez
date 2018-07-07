from django.db import models


class AddCompetitor(models.Model):
    stage = models.ForeignKey('main.AddStage', on_delete=models.CASCADE)
    competitor = models.ForeignKey('main.Competitor', on_delete=models.CASCADE)
    sequence = models.IntegerField()
