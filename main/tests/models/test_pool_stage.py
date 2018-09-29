from ..factories.competition_factory import PreAddedCompetitionOfSize
from django.test import TestCase
from main.models import Stage, PoolStage, Competition, Pool


def make_boring_results(pool):
    entries = pool.poolentry_set.order_by('pk').all()
    for avoid_index, fencer_a in enumerate(entries):
        for fencer_b in entries[avoid_index + 1:]:
            fencer_a.fencerA_bout_set.create(fencerB=fencer_b, scoreA=5, victoryA=True)
            fencer_b.fencerA_bout_set.create(fencerB=fencer_a, scoreA=0, victoryA=False)


class TestPoolStage(TestCase):

    def setUp(self):
        self.competition = PreAddedCompetitionOfSize(entries__num_of_entries=16)  # type: Competition
        self.stage = self.competition.stage_set.create(type=Stage.POOL, number=1)
        self.pool_stage = self.stage.poolstage_set.first()  # type: PoolStage

    def test_function_start_basic(self):
        entries = self.competition.entry_set.all()
        self.assertFalse(self.pool_stage.pool_set.all())
        self.pool_stage.start(1)
        pools = self.pool_stage.pool_set.all()
        self.assertEqual(1, len(pools))
        pool_entries = map(lambda x: x.entry, pools[0].poolentry_set.all())
        self.assertEqual(set(self.competition.entry_set.all()), set(pool_entries))

    def test_function_start_structure(self):
        entries = self.stage.input()
        self.assertFalse(self.pool_stage.pool_set.all())
        self.pool_stage.start(3)
        pools = self.pool_stage.pool_set.all()
        self.assertEqual(3, len(pools))
        expected = [set() for _ in pools]
        x = 0

        while x < len(entries):
            y = 0
            while y < len(pools) and x < len(entries):
                expected[y].add(entries[x])
                y += 1
                x += 1
            y -= 1
            while y >= 0 and x < len(entries):
                expected[y].add(entries[x])
                y -= 1
                x += 1
        pool_entries = list(map(lambda z: set(map(lambda w: w.entry, z.poolentry_set.all())), pools))
        self.assertEqual(expected, pool_entries)

    def test_sub_class_fencer_comparisons(self):
        # Victory Priority
        f1 = PoolStage.Fencer(4, 4, 0, 0, 0)
        f2 = PoolStage.Fencer(4, 3, 20, 0, 1)
        self.assertTrue(f1 > f2, "Victory should take precedence")
        # Victory rate/percentage
        f1 = PoolStage.Fencer(6, 6, 20, 0, 0)
        f2 = PoolStage.Fencer(10, 5, 0, 0, 1)
        self.assertTrue(f1 > f2, "Victory percentage more important than number of victories")
        # Indicator Fallback
        f1 = PoolStage.Fencer(1, 1, 20, 0, 0)
        f2 = PoolStage.Fencer(1, 1, 0, 0, 1)
        self.assertTrue(f1 > f2, "Fallback to indicator")
        # TS fallback fallback
        f1 = PoolStage.Fencer(1, 1, 10, 5, 0)
        f2 = PoolStage.Fencer(1, 1, 5, 0, 1)
        self.assertTrue(f1 > f2, "Fallback to ts")
        # random 3rd fallback
        f1 = PoolStage.Fencer(1, 1, 5, 0, 0)
        f2 = PoolStage.Fencer(1, 1, 5, 0, 1)
        got_lt = False
        got_gte = False
        for x in range(20):
            if f1 > f2:
                got_gte = True
            else:
                got_lt = True
        self.assertTrue(got_lt and got_gte, "random fallback")

    def test_function_results(self):
        competition = PreAddedCompetitionOfSize(entries__num_of_entries=3)  # type: Competition
        stage = competition.stage_set.create(type=Stage.POOL, number=1)
        pool_stage = stage.poolstage_set.first()  # type: PoolStage
        pool_stage.start(1)
        pool = pool_stage.pool_set.first()
        make_boring_results(pool)
        results = pool_stage.results()
        self.assertEqual(2, results[0].V)
        self.assertEqual(10, results[0].ind())

    def test_function_results_with_carry(self):
        competition = PreAddedCompetitionOfSize(entries__num_of_entries=3)  # type: Competition
        stage = competition.stage_set.create(type=Stage.POOL, number=1)
        pool_stage = stage.poolstage_set.first()  # type: PoolStage
        pool_stage.start(1)
        pool = pool_stage.pool_set.first()
        make_boring_results(pool)
        stage.state = Stage.FINISHED
        stage.save()
        stage = competition.stage_set.create(type=Stage.POOL, number=2)
        pool_stage = stage.poolstage_set.first()  # type: PoolStage
        pool_stage.start(1)
        pool_stage.carry_previous_results = True
        pool_stage.save()
        pool = pool_stage.pool_set.first()
        make_boring_results(pool)
        results = pool_stage.results()
        self.assertEqual(4, results[0].V)
        self.assertEqual(20, results[0].ind())

    def test_function_ordered_competitors_base(self):
        competition = PreAddedCompetitionOfSize(entries__num_of_entries=5)  # type: Competition
        stage = competition.stage_set.create(type=Stage.POOL, number=1)
        pool_stage = stage.poolstage_set.first()  # type: PoolStage
        pool_stage.start(1)
        pool = pool_stage.pool_set.first()
        make_boring_results(pool)
        stage.state = Stage.FINISHED
        stage.save()
        self.assertListEqual(pool_stage.ordered_competitors(), list(competition.entry_set.order_by('pk').all()))

    def test_function_ordered_competitors_with_draw(self):
        competition = PreAddedCompetitionOfSize(entries__num_of_entries=10)  # type: Competition
        stage = competition.stage_set.create(type=Stage.POOL, number=1)
        pool_stage = stage.poolstage_set.first()  # type: PoolStage
        pool_stage.start(2)
        pool = pool_stage.pool_set.first()
        make_boring_results(pool_stage.pool_set.all()[0])
        make_boring_results(pool_stage.pool_set.all()[1])
        stage.state = Stage.FINISHED
        stage.save()
        first_ordering = pool_stage.ordered_competitors()
        new_ordering = first_ordering.copy()
        x = 0
        while new_ordering == first_ordering:
            new_ordering = pool_stage.ordered_competitors()
            if new_ordering != first_ordering:
                break
            elif x == 10:
                self.fail('ordering should change if there is a draw')
            x += 1
        rough_expected_ordering = competition.entry_set.order_by('pk').all()
        for x in range(5):
            # checking that overall ordering is still correct
            expected = set(rough_expected_ordering[x*2:x*2+2])
            actual = set(first_ordering[x*2:x*2+2])
            self.assertSetEqual(expected, actual)
