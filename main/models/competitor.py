from django.db import models
from . import Club


class Competitor(models.Model):
    name = models.CharField(max_length=100)
    organisation = models.ForeignKey('main.Organisation', on_delete=models.CASCADE)
    license_number = models.CharField(max_length=15)
