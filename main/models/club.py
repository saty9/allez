from django.db import models
from . import Address


class Club(models.Model):
    name = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    @staticmethod
    def simplify_name(name):
        junk = [' fencing',
                ' club',
                ' fc',
                'salle ']
        name = name.lower()
        for j in junk:
            name = name.replace(j, '')
        return name

