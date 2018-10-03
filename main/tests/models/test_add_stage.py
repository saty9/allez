from ..factories.competition_factory import CompetitionOfSize
from django.test import TestCase
from main.models import Stage, AddStage, Entry


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

    def test_ranked_competitors_base(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.STARTED, number=0)
        add_stage = stage.addstage_set.first()
        entry_set = list(self.competition.entry_set.order_by('pk').all())
        for index, e in enumerate(entry_set):
            add_stage.addcompetitor_set.create(entry=e, sequence=index)
        first = entry_set[0].addcompetitor_set.first()
        first.sequence = entry_set[-1].addcompetitor_set.first().sequence
        first.save()
        stage.state = stage.FINISHED
        stage.save()
        expected = []
        for e in entry_set[1:-1]:
            expected.append(set([e]))
        expected.append(set([entry_set[0], entry_set[-1]]))
        actual = list(map(set, add_stage.ranked_competitors()))
        self.assertListEqual(expected, actual)

    def test_where_TOP(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.STARTED, number=0)
        add_stage = stage.addstage_set.first()
        entry_set = self.competition.entry_set.order_by('id').all()
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
        entry_set = self.competition.entry_set.order_by('id').all()
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

    def test_possible_additions_base(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.NOT_STARTED, number=0)
        add_stage = stage.addstage_set.first()
        expected = self.competition.entry_set.all()
        self.assertSetEqual(set(expected), set(add_stage.possible_additions()))

    def test_possible_additions_entry_with_bad_state(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.NOT_STARTED, number=0)
        add_stage = stage.addstage_set.first()
        expected = list(self.competition.entry_set.all())
        e = expected[0]
        expected = expected[1:]
        for s in [Entry.DID_NOT_FINISH, Entry.DID_NOT_START, Entry.EXCLUDED]:
            e.state = s
            e.save()
            self.assertSetEqual(set(expected), set(add_stage.possible_additions()))

    def test_possible_additions_entry_already_added(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.NOT_STARTED, number=0)
        add_stage = stage.addstage_set.first()
        expected = list(self.competition.entry_set.all())
        e = expected[0]
        expected = expected[1:]
        add_stage.addcompetitor_set.create(entry=e, sequence=0)
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.NOT_STARTED, number=1)
        add_stage = stage.addstage_set.first()
        self.assertSetEqual(set(expected), set(add_stage.possible_additions()))

    def test_add_entries_base(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.FINISHED, number=0)
        add_stage = stage.addstage_set.first()
        expected = list(self.competition.entry_set.all())
        add_stage.add_entries(map(lambda x: [x], expected))
        self.assertListEqual(expected, stage.ordered_competitors())

    def test_add_entries_entry_already_added_elsewhere(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.FINISHED, number=0)
        add_stage = stage.addstage_set.first()
        expected = list(self.competition.entry_set.all())
        e = expected[-1]
        add_stage.add_entries([[e]])
        self.assertListEqual([e], stage.ordered_competitors())

        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.FINISHED, number=1)
        add_stage = stage.addstage_set.first()
        add_stage.add_entries(map(lambda x: [x], expected))
        self.assertListEqual(expected, stage.ordered_competitors())
        self.assertListEqual(expected[:-1], list(map(lambda x: x.entry, add_stage.addcompetitor_set.all())))

    def test_add_entries_sequence_already_exists(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.FINISHED, number=0)
        add_stage = stage.addstage_set.first()
        expected = list(self.competition.entry_set.all())
        e = expected[0]
        expected = expected[1:]
        add_stage.add_entries(map(lambda x: [x], expected))
        self.assertListEqual(expected, stage.ordered_competitors())
        add_stage.add_entries([[e]])
        expected.append(e)
        self.assertListEqual(expected, stage.ordered_competitors())

    def test_add_entries_same_ranking(self):
        stage = self.competition.stage_set.create(type=Stage.ADD, state=Stage.FINISHED, number=0)
        add_stage = stage.addstage_set.first()
        expected = list(self.competition.entry_set.all())
        add_stage.add_entries([expected])
        self.assertListEqual([expected], stage.ranked_competitors())
