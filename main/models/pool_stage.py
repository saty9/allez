from django.db import models
from random import random
from .pool_bout import PoolBout


class PoolStage(models.Model):
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    carry_results = models.BooleanField(default=False)

    def ordered_competitors(self):
        results = self.results()
        results.sort(reverse=True)
        return list(map(lambda x: x.entry, results))

    def results(self):
        fencers = []
        for index, p in enumerate(self.pool_set.all()):
            for f in p.poolentry_set.all():
                bouts_a = PoolBout.objects.filter(fencerA=f)
                bouts_b = PoolBout.objects.filter(fencerB=f)
                b = bouts_a.count()
                v = bouts_a.filter(victoryA=True).count()
                ts = bouts_a.aggregate(models.Sum('scoreA'))['scoreA__sum']
                tr = bouts_b.aggregate(models.Sum('scoreA'))['scoreA__sum']
                fencers.append(self.Fencer(b, v, ts, tr, f.entry))
        return fencers

    class Fencer:
        bouts = 0
        V = 0
        TS = 0
        TR = 0
        win_percentage = 0
        entry = 0

        def __init__(self, bouts, v, ts, tr, entry):
            self.bouts = bouts
            self.V = v
            self.TS = ts
            self.TR = tr
            self.bouts = bouts
            self.win_percentage = v/bouts
            self.entry = entry

        def __add__(self, other):
            if self.entry.id == other.entry.id:
                return self.Fencer(self.bouts + other.bouts,
                                   self.V + other.V,
                                   self.TS + other.TS,
                                   self.TR + other.TR,
                                   self.entry)
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
