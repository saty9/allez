from ..factories.competition_factory import PreAddedCompetitionOfSize
from ..factories.org_member_factory import ManagerFactory, DTFactory
from ..factories.organisation_factory import OrganisationFactory
from ..factories.user_factory import UserFactory
from django.db.models import F
from django.test import TestCase, Client
from django.urls import reverse
from main.models import Stage, PoolBout
from ..models.test_pool_stage import make_boring_results


class TestPoolAPI(TestCase):

    def setUp(self):
        self.c = Client()
        self.competition = PreAddedCompetitionOfSize(entries__num_of_entries=8)
        self.stage = self.competition.stage_set.create(state=Stage.STARTED, type=Stage.POOL, number=1)
        self.pool_stage = self.stage.poolstage_set.first()
        self.pool_stage.start(1)
        self.pool = self.pool_stage.pool_set.first()
        self.manager = ManagerFactory(organisation=self.competition.organisation).user
        org = OrganisationFactory()
        self.wrong_org_manager = ManagerFactory(organisation=org).user
        self.target = reverse('main/pool_endpoint', kwargs={'pool_id': self.pool.id})

    def test_authorization_block(self):
        out = self.c.post(self.target, {'type': 'anything'})
        unauthorised_message = {'success': False, 'reason': 'NotLoggedIn'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

        self.c.force_login(self.wrong_org_manager)
        out = self.c.post(self.target, {'type': 'set_cull_level'})
        unauthorised_message = {'success': False, 'reason': 'InsufficientPermissions'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

    def test_more_auth_stuff(self):
        ref = UserFactory()
        ref_obj = self.competition.referee_set.create(user=ref)
        self.pool.referee = ref_obj
        self.pool.save()
        other_ref = UserFactory()
        self.competition.referee_set.create(user=other_ref)
        dt = DTFactory(organisation=self.competition.organisation).user
        for user in [other_ref, UserFactory()]:
            self.c.force_login(user)
            entries = self.pool.poolentry_set.all()
            e1 = entries[1]
            e2 = entries[0]
            out = self.c.post(self.target, {'type': 'bout_result',
                                            'entry_1': e1.id,
                                            'entry_2': e2.id,
                                            'e1_score': 5,
                                            'e2_score': 0,
                                            'e1_victory': 1})
            self.assertJSONEqual(out.content, {'success': False, 'reason': 'InsufficientPermissions'})
        for user in [self.manager, dt, ref]:
            self.c.force_login(user)
            entries = self.pool.poolentry_set.all()
            e1 = entries[1]
            e2 = entries[0]
            out = self.c.post(self.target, {'type': 'bout_result',
                                            'entry_1': e1.id,
                                            'entry_2': e2.id,
                                            'e1_score': 5,
                                            'e2_score': 0,
                                            'e1_victory': 1})
            self.assertJSONEqual(out.content, {'success': True, 'pool_complete': False})

    def test_get_pool_data_base(self):
        make_boring_results(self.pool)
        out = self.c.get(self.target)
        bouts = list(PoolBout.objects.filter(fencerA__in=self.pool.poolentry_set.all()).values().all())
        entries = list(self.pool.poolentry_set.values('id', 'number', name=F('entry__competitor__name')))
        self.assertJSONEqual(out.content, {
            'entries': entries,
            'bouts': bouts})
        for bout in bouts:
            self.assertIn('fencerA_id', bout.keys())
            self.assertIn('fencerB_id', bout.keys())
            self.assertIn('scoreA', bout.keys())
            self.assertIn('victoryA', bout.keys())

    def test_get_pool_data_no_bouts(self):
        out = self.c.get(self.target)
        entries = list(self.pool.poolentry_set.values('id', 'number', name=F('entry__competitor__name')))
        self.assertJSONEqual(out.content, {'entries': entries,
                                           'bouts': []})
        for e in entries:
            self.assertIn('id', e.keys())
            self.assertIn('number', e.keys())
            self.assertIn('name', e.keys())

    def test_get_pool_data_non_existent_pool(self):
        self.pool.delete()
        out = self.c.get(self.target)
        self.assertEqual(out.status_code, 404)

    def test_post_non_existent_pool(self):
        self.pool.delete()
        out = self.c.post(self.target, {'anything': 7})
        self.assertEqual(out.status_code, 404)

    def test_post_result_new(self):
        self.c.force_login(self.manager)
        entries = self.pool.poolentry_set.all()
        e1 = entries[1]
        e2 = entries[0]
        out = self.c.post(self.target, {'type': 'bout_result',
                                        'entry_1': e1.id,
                                        'entry_2': e2.id,
                                        'e1_score': 5,
                                        'e2_score': 0,
                                        'e1_victory': 1})
        self.assertJSONEqual(out.content, {'success': True, 'pool_complete': False})
        self.assertEqual(e1.fencerA_bout_set.count(), 1)
        self.assertEqual(e2.fencerA_bout_set.count(), 1)
        e1_bout = e1.fencerA_bout_set.first()
        e2_bout = e2.fencerA_bout_set.first()
        self.assertEqual(e1_bout.victoryA, True)
        self.assertEqual(e1_bout.fencerB, e2)
        self.assertEqual(e1_bout.scoreA, 5)
        self.assertEqual(e2_bout.victoryA, False)
        self.assertEqual(e2_bout.fencerB, e1)
        self.assertEqual(e2_bout.scoreA, 0)

    def test_post_result_bad_score_victory(self):
        self.c.force_login(self.manager)
        entries = self.pool.poolentry_set.all()
        e1 = entries[1]
        e2 = entries[0]
        out = self.c.post(self.target, {'type': 'bout_result',
                                        'entry_1': e1.id,
                                        'entry_2': e2.id,
                                        'e1_score': 0,
                                        'e2_score': 5,
                                        'e1_victory': 1})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'score victory mismatch',
                                           'verbose_reason': 'score victory mismatch'})
        self.assertEqual(e1.fencerA_bout_set.count(), 0)

    def test_post_result_score_tie_with_victory(self):
        self.c.force_login(self.manager)
        entries = self.pool.poolentry_set.all()
        e1 = entries[1]
        e2 = entries[0]
        out = self.c.post(self.target, {'type': 'bout_result',
                                        'entry_1': e1.id,
                                        'entry_2': e2.id,
                                        'e1_score': 4,
                                        'e2_score': 4,
                                        'e1_victory': 1})
        self.assertJSONEqual(out.content, {'success': True, 'pool_complete': False})
        self.assertEqual(e1.fencerA_bout_set.count(), 1)
        self.assertEqual(e2.fencerA_bout_set.count(), 1)
        e1_bout = e1.fencerA_bout_set.first()
        e2_bout = e2.fencerA_bout_set.first()
        self.assertEqual(e1_bout.victoryA, True)
        self.assertEqual(e1_bout.fencerB, e2)
        self.assertEqual(e1_bout.scoreA, 4)
        self.assertEqual(e2_bout.victoryA, False)
        self.assertEqual(e2_bout.fencerB, e1)
        self.assertEqual(e2_bout.scoreA, 4)

    def test_post_result_overwrite(self):
        self.c.force_login(self.manager)
        entries = self.pool.poolentry_set.all()
        e1 = entries[1]
        e2 = entries[0]
        e1.fencerA_bout_set.create(fencerB=e2, scoreA=0, victoryA=False)
        e2.fencerA_bout_set.create(fencerB=e1, scoreA=5, victoryA=True)
        out = self.c.post(self.target, {'type': 'bout_result',
                                        'entry_1': e1.id,
                                        'entry_2': e2.id,
                                        'e1_score': 5,
                                        'e2_score': 0,
                                        'e1_victory': 1})
        self.assertJSONEqual(out.content, {'success': True, 'pool_complete': False})
        self.assertEqual(e1.fencerA_bout_set.count(), 1)
        self.assertEqual(e2.fencerA_bout_set.count(), 1)
        e1_bout = e1.fencerA_bout_set.first()
        e2_bout = e2.fencerA_bout_set.first()
        self.assertEqual(e1_bout.victoryA, True)
        self.assertEqual(e1_bout.fencerB, e2)
        self.assertEqual(e1_bout.scoreA, 5)
        self.assertEqual(e2_bout.victoryA, False)
        self.assertEqual(e2_bout.fencerB, e1)
        self.assertEqual(e2_bout.scoreA, 0)

    def test_post_result_bad_stage_state(self):
        self.c.force_login(self.manager)
        entries = self.pool.poolentry_set.all()
        e1 = entries[1]
        e2 = entries[0]
        e1.fencerA_bout_set.create(fencerB=e2, scoreA=0, victoryA=False)
        e2.fencerA_bout_set.create(fencerB=e1, scoreA=5, victoryA=True)
        for state in [Stage.NOT_STARTED, Stage.READY, Stage.FINISHED, Stage.LOCKED]:
            self.stage.state = state
            self.stage.save()
            out = self.c.post(self.target, {'type': 'bout_result',
                                            'entry_1': e1.id,
                                            'entry_2': e2.id,
                                            'e1_score': 5,
                                            'e2_score': 0,
                                            'e1_victory': 1})
            self.assertJSONEqual(out.content, {'success': False, 'reason': 'stage not currently running'})
            self.assertEqual(e1.fencerA_bout_set.count(), 1)
            self.assertEqual(e2.fencerA_bout_set.count(), 1)
            e1_bout = e1.fencerA_bout_set.first()
            e2_bout = e2.fencerA_bout_set.first()
            self.assertEqual(e1_bout.victoryA, False)
            self.assertEqual(e1_bout.fencerB, e2)
            self.assertEqual(e1_bout.scoreA, 0)
            self.assertEqual(e2_bout.victoryA, True)
            self.assertEqual(e2_bout.fencerB, e1)
            self.assertEqual(e2_bout.scoreA, 5)

    def test_post_result_pool_complete(self):
        make_boring_results(self.pool)
        self.c.force_login(self.manager)
        entries = self.pool.poolentry_set.all()
        e1 = entries[1]
        e2 = entries[0]
        out = self.c.post(self.target, {'type': 'bout_result',
                                        'entry_1': e1.id,
                                        'entry_2': e2.id,
                                        'e1_score': 5,
                                        'e2_score': 0,
                                        'e1_victory': 1})
        self.assertJSONEqual(out.content, {'success': True, 'pool_complete': True})

    def test_post_bad_type(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'anything_else'})
        self.assertJSONEqual(out.content, {'success': False, 'reason': 'unable to understand post'})
