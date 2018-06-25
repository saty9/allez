from abc import ABC, abstractmethod
from random import random
from django.db import models
from . import StageMember, Stage
from functools import reduce


class StageObject(models.Model):
    competition = models.ForeignKey('main.Competition', on_delete=models.CASCADE)
    stage = models.ForeignKey('main.Stage', on_delete=models.PROTECT)

    def ordered_competitors(self):
        if self.stage == Stage.POOL:
            return PoolStage(self).ordered()

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
    pools = {}

    def __init__(self, stage_object):
        fencers = stage_object.stagemember_set
        for index, fencer in enumerate(fencers):
            pool_number = fencer.data[StageMember.INDEX_POOL_NUMBER]
            if pool_number not in self.pools:
                self.pools[pool_number] = []
            data = {'id': fencer,
                    'points': fencer.data[StageMember.INDEX_POINTS],
                    'victories': fencer.data[StageMember.INDEX_VICTORIES]}
            self.pools[pool_number].append(data)

    def ordered_fencers(self):
        fencers = []
        for pool in self.pools:
            for index, f in enumerate(pool):
                data = {
                    self.V: sum(f['victories']),
                    self.TS: sum(f['points']),
                    self.TR: reduce((lambda x, y: x['points'][index] + y), pool, 0)}
                fencers.append(data)

    def compare(self, fencer1, fencer2):
        if fencer1[self.V] != fencer2[self.V]:
            return fencer1[self.V] < fencer2[self.V]
        elif (fencer1[self.HS] - fencer1[self.HR]) != (fencer2[self.HS] - fencer2[self.HR]):
            return (fencer1[self.HS] - fencer1[self.HR]) < (fencer2[self.HS] - fencer2[self.HR])
        elif fencer1[self.HS] != fencer2[self.HS]:
            return fencer1[self.HS] < fencer2[self.HS]
        else:
            bool(random.getrandbits(1))
