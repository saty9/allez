from django.db import models


class AddCompetitor(models.Model):
    stage = models.ForeignKey('main.AddStage', on_delete=models.CASCADE)
    entry = models.ForeignKey('main.Entry', on_delete=models.CASCADE)
    sequence = models.IntegerField()
