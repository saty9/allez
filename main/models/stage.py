from abc import ABC, abstractmethod
from random import random
from django.contrib.postgres.fields import JSONField
from django.db import models
from .pool_bout import PoolBout


class Stage(models.Model):
    POOL = 'POO'
    DE = 'DEL'
    CULL = 'CUL'
    stage_types = ((POOL, "Pool"),
                   (DE, "Direct Elimination"),
                   (CULL, "Cull"))
    NOT_STARTED = 'STD'
    READY = 'RDY'
    STARTED = 'GO'
    FINISHED = 'FIN'
    LOCKED = 'LCK'
    states = ((NOT_STARTED, "Not Started"),
              (READY, "Ready to Start"),
              (STARTED, "Running"),
              (FINISHED, "Finished"),
              (LOCKED, "Finished and Confirmed"))
    type = models.CharField(max_length=3, choices=stage_types)
    state = models.CharField(max_length=3, choices=states, default=NOT_STARTED)
    data = JSONField()
    competition = models.ForeignKey('main.Competition', on_delete=models.CASCADE)
    number = models.IntegerField()

    def ordered_competitors(self):
        if self.type == self.POOL:
            return PoolStage(self).ordered_fencers()
        elif self.type == self.CULL:
            lst2 = None  # fencers who survived the cull
            lst1 = None  # previous stages ordered fencer
            temp = set(lst2)
            lst3 = [value for value in lst1 if value in temp]
            return lst3

    class Meta:
        unique_together = ('number', 'competition')


class XStage(ABC):

    @abstractmethod
    def ordered_fencers(self):
        pass

    def compare(self, fencer1, fencer2):
        pass


class PoolStage(XStage):
    stage_object = None

    def __init__(self, stage_object: Stage):
        self.stage_object = stage_object

    def ordered_fencers(self):
        fencers = []
        for index, p in enumerate(self.stage_object.pool_set.all()):
            for f in p.poolentry_set.all():
                bouts_a = PoolBout.objects.filter(fencerA=f)
                bouts_b = PoolBout.objects.filter(fencerB=f)
                b = bouts_a.count()
                v = bouts_a.filter(victoryA=True).count()
                ts = bouts_a.aggregate(models.Sum('scoreA'))['scoreA__sum']
                tr = bouts_b.aggregate(models.Sum('scoreA'))['scoreA__sum']
                fencers.append(self.Fencer(b, v, ts, tr, f.entry_id))
        fencers.sort(reverse=True)
        return fencers

    class Fencer:
        bouts = 0
        V = 0
        TS = 0
        TR = 0
        win_percentage = 0
        ID = 0

        def __init__(self, bouts, v, ts, tr, ID):
            self.bouts = bouts
            self.V = v
            self.TS = ts
            self.TR = tr
            self.bouts = bouts
            self.win_percentage = v/bouts
            self.ID = ID

        def __add__(self, other):
            if self.ID == other.ID:
                return self.Fencer(self.bouts + other.bouts,
                                   self.V + other.V,
                                   self.TS + other.TS,
                                   self.TR + other.TR,
                                   self.ID)
            else:
                ArithmeticError('cant add different fencers results')

        def __lt__(self, other):
            if self.win_percentage != other.win_percentage:
                return self.win_percentage < other.win_percentage
            elif self.ind() != other.ind():
                return self.ind() < other.ind()
            elif self.TS != other.TS:
                return self.TS < other.TS
            else:
                return bool(random.getrandbits(1))

        def __str__(self):
            return "V:{:.03}, Ind:{}, TS:{}".format(self.win_percentage, self.ind(), self.TS)

        def __repr__(self):
            if str(self):
                return str(self)
            else:
                "FENCER OBJECT WITH ERROR"

        def ind(self):
            return self.TS - self.TR
