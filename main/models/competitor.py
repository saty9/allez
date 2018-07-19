from django.db import models
from .address import country_list
from . import Club


class Competitor(models.Model):
    name = models.CharField(max_length=100)
    organisation = models.ForeignKey('main.Organisation', on_delete=models.CASCADE)
    license_number = models.CharField(max_length=15)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True)
