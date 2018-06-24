from django.db import models
from .address import Address


class Organisation(models.Model):
    name = models.CharField(max_length=200)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    email = models.EmailField()
    contactNumber = models.CharField(max_length=15)

