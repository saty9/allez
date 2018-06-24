from django.db import models
from .address import country_list
from . import Club


class Competitor(models.Model):
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=15)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True)
    country = models.CharField(max_length=3, choices=country_list, default='GBR')
