from django.db import models


class DeSeed(models.Model):
    entry = models.ForeignKey('main.Entry', on_delete=models.CASCADE)
    de = models.ForeignKey('main.De', on_delete=models.CASCADE)
    seed = models.IntegerField()
