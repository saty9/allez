from ..factories.competition_factory import PreAddedCompetitionOfSize
from django.test import TestCase
from main.models import Stage, DeStage, Competition
from main.models.de_table import UnfinishedTableException
from main.tests.models.test_de_stage import make_boring_de_table_results, make_boring_de_results


class TestDeTable(TestCase):

    def setUp(self):
        self.competition = PreAddedCompetitionOfSize(entries__num_of_entries=9)  # type: Competition
        self.stage = self.competition.stage_set.create(type=Stage.DE, number=1)
        self.de_stage = self.stage.destage_set.first()  # type: DeStage
        self.de_stage.start()
        self.head_table = self.de_stage.detable_set.first()

    def test_function_automated(self):
        self.assertFalse(self.head_table.automated())
        make_boring_de_table_results(self.head_table)
        self.head_table.make_children()
        loser_table = self.head_table.children.filter(winners=False).first()
        assert loser_table.automated()

    def test_function_automated_bye_only_table_case(self):
        make_boring_de_table_results(self.head_table)
        self.head_table.make_children()
        loser_table = self.head_table.children.filter(winners=False).first()
        loser_table.make_children()
        bye_only_table = loser_table.children.filter(winners=False).first()
        assert bye_only_table.automated()

    def test_function_automated_low_max_rank_case(self):
        self.de_stage.fight_down_to = 4
        make_boring_de_table_results(self.head_table)
        self.head_table.make_children()
        winner_table = self.head_table.children.filter(winners=False).first()
        make_boring_de_table_results(winner_table)
        winner_table.make_children()
        winner_loser_table = winner_table.children.filter(winners=False).first()
        assert winner_loser_table.automated()
        winner_winner_table = winner_table.children.filter(winners=True).first()
        self.assertFalse(winner_winner_table.automated())

    def test_function_make_children(self):
        make_boring_de_table_results(self.head_table)
        self.head_table.make_children()
        winner_table = self.head_table.children.filter(winners=True).first()
        expected_winner_table_entries = self.stage.input()[0:8]
        self.assertListEqual(expected_winner_table_entries,
                             list(map(lambda x: x.entry, winner_table.
                                      detableentry_set.
                                      order_by('entry__deseed__seed').all())))
        loser_table = self.head_table.children.filter(winners=False).first()
        expected_loser_table_entries = [self.stage.input()[-1]] + [None for _ in range(7)]
        self.assertListEqual(expected_loser_table_entries,
                             list(map(lambda x: x.entry, loser_table.
                                      detableentry_set.
                                      order_by('entry__deseed__seed').all())))

    def test_function_make_children_incomplete_fights(self):
        make_boring_de_table_results(self.head_table)
        entry1 = self.head_table.detableentry_set.first()
        entry1.victory = False
        entry1.save()
        self.assertRaises(UnfinishedTableException, self.head_table.make_children)
        self.assertEqual(self.head_table.children.count(), 0)

    def test_function_make_children_with_prexisting_children(self):
        make_boring_de_table_results(self.head_table)
        self.head_table.make_children()
        self.assertRaises(AssertionError, self.head_table.make_children)

    def test_function_max_rank_table_head(self):
        self.assertEqual(self.head_table.max_rank(), 1)

    def test_function_max_rank_winners(self):
        make_boring_de_table_results(self.head_table)
        self.head_table.make_children()
        winners = self.head_table.children.filter(winners=True).first()
        self.assertEqual(winners.max_rank(), 1)

    def test_function_max_rank_losers(self):
        make_boring_de_table_results(self.head_table)
        self.head_table.make_children()
        losers = self.head_table.children.filter(winners=False).first()
        self.assertEqual(losers.max_rank(), 9)

    def test_function_ordered_competitors_automated(self):
        make_boring_de_table_results(self.head_table)
        self.head_table.make_children()
        winner_table = self.head_table.children.filter(winners=True).first()
        make_boring_de_table_results(winner_table)
        winner_table.make_children()
        winner_loser_table = winner_table.children.filter(winners=False).first()
        expected = winner_loser_table.detableentry_set.all()
        tuples = []
        for e in expected:
            tuples.append((e, self.de_stage.deseed_set.get(entry=e.entry).seed))
        expected = list(map(lambda x: x[0], sorted(tuples, key=lambda y: y[1])))
        self.assertListEqual(expected, winner_loser_table.ordered_competitors())

    def test_function_ordered_competitors_table_of_2(self):
        make_boring_de_table_results(self.head_table)
        self.head_table.make_children()
        winner_table = self.head_table.children.filter(winners=True).first()
        while winner_table.detableentry_set.count() > 2:
            make_boring_de_table_results(winner_table)
            winner_table.make_children()
            winner_table = winner_table.children.filter(winners=True).first()
        make_boring_de_table_results(winner_table)
        original_winner = winner_table.detableentry_set.filter(victory=True).first()
        original_winner.victory = False
        original_loser = original_winner.against()
        original_loser.victory = True
        original_winner.save()
        original_loser.save()
        self.assertListEqual([original_loser, original_winner], winner_table.ordered_competitors())

    def test_function_ordered_competitors_table_bigger_than_2(self):
        self.de_stage.fight_down_to = 9
        self.de_stage.save()
        make_boring_de_results(self.de_stage)
        expected = self.head_table.detableentry_set.exclude(entry__isnull=True).all()
        tuples = []
        for e in expected:
            tuples.append((e, self.de_stage.deseed_set.get(entry=e.entry).seed))
        expected = list(map(lambda x: x[0].entry, sorted(tuples, key=lambda y: y[1])))
        actual = list(map(lambda x: x.entry, self.head_table.ordered_competitors()))
        self.assertListEqual(expected, actual)

    def test_function_ordered_competitors_table_bigger_than_2_missing_children(self):
        make_boring_de_table_results(self.head_table)
        self.assertRaises(UnfinishedTableException, self.head_table.ordered_competitors)

    def test_function_ordered_competitors_incomplete_fights(self):
        self.assertRaises(UnfinishedTableException, self.head_table.ordered_competitors)
        make_boring_de_table_results(self.head_table)
        self.head_table.make_children()
        winner_table = self.head_table.children.filter(winners=True).first()
        while winner_table.detableentry_set.count() > 2:
            make_boring_de_table_results(winner_table)
            winner_table.make_children()
            winner_table = winner_table.children.filter(winners=True).first()
        self.assertRaises(UnfinishedTableException, winner_table.ordered_competitors)
