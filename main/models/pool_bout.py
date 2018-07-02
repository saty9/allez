from django.db import models
from .pool_entry import PoolEntry


class PoolBout(models.Model):
    """Represents 1 side of a bout between 2 fencers"""
    fencerA = models.ForeignKey('main.PoolEntry', on_delete=models.PROTECT, related_name='fencerA_bout_set')
    fencerB = models.ForeignKey('main.PoolEntry', on_delete=models.PROTECT, related_name='fencerB_bout_set')
    scoreA = models.IntegerField()
    victoryA = models.BooleanField()

    @classmethod
    def create(cls, fencer1: PoolEntry, fencer2: PoolEntry, fencer1score: int, fencer2score: int, fencer1victory: bool):
        """creates a pair of PoolBouts in the database"""
        assert fencer1.pool == fencer2.pool, "Fencers are from different pools"
        if fencer1victory:
            assert (fencer1score >= fencer2score), "{} has less points than {} but won".format(fencer1, fencer2)
        else:
            assert (fencer1score <= fencer2score), "{} has less points than {} but won".format(fencer2, fencer1)
        bout_a = cls(fencerA=fencer1, fencerB=fencer2, scoreA=fencer1score, victoryA=fencer1victory)
        bout_b = cls(fencerA=fencer2, fencerB=fencer1, scoreA=fencer2score, victoryA=not fencer1victory)
        bout_a.save()
        bout_b.save()

