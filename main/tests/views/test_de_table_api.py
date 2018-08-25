from main.tests.factories.competition_factory import PreAddedCompetitionOfSize
from main.tests.factories.org_member_factory import ManagerFactory
from main.tests.factories.organisation_factory import OrganisationFactory
from main.tests.models.test_de_stage import make_boring_de_table_results
from django.test import TestCase, Client
from django.urls import reverse
from main.models import Stage


class TestDeTableAPI(TestCase):

    def setUp(self):
        self.c = Client()
        self.competition = PreAddedCompetitionOfSize(entries__num_of_entries=8)
        self.stage = self.competition.stage_set.create(state=Stage.STARTED, type=Stage.DE, number=1)
        self.de_stage = self.stage.destage_set.first()
        self.de_stage.start()
        self.table_head = self.de_stage.detable_set.first()
        self.manager = ManagerFactory(organisation=self.competition.organisation).user
        org = OrganisationFactory()
        self.wrong_org_manager = ManagerFactory(organisation=org).user
        self.target = reverse('main/de_table_endpoint', kwargs={'table_id': self.table_head.id})

    def test_add_result_base(self):
        self.c.force_login(self.manager)
        eA = self.table_head.detableentry_set.first()
        eB = eA.against()
        out = self.c.post(self.target, {'type': 'add_result',
                                        'entryA': eA.id,
                                        'entryB': eB.id,
                                        'scoreA': 15,
                                        'scoreB': 7,
                                        'victoryA': 1})
        self.assertJSONEqual(out.content, {'success': True})
        eA.refresh_from_db()
        eB.refresh_from_db()
        self.assertEqual(eA.score, 15)
        self.assertEqual(eA.victory, True)
        self.assertEqual(eB.score, 7)
        self.assertEqual(eB.victory, False)

    def test_add_result_score_victory_mismatch(self):
        self.c.force_login(self.manager)
        eA = self.table_head.detableentry_set.first()
        eB = eA.against()
        out = self.c.post(self.target, {'type': 'add_result',
                                        'entryA': eA.id,
                                        'entryB': eB.id,
                                        'scoreA': 7,
                                        'scoreB': 15,
                                        'victoryA': 1})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'score victory mismatch',
                                           'verbose_reason': 'score victory mismatch'})
        eA.refresh_from_db()
        eB.refresh_from_db()
        self.assertEqual(eA.score, 0)
        self.assertEqual(eA.victory, False)
        self.assertEqual(eB.score, 0)
        self.assertEqual(eB.victory, False)

    def test_add_result_score_tie_with_victory(self):
        self.c.force_login(self.manager)
        eA = self.table_head.detableentry_set.first()
        eB = eA.against()
        out = self.c.post(self.target, {'type': 'add_result',
                                        'entryA': eA.id,
                                        'entryB': eB.id,
                                        'scoreA': 7,
                                        'scoreB': 7,
                                        'victoryA': 0})
        self.assertJSONEqual(out.content, {'success': True})
        eA.refresh_from_db()
        eB.refresh_from_db()
        self.assertEqual(eA.score, 7)
        self.assertEqual(eA.victory, False)
        self.assertEqual(eB.score, 7)
        self.assertEqual(eB.victory, True)

    def test_add_result_bad_entry_pair(self):
        self.c.force_login(self.manager)
        eA = self.table_head.detableentry_set.first()
        eB = self.table_head.detableentry_set.exclude(id__in=[eA.id, eA.against().id]).first()
        out = self.c.post(self.target, {'type': 'add_result',
                                        'entryA': eA.id,
                                        'entryB': eB.id,
                                        'scoreA': 15,
                                        'scoreB': 7,
                                        'victoryA': 1})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'bad entry pair',
                                           'verbose_reason': "these entries aren't fighting each other this round"})
        eA.refresh_from_db()
        eB.refresh_from_db()
        self.assertEqual(eA.score, 0)
        self.assertEqual(eA.victory, False)
        self.assertEqual(eB.score, 0)
        self.assertEqual(eB.victory, False)

    def test_add_result_bye_victory(self):
        competition = PreAddedCompetitionOfSize(entries__num_of_entries=7)
        stage = competition.stage_set.create(state=Stage.STARTED, type=Stage.DE, number=1)
        de_stage = stage.destage_set.first()
        de_stage.start()
        table_head = de_stage.detable_set.first()
        manager = ManagerFactory(organisation=competition.organisation).user
        target = reverse('main/de_table_endpoint', kwargs={'table_id': table_head.id})
        self.c.force_login(manager)
        eA = table_head.detableentry_set.first()
        eB = eA.against()
        out = self.c.post(target, {'type': 'add_result',
                                   'entryA': eA.id,
                                   'entryB': eB.id,
                                   'scoreA': 0,
                                   'scoreB': 15,
                                   'victoryA': 0})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'bye_victory',
                                           'verbose_reason': 'Byes cannot win a match'})
        eA.refresh_from_db()
        eB.refresh_from_db()
        self.assertEqual(eA.score, 0)
        self.assertEqual(eA.victory, True)
        self.assertEqual(eB.score, 0)
        self.assertEqual(eB.victory, False)

    def test_add_result_with_children(self):
        self.c.force_login(self.manager)
        make_boring_de_table_results(self.table_head)
        self.table_head.make_children()
        eA = self.table_head.detableentry_set.first()
        eB = eA.against()
        out = self.c.post(self.target, {'type': 'add_result',
                                        'entryA': eA.id,
                                        'entryB': eB.id,
                                        'scoreA': 0,
                                        'scoreB': 15,
                                        'victoryA': 0})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'child_exists',
                                           'verbose_reason': 'Cannot add results after next round of tables made'})
        eA.refresh_from_db()
        eB.refresh_from_db()
        self.assertEqual(eA.score, 15)
        self.assertEqual(eA.victory, True)
        self.assertEqual(eB.score, 0)
        self.assertEqual(eB.victory, False)

    def test_add_result_bad_state(self):
        self.c.force_login(self.manager)
        for state in [Stage.NOT_STARTED, Stage.READY, Stage.FINISHED, Stage.LOCKED]:
            self.stage.state = state
            self.stage.save()
            eA = self.table_head.detableentry_set.first()
            eB = eA.against()
            eA_before = eA
            eB_before = eB
            out = self.c.post(self.target, {'type': 'add_result',
                                            'entryA': eA.id,
                                            'entryB': eB.id,
                                            'scoreA': 15,
                                            'scoreB': 7,
                                            'victoryA': 1})
            self.assertJSONEqual(out.content, {'success': False,
                                               'reason': 'incorrect state',
                                               'verbose_reason': 'stage not currently running'})
            eA.refresh_from_db()
            eB.refresh_from_db()
            self.assertEqual(eA.score, eA_before.score)
            self.assertEqual(eA.victory, eA_before.victory)
            self.assertEqual(eB.score, eB_before.score)
            self.assertEqual(eB.victory, eB_before.victory)

    def test_table_complete_base(self):
        self.c.force_login(self.manager)
        make_boring_de_table_results(self.table_head)
        out = self.c.post(self.target, {'type': 'table_complete'})
        self.assertJSONEqual(out.content, {'success': True})
        self.table_head.refresh_from_db()
        assert self.table_head.children.exists
        assert self.table_head.complete

    def test_table_complete_bouts_incomplete(self):
        self.c.force_login(self.manager)
        make_boring_de_table_results(self.table_head)
        e1 = self.table_head.detableentry_set.last()
        e2 = e1.against()
        e1.victory = False
        e1.save()
        e2.victory = False
        e2.save()
        out = self.c.post(self.target, {'type': 'table_complete'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'incomplete_bouts',
                                           'verbose_reason': 'One or more bouts incomplete'})
        self.table_head.refresh_from_db()
        self.assertFalse(self.table_head.children.exists())
        self.assertFalse(self.table_head.complete)

    def test_table_complete_already_complete(self):
        self.c.force_login(self.manager)
        make_boring_de_table_results(self.table_head)
        self.table_head.make_children()
        out = self.c.post(self.target, {'type': 'table_complete'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'already_complete',
                                           'verbose_reason': 'This table is already marked as complete'})
        assert self.table_head.complete

    def test_get_bouts(self):
        self.c.force_login(self.manager)
        make_boring_de_table_results(self.table_head)
        expected_bouts = []
        entries = list(self.table_head.detableentry_set.all())

        def response_dict(e):
            seed = self.de_stage.deseed_set.get(entry=e.entry).seed
            return {'id': e.id,
                    'entry_id': e.entry.id,
                    'score': e.score,
                    'victory': e.victory,
                    'seed': seed,
                    'entry__competitor__name': e.entry.competitor.name,
                    'entry__competitor__club__name': e.entry.competitor.club.name}
        for e in entries:
            against = e.against()
            bout = {'e0': response_dict(e),
                    'e1': response_dict(against)}
            expected_bouts.append(bout)
            entries.remove(against)
        out = self.c.get(self.target)
        self.assertJSONEqual(out.content, {'bouts': expected_bouts})

    def test_get_bouts_404(self):
        self.c.force_login(self.manager)
        target = reverse('main/de_table_endpoint', kwargs={'table_id': 5})
        out = self.c.get(target)
        self.assertEqual(out.status_code, 404)

    def test_post_bad_type(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'anything_else'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'unrecognised request',
                                           'verbose_reason': 'unrecognised request'})
