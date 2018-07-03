from django.db import models


class PoolEntry(models.Model):
    """Represents a fencer in a pool"""
    entry = models.ForeignKey('main.Entry', on_delete=models.PROTECT)
    pool = models.ForeignKey('main.Pool', on_delete=models.CASCADE)
    number = models.IntegerField()

    class Meta:
        unique_together = (('pool', 'number'),
                           ('entry', 'pool'))

    def ts(self):
        return self.fencerA_bout_set.aggregate(models.Sum('scoreA'))['scoreA__sum']

    def tr(self):
        return self.fencerB_bout_set.aggregate(models.Sum('scoreA'))['scoreA__sum']

    def victories(self):
        return self.fencerA_bout_set.filter(victoryA=True).count()
