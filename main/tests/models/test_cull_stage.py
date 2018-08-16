from ..factories.competition_factory import PreAddedCompetitionOfSize
from django.test import TestCase
from main.models import Stage, AddStage


class TestCullStage(TestCase):

    def setUp(self):
        self.competition = PreAddedCompetitionOfSize(entries__num_of_entries=8)
        self.stage = self.competition.stage_set.create(type=Stage.CULL, number=1)
        self.cull_stage = self.stage.cullstage_set.first()

    def test_simple_cull(self):
        self.cull_stage.number = 4
        self.cull_stage.save()
        out = self.stage.ordered_competitors()
        expected = self.stage.input()[0:4]
        self.assertEqual(out, expected)

    def test_cull_with_tie(self):
        self.assertEqual(True, False)