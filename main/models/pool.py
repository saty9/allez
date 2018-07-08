from django.db import models


class Pool(models.Model):
    """Represents a single pool in a stage"""
    stage = models.ForeignKey('main.PoolStage', on_delete=models.PROTECT)
    number = models.IntegerField()
    referee = models.ForeignKey('main.Referee', on_delete=models.PROTECT, null=True, default=None)

    def complete(self):
        """returns whether all bouts in this pool have been fought"""
        victories = 0
        expected = 0
        add = 0
        for p_entry in self.poolentry_set.all():
            victories += p_entry.victories()
            expected += add
            add += 1
        return victories == expected

    def bout_order(self):
        """returns a string indicating order fencers should fight each other"""
        # TODO add different behaviour if fencers from the same team are in a pool
        p_of_12 = ("1-2 7-8 4-5 10-11 2-3 8-9 5-6 11-12 3-1 9-7 6-4 12-10 2-5 8-11 1-4 7-10 5-3 11-9 1-6 7-12 4-2 "
                   "10-8 3-6 9-12 5-1 11-7 3-4 9-10 6-2 12-8 1-7 3-9 10-4 8-2 5-11 12-6 1-8 10-1 11-2 12-3 4-7 8-5 "
                   "9-2 3-10 4-11 12-5 6-7 9-1 2-10 11-3 4-12 7-5 6-8 6-9 11-1 2-12 7-3 9-5 6-10 12-1 2-7 4-9 4-8 8-3 "
                   "10-5 6-11")
        p_of_11 = ("8-9 5-6 9-7 6-4 2-5 8-11 1-4 7-10 5-3 11-9 9-10 6-2 1-7 3-9 10-4 8-2 5-11 1-8 9-2 8-5 6-9 11-1 7-3 "
                   "4-8 1-2 7-8 4-5 10-11 2-3 1-6 4-2 10-8 3-6 5-1 11-7 3-4 3-10 4-11 6-7 9-1 2-10 11-3 7-5 9-5 8-3 "
                   "4-9 6-10 2-7 3-1 6-8 10-1 11-2 4-7 10-5 6-11")
        p_of_10 = ("8-6 4-5 9-10 2-3 7-8 5-1 10-6 4-2 9-7 5-3 10-8 9-3 2-6 5-8 1-4 6-9 2-5 7-10 3-1 1-2 6-7 3-4 8-9 "
                   "5-10 1-6 2-7 3-8 4-9 6-5 10-2 8-1 7-4 4-10 1-9 3-7 8-2 6-4 9-5 10-3 7-1 4-8 2-9 3-6 5-7 1-10")
        p_of_9 = ("1-9 2-8 3-7 4-6 1-5 2-9 8-3 7-4 6-5 1-2 9-3 8-4 7-5 6-1 3-2 9-4 5-8 7-6 3-1 2-4 5-9 8-6 7-1 4-3 5-2 "
                  "6-9 8-7 4-1 5-3 6-2 9-7 1-8 4-5 3-6 2-7 9-8")
        p_of_8 = ("2-3 1-5 7-4 6-8 1-2 3-4 5-6 8-7 4-1 5-2 8-3 6-7 4-2 8-1 7-5 3-6 2-8 7-4 6-1 3-7 4-8 2-6 3-5 1-7 4-6 "
                  "8-5 7-2 1-3")
        p_of_7 = "1-4 2-5 3-6 7-1 5-4 2-3 6-7 5-1 4-3 6-2 5-7 3-1 4-8 7-2 3-5 1-6 2-4 7-3 6-5 1-2 4-7"
        p_of_6 = "1-2 4-5 2-3 5-6 3-1 6-4 2-5 1-4 5-3 1-6 4-2 3-6 5-1 3-4 6-2"
        p_of_5 = "1-2 3-4 5-1 2-3 5-4 1-3 2-5 4-1 3-5 4-2"
        p_of_4 = "1-4 2-3 1-3 2-4 3-4 1-2"
        p_of_3 = "1-2 2-3 3-1"
        switch = {
            12: p_of_12,
            11: p_of_11,
            10: p_of_10,
            9: p_of_9,
            8: p_of_8,
            7: p_of_7,
            6: p_of_6,
            5: p_of_5,
            4: p_of_4,
            3: p_of_3,
        }
        return switch.get(self.poolentry_set.count(), "Unexpected pool size")
