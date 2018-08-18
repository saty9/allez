import json

from ..factories.competition_factory import PreAddedCompetitionOfSize
from ..factories.org_member_factory import ManagerFactory
from ..factories.organisation_factory import OrganisationFactory
from ..factories.entry_factory import EntryFactory
from django.test import TestCase, Client
from django.urls import reverse
from main.models import Stage
from main.settings import MAX_POOL_SIZE
from ..models.test_pool_stage import make_boring_results


class TestPoolStageAPI(TestCase):

    def setUp(self):
        self.c = Client()
        self.competition = PreAddedCompetitionOfSize(entries__num_of_entries=30)
        self.stage = self.competition.stage_set.create(state=Stage.NOT_STARTED, type=Stage.POOL, number=1)
        self.pool_stage = self.stage.poolstage_set.first()
        self.manager = ManagerFactory(organisation=self.competition.organisation).user
        org = OrganisationFactory()
        self.wrong_org_manager = ManagerFactory(organisation=org).user
        self.target = reverse('main/stage_endpoint', kwargs={'stage_id': self.stage.id})

    def test_authorization_block(self):
        out = self.c.post(self.target, {'type': 'generate_pools'})
        unauthorised_message = {'success': False, 'reason': 'NotLoggedIn'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

        self.c.force_login(self.wrong_org_manager)
        out = self.c.post(self.target, {'type': 'generate_pools'})
        unauthorised_message = {'success': False, 'reason': 'InsufficientPermissions'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

    def test_generate_pools_base(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'generate_pools', 'number_of_pools': 3})
        self.assertJSONEqual(out.content, {'success': True})
        self.pool_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(self.pool_stage.pool_set.count(), 3)
        self.assertEqual(self.stage.state, Stage.READY)

    def test_generate_pools_oversize_pool(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'generate_pools', 'number_of_pools': 1})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': "invalid pool size",
                                           'verbose_reason': 'produces pools with less than 3 or more than {} fencers'
                             .format(MAX_POOL_SIZE)})
        self.pool_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(self.pool_stage.pool_set.count(), 0)
        self.assertEqual(self.stage.state, Stage.NOT_STARTED)

    def test_generate_pools_undersize_pool(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'generate_pools', 'number_of_pools': 1})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': "invalid pool size",
                                           'verbose_reason': 'produces pools with less than 3 or more than {} fencers'
                             .format(MAX_POOL_SIZE)})
        self.pool_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(self.pool_stage.pool_set.count(), 0)
        self.assertEqual(self.stage.state, Stage.NOT_STARTED)

    def test_generate_pools_undersize_pool(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'generate_pools', 'number_of_pools': 1})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': "invalid pool size",
                                           'verbose_reason': 'produces pools with less than 3 or more than {} fencers'
                             .format(MAX_POOL_SIZE)})
        self.pool_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(self.pool_stage.pool_set.count(), 0)
        self.assertEqual(self.stage.state, Stage.NOT_STARTED)

    def test_generate_pools_previous_unfinished(self):
        self.c.force_login(self.manager)
        add = self.competition.stage_set.get(number=0)
        add.state = Stage.STARTED
        add.save()
        out = self.c.post(self.target, {'type': 'generate_pools', 'number_of_pools': 3})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': "previous stage not completed yet",
                                           'verbose_reason': 'previous stage not completed yet'
                             .format(MAX_POOL_SIZE)})
        self.pool_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(self.pool_stage.pool_set.count(), 0)
        self.assertEqual(self.stage.state, Stage.NOT_STARTED)

    def test_generate_pools_bad_state(self):
        self.c.force_login(self.manager)
        for state in [Stage.READY, Stage.STARTED, Stage.FINISHED, Stage.LOCKED]:
            self.stage.state = state
            self.stage.save()
            out = self.c.post(self.target, {'type': 'generate_pools', 'number_of_pools': 3})
            self.assertJSONEqual(out.content, {'success': False,
                                               'reason': "incorrect state",
                                               'verbose_reason': 'this stage has already generated pools'})
            self.pool_stage.refresh_from_db()
            self.stage.refresh_from_db()
            self.assertEqual(self.pool_stage.pool_set.count(), 0)
            self.assertEqual(self.stage.state, state)

    def test_confirm_pools_simple(self):
        self.c.force_login(self.manager)
        self.pool_stage.start(3)
        self.stage.state = Stage.READY
        self.stage.save()
        pools_before = list(self.pool_stage.pool_set.all())
        p_entries_before = [list(x.poolentry_set.values()) for x in pools_before]
        out = self.c.post(self.target, {'type': 'confirm_pools'})
        self.assertJSONEqual(out.content, {'success': True})
        self.pool_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(self.pool_stage.pool_set.count(), 3)
        self.assertEqual(self.stage.state, Stage.STARTED)
        self.assertEqual(list(self.pool_stage.pool_set.all()), pools_before)
        p_entries_after = [list(x.poolentry_set.values()) for x in self.pool_stage.pool_set.all()]
        self.assertEqual(p_entries_after, p_entries_before)

    def test_confirm_pools_rearrange_pool(self):
        self.c.force_login(self.manager)
        self.pool_stage.start(3)
        self.stage.state = Stage.READY
        self.stage.save()
        pools_before = list(self.pool_stage.pool_set.all())
        p_entries_before = [list(x.poolentry_set.order_by('entry_id').values('entry_id')) for x in pools_before]
        intended_new_pools = {x: list(map(lambda z: z['entry_id'], y)) for x, y in enumerate(p_entries_before)}
        temp = intended_new_pools[0][0]
        intended_new_pools[0][0] = intended_new_pools[1][0]
        intended_new_pools[1][0] = temp
        out = self.c.post(self.target, {'type': 'confirm_pools', 'pools': json.dumps(intended_new_pools)})
        self.assertJSONEqual(out.content, {'success': True})
        self.pool_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(self.pool_stage.pool_set.count(), 3)
        self.assertEqual(self.stage.state, Stage.STARTED)
        self.assertNotEqual(list(self.pool_stage.pool_set.all()), pools_before)
        p_entries_after = [list(x.poolentry_set.order_by('entry_id').values('entry_id')) for x in self.pool_stage.pool_set.all()]
        pools_after = {x: list(map(lambda z: z['entry_id'], y)) for x, y in enumerate(p_entries_after)}
        self.assertEqual(pools_after, intended_new_pools)

    def test_confirm_pools_size_difference_error(self):
        self.c.force_login(self.manager)
        self.pool_stage.start(3)
        self.stage.state = Stage.READY
        self.stage.save()
        pools_before = list(self.pool_stage.pool_set.all())
        p_entries_before = [list(x.poolentry_set.order_by('entry_id').values('entry_id')) for x in pools_before]
        intended_new_pools = {x: list(map(lambda z: z['entry_id'], y)) for x, y in enumerate(p_entries_before)}
        intended_new_pools[0].append(intended_new_pools[1][0])
        intended_new_pools[1].__delitem__(0)
        out = self.c.post(self.target, {'type': 'confirm_pools', 'pools': json.dumps(intended_new_pools)})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'pool size difference',
                                           'verbose_reason': 'Pools can differ in size by at most 1'})
        self.pool_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(3, self.pool_stage.pool_set.count())
        self.assertEqual(Stage.READY, self.stage.state)
        self.assertEqual(pools_before, list(self.pool_stage.pool_set.all()))
        p_entries_after = [list(x.poolentry_set.order_by('entry_id').values('entry_id')) for x in
                           self.pool_stage.pool_set.all()]
        self.assertEqual(p_entries_before, p_entries_after)

    def test_confirm_pools_change_of_entries(self):
        self.c.force_login(self.manager)
        e = EntryFactory(competition=self.competition)
        self.pool_stage.start(3)
        self.stage.state = Stage.READY
        self.stage.save()
        pools_before = list(self.pool_stage.pool_set.all())
        p_entries_before = [list(x.poolentry_set.order_by('entry_id').values('entry_id')) for x in pools_before]
        intended_new_pools = {x: list(map(lambda z: z['entry_id'], y)) for x, y in enumerate(p_entries_before)}
        intended_new_pools[0][0] = e.id
        out = self.c.post(self.target, {'type': 'confirm_pools', 'pools': json.dumps(intended_new_pools)})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'pool entry mismatch',
                                           'verbose_reason': 'Manipulation of entry ids detected'})
        self.pool_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(3, self.pool_stage.pool_set.count())
        self.assertEqual(Stage.READY, self.stage.state)
        self.assertEqual(pools_before, list(self.pool_stage.pool_set.all()))
        p_entries_after = [list(x.poolentry_set.order_by('entry_id').values('entry_id')) for x in
                           self.pool_stage.pool_set.all()]
        self.assertEqual(p_entries_before, p_entries_after)

    def test_confirm_pools_change_pool_count(self):
        self.c.force_login(self.manager)
        self.pool_stage.start(3)
        self.stage.state = Stage.READY
        self.stage.save()
        pools_before = list(self.pool_stage.pool_set.all())
        p_entries_before = [list(x.poolentry_set.order_by('entry_id').values('entry_id')) for x in pools_before]
        intended_new_pools = {x: list(map(lambda z: z['entry_id'], y)) for x, y in enumerate(p_entries_before)}
        intended_new_pools.__delitem__(0)
        out = self.c.post(self.target, {'type': 'confirm_pools', 'pools': json.dumps(intended_new_pools)})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'pool count mismatch',
                                           'verbose_reason': 'Number of pools submitted does not match number of pools '
                                                             'in this round'})
        self.pool_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(3, self.pool_stage.pool_set.count())
        self.assertEqual(Stage.READY, self.stage.state)
        self.assertEqual(pools_before, list(self.pool_stage.pool_set.all()))
        p_entries_after = [list(x.poolentry_set.order_by('entry_id').values('entry_id')) for x in
                           self.pool_stage.pool_set.all()]
        self.assertEqual(p_entries_before, p_entries_after)

    def test_confirm_pools_bad_state(self):
        self.c.force_login(self.manager)
        self.pool_stage.start(3)
        for state in [Stage.NOT_STARTED, Stage.STARTED, Stage.FINISHED, Stage.LOCKED]:
            self.stage.state = state
            self.stage.save()
            pools_before = list(self.pool_stage.pool_set.all())
            out = self.c.post(self.target, {'type': 'confirm_pools'})
            self.assertJSONEqual(out.content, {'success': False,
                                               'reason': 'incorrect state',
                                               'verbose_reason': 'Stage not in ready state'})
            self.pool_stage.refresh_from_db()
            self.stage.refresh_from_db()
            self.assertEqual(self.pool_stage.pool_set.count(), 3)
            self.assertEqual(self.stage.state, state)
            self.assertEqual(list(self.pool_stage.pool_set.all()), pools_before)

    def test_bad_post_type(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'anything'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'unrecognised request',
                                           'verbose_reason': 'unrecognised request'})

    def test_finish_stage_base(self):
        self.c.force_login(self.manager)
        self.pool_stage.start(3)
        self.stage.state = Stage.STARTED
        self.stage.save()
        for pool in self.pool_stage.pool_set.all():
            make_boring_results(pool)
        out = self.c.post(self.target, {'type': 'finish_stage'})
        self.assertJSONEqual(out.content, {'success': True})
        self.stage.refresh_from_db()
        self.assertEqual(self.stage.state, Stage.FINISHED)

    def test_finish_stage_not_complete(self):
        self.c.force_login(self.manager)
        self.pool_stage.start(3)
        self.stage.state = Stage.STARTED
        self.stage.save()
        out = self.c.post(self.target, {'type': 'finish_stage'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'stage not finished',
                                           'verbose_reason': 'stage not finished'})
        self.stage.refresh_from_db()
        self.assertEqual(self.stage.state, Stage.STARTED)

    def test_finish_stage_bad_state(self):
        self.c.force_login(self.manager)
        self.pool_stage.start(3)
        for state in [Stage.NOT_STARTED, Stage.READY, Stage.FINISHED, Stage.LOCKED]:
            self.stage.state = state
            self.stage.save()
            out = self.c.post(self.target, {'type': 'finish_stage'})
            self.assertJSONEqual(out.content, {'success': False,
                                               'reason': 'incorrect state',
                                               'verbose_reason': 'stage not currently running'})
            self.stage.refresh_from_db()
            self.assertEqual(self.stage.state, state)
