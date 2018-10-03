from ..factories.competition_factory import CompetitionOfSize
from django.test import TestCase
from main.models import Stage


class TestStage(TestCase):

    def setUp(self):
        self.competition = CompetitionOfSize(entries__num_of_entries=8)

    def test_input_is_static(self):
        self.competition.entry_set.update(seed=1)
        stage = self.competition.stage_set.create(type=Stage.ADD, number=0)
        add_stage = stage.addstage_set.first()
        add_stage.add_entries([self.competition.entry_set.order_by('seed').all()])
        stage.state = Stage.FINISHED
        stage.save()
        stage2 = self.competition.stage_set.create(type=Stage.ADD, number=1)
        stage_input = stage2.input()
        for x in range(4):
            self.assertListEqual(stage_input, stage2.input())
