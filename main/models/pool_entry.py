from django.db import models


class PoolEntry(models.Model):
    """Represents a fencer in a pool"""
    fencer = models.ForeignKey('main.Entry', on_delete=models.PROTECT)
    pool = models.ForeignKey('main.Pool', on_delete=models.CASCADE)
    number = models.IntegerField()

    class Meta:
        unique_together = (('pool', 'number'),
                           ('fencer', 'pool'))
