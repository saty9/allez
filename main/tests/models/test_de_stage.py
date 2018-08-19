from ..factories.competition_factory import PreAddedCompetitionOfSize
from django.test import TestCase
from main.models import Stage, DeStage, Competition, DeTable


def make_boring_de_results(de_stage):
    tables = [de_stage.detable_set.first()]
    for table in tables:
        if not table.automated():
            make_boring_de_table_results(table)
            if table.detableentry_set.count() > 2:
                table.make_children()
                tables += list(de_stage.detable_set.filter(parent=table).all())


def make_boring_de_table_results(table):
    entries = list(table.detableentry_set.order_by('entry__deseed__seed').all())
    for e in entries:
        against = e.against()
        e.score = 15
        e.victory = True
        entries.remove(against)
        e.save()


class TestDeStage(TestCase):

    def setUp(self):
        self.competition = PreAddedCompetitionOfSize(entries__num_of_entries=15)  # type: Competition
        self.stage = self.competition.stage_set.create(type=Stage.DE, number=1)
        self.de_stage = self.stage.destage_set.first()  # type: DeStage

    def test_function_start_base(self):
        self.de_stage.start()
        self.assertEqual(self.de_stage.detable_set.count(), 1, "expecting 1 table to have been generated")
        de_table = self.de_stage.detable_set.first()  # type: DeTable
        self.assertEqual(self.de_stage.deseed_set.count(), 15, "expecting 15 seeds")
        self.assertEqual(de_table.detableentry_set.filter(entry__isnull=True).count(), 1, "expecting 1 bye")
        expected_bye = de_table.detableentry_set.filter(entry__isnull=True).first()
        assert expected_bye.against().victory
        expected_seed_order = list(self.de_stage.stage.input())
        actual_seed_order = list(map(lambda x: x.entry, self.de_stage.deseed_set.order_by('seed').all()))
        self.assertListEqual(expected_seed_order, actual_seed_order)

    def test_function_start_already_started(self):
        self.de_stage.start()
        self.assertRaises(AssertionError, self.de_stage.start)
        self.assertEqual(self.de_stage.detable_set.count(), 1, "expecting only 1 table")

    def test_function_ordered_competitors(self):
        self.de_stage.start()
        make_boring_de_results(self.de_stage)
        input_entries = self.de_stage.stage.input()
        self.assertListEqual(input_entries, self.de_stage.ordered_competitors())
        x = self.de_stage.detable_set.first()
        while x.children.exists():
            x = x.children.filter(winners=True).first()
        y = x.detableentry_set.first()
        against_y = y.against()
        against_y.victory = y.victory
        y.victory = not y.victory
        against_y.save()
        y.save()
        temp = input_entries[0]
        input_entries[0] = input_entries[1]
        input_entries[1] = temp
        self.assertListEqual(input_entries, self.de_stage.ordered_competitors())

    def test_function_ordered_competitors_not_complete(self):
        self.de_stage.start()
        self.assertRaises(Stage.NotCompleteError, self.de_stage.ordered_competitors)

