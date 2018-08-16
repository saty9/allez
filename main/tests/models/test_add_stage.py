from ..factories.competition_factory import CompetitionOfSize
from django.test import TestCase
from main.models import Stage, AddStage


class TestAddStage(TestCase):

    def setUp(self):
        self.competition = CompetitionOfSize(entries__num_of_entries=8)

    def test_ordered_competitors_NOT_STARTED(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.NOT_STARTED, number=0)
        add_stage = stage.addstage_set.first()
        self.assertRaises(Stage.NotCompleteError, add_stage.ordered_competitors)

    def test_ordered_competitors_READY(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.READY, number=0)
        add_stage = stage.addstage_set.first()
        self.assertRaises(Stage.NotCompleteError, add_stage.ordered_competitors)

    def test_ordered_competitors_OTHERS(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.STARTED, number=0)
        add_stage = stage.addstage_set.first()
        entry_set = self.competition.entry_set.all()
        for index, e in enumerate(entry_set):
            add_stage.addcompetitor_set.create(entry=e, sequence=index)
        for state in [Stage.STARTED, Stage.FINISHED, Stage.LOCKED]:
            stage.state = state
            stage.save()
            ordered_competitors = add_stage.ordered_competitors()
            self.assertEqual(len(ordered_competitors), len(entry_set))
            self.assertEqual(ordered_competitors, list(entry_set))

    def test_where_TOP(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.STARTED, number=0)
        add_stage = stage.addstage_set.first()
        entry_set = self.competition.entry_set.all()
        for index, e in enumerate(entry_set[1:]):
            add_stage.addcompetitor_set.create(entry=e, sequence=index)
        self.assertEqual(add_stage.ordered_competitors(), list(entry_set[1:]))

        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.STARTED, number=1)
        add_stage = stage.addstage_set.first()
        add_stage.where = AddStage.TOP
        add_stage.save()
        add_stage.addcompetitor_set.create(entry=entry_set[0], sequence=0)

        ordered_competitors = add_stage.ordered_competitors()
        self.assertEqual(len(ordered_competitors), len(entry_set))
        self.assertEqual(ordered_competitors, list(entry_set))

    def test_where_BOTTOM(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.STARTED, number=0)
        add_stage = stage.addstage_set.first()
        entry_set = self.competition.entry_set.all()
        for index, e in enumerate(entry_set[1:]):
            add_stage.addcompetitor_set.create(entry=e, sequence=index)
        self.assertEqual(add_stage.ordered_competitors(), list(entry_set[1:]))

        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.STARTED, number=1)
        add_stage = stage.addstage_set.first()
        add_stage.where = AddStage.BOTTOM
        add_stage.save()
        add_stage.addcompetitor_set.create(entry=entry_set[0], sequence=0)

        ordered_competitors = add_stage.ordered_competitors()
        self.assertEqual(len(ordered_competitors), len(entry_set))
        self.assertEqual(ordered_competitors, list(entry_set[1:]) + [entry_set[0]])
