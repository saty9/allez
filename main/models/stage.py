from abc import ABC, abstractmethod
from random import random
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.expressions import RawSQL
from . import StageMember
from functools import reduce


class Stage(models.Model):
    POOL = 'POO'
    DE = 'DEL'
    CULL = 'CUL'
    stage_types = ((POOL, "Pool"),
                   (DE, "Direct Elimination"),
                   (CULL, "Cull"))
    next = models.ForeignKey('self', on_delete=models.PROTECT, null=True)
    type = models.CharField(max_length=3, choices=stage_types)
    data = JSONField()
    competition = models.ForeignKey('main.Competition', on_delete=models.CASCADE)
    number = models.IntegerField()

    def ordered_competitors(self):
        if self.type == self.POOL:
            return PoolStage(self).ordered_fencers()


class XStage(ABC):

    @abstractmethod
    def ordered_fencers(self):
        pass

    def compare(self, fencer1, fencer2):
        pass


class PoolStage(XStage):
    V = 0
    TS = 1
    TR = 2
    bouts = 3
    pools = {}

    def __init__(self, stage_object):
        # TODO replace order by after feature is added in django release
        fencers = stage_object.stagemember_set.order_by(RawSQL("data->>%s", (str(StageMember.INDEX_POOL_POSITION),)))
        self.pools = {}
        for index, fencer in enumerate(fencers):
            print(fencer.data)
            pool_number = fencer.data[StageMember.INDEX_POOL_NUMBER]
            if pool_number not in self.pools:
                self.pools[pool_number] = []
            data = {'id': fencer.competitor_id,
                    'points': fencer.data[StageMember.INDEX_POINTS],
                    'victories': fencer.data[StageMember.INDEX_VICTORIES]}
            self.pools[pool_number].append(data)

    def ordered_fencers(self):
        fencers = []
        for pool in self.pools:
            for index, f in enumerate(self.pools[pool]):
                bouts = len(self.pools[pool]) - 1
                v = sum(f['victories'])
                ts = sum(f['points'])
                tr = reduce((lambda x, y: x + y['points'][index]), [0] + self.pools[pool])
                fencers.append(self.Fencer(bouts, v, ts, tr, f['id']))
        fencers.sort(reverse=True)
        return fencers

    class Fencer:
        bouts = 0
        V = 0
        TS = 0
        TR = 0
        win_percentage = 0
        ID = 0  # Entry ID not stage_member ID

        def __init__(self, bouts, v, ts, tr, id):
            self.bouts = bouts
            self.V = v
            self.TS = ts
            self.TR = tr
            self.bouts = bouts
            self.win_percentage = v/bouts
            self.ID = id

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
            elif (self.HS - self.HR) != (other.HS - other.HR):
                return (self.HS - self.HR) < (other.HS - other.HR)
            elif self.HS != other.HS:
                return self.HS < other.HS
            else:
                return bool(random.getrandbits(1))

        def __str__(self):
            return "V:{:.03}, Ind:{}, TS:{}".format(self.win_percentage, self.TS - self.TR, self.TS)

        def __repr__(self):
            if str(self):
                return str(self)
            else:
                "FENCER OBJECT WITH ERROR"
