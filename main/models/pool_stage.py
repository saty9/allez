from django.db import models
from random import getrandbits
from .pool_bout import PoolBout
from .entry import Entry
from main.utils.club_solver import attempt_solve


class PoolStage(models.Model):
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    carry_previous_results = models.BooleanField(default=False)

    def ordered_competitors(self):
        """
        :return: ordered list of entries
        :rtype: list of Entry
        """
        from .stage import Stage
        if self.stage.state in [Stage.READY, Stage.NOT_STARTED] or \
                any(map(lambda x: not x.complete(), self.pool_set.all())):
            raise Stage.NotCompleteError("Stage not finished yet")
        results = self.results()
        results.sort(reverse=True)
        return list(map(lambda x: x.entry, results))

    def start(self, number_of_pools):
        """Generate the given number of pools and add entries to them

        :param int number_of_pools: number of pools to generate
        :return: None
        """
        fencers = self.stage.input()
        pools = [[] for _ in range(number_of_pools)]

        pool_number = 0
        x = 0

        # distribute fencers into pools by seed
        while x < len(fencers):
            while pool_number <= number_of_pools - 1 and x < len(fencers):
                pools[pool_number].append(fencers[x])
                x += 1
                pool_number += 1
            pool_number -= 1
            while pool_number >= 0 and x < len(fencers):
                pools[pool_number].append(fencers[x])
                x += 1
                pool_number -= 1
            pool_number += 1

        attempt_solve(pools)

        # build database entries
        for index, pool in enumerate(pools):
            db_pool = self.pool_set.create(number=index + 1)
            for pool_pos, entry in enumerate(pool):
                db_pool.poolentry_set.create(entry=entry, number=pool_pos + 1)

    def results(self):
        """Get the results for each entry from this stages pools.

        If carry_previous_results is True then it will merge in results from the last round of pools

        If a fencer was in the last set of results but is not in the new one they are dropped from the results

        :return: an unordered list of PoolStage.Fencer's
        :rtype: list of Fencer
        """
        fencers = []
        for index, p in enumerate(self.pool_set.all()):
            excluded = p.poolentry_set.\
                filter(entry__state__in=[Entry.EXCLUDED, Entry.DID_NOT_FINISH, Entry.DID_NOT_START],
                       entry__exited_at_stage=self.stage).all()
            for f in p.poolentry_set.all():
                bouts_a = PoolBout.objects.filter(fencerA=f).exclude(fencerA__in=excluded)
                bouts_b = PoolBout.objects.filter(fencerB=f).exclude(fencerB__in=excluded)
                b = bouts_a.count()
                v = bouts_a.filter(victoryA=True).count()
                ts = bouts_a.aggregate(models.Sum('scoreA'))['scoreA__sum']
                tr = bouts_b.aggregate(models.Sum('scoreA'))['scoreA__sum']
                fencers.append(self.Fencer(b, v, ts, tr, f.entry))
        if self.carry_previous_results:
            previous_stage = self.stage.competition.stage_set.get(number=self.stage.number - 1)
            if previous_stage.type != previous_stage.POOL:
                raise AssertionError("Cannot carry results forward if previous stage was not a pool")
            if not previous_stage.poolstage_set.first():
                raise AssertionError("PoolStage for previous stage missing")

            old_results = previous_stage.poolstage_set.first().results()
            out = []
            for f in fencers:
                found = False
                for o in old_results:
                    if f.entry.id == o.entry.id:
                        found = True
                        out.append(f + o)
                        break
                if not found:
                    out.append(f)
            fencers = out
        return fencers

    class Fencer:
        """Represents a fencers results from a pool stage"""
        bouts = 0
        V = 0
        TS = 0
        TR = 0
        win_percentage = 0
        entry = 0

        def __init__(self, bouts, v, ts, tr, entry):
            """
            :param bouts: number of bouts these results are from
            :param v: number of victories
            :param ts: number of hits scored
            :param tr: number of hits received
            :param entry: entry id"""
            self.bouts = bouts
            self.V = v
            self.TS = ts
            self.TR = tr
            self.bouts = bouts
            self.win_percentage = v/bouts
            self.entry = entry

        def __add__(self, other):
            if self.entry.id == other.entry.id:
                return self.__class__(self.bouts + other.bouts,
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
                return bool(getrandbits(1))

        def __str__(self):
            return "V:{:.03}, Ind:{}, TS:{}".format(self.win_percentage, self.ind(), self.TS)

        def __repr__(self):
            if str(self):
                return str(self)
            else:
                "FENCER OBJECT WITH ERROR"

        def ind(self):
            """get indicator for results"""
            return self.TS - self.TR

