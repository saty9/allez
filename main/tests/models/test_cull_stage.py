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
        """when there is a cull if fencerA is tied with fencerB
                and the cull boundary lies between them both must survive"""
        add_stage = AddStage.objects.get(stage__competition=self.competition)
        add_stage.addcompetitor_set.filter(sequence__gt=0, sequence__lt=3).update(sequence=1)
        self.cull_stage.number = 2
        self.cull_stage.save()
        expected = self.stage.input()[0:3]
        result = self.cull_stage.ordered_competitors()
        self.assertEqual(expected[0], result[0])
        self.assertSetEqual(set(expected[1:]), set(result[1:]))