from ..factories.competition_factory import PreAddedCompetitionOfSize
from ..factories.org_member_factory import ManagerFactory
from ..factories.organisation_factory import OrganisationFactory
from django.test import TestCase, Client
from django.urls import reverse
from main.models import Stage


class TestCullStageAPI(TestCase):

    def setUp(self):
        self.c = Client()
        self.competition = PreAddedCompetitionOfSize(entries__num_of_entries=8)
        self.stage = self.competition.stage_set.create(state=Stage.NOT_STARTED, type=Stage.CULL, number=1)
        self.cull = self.stage.cullstage_set.first()
        self.manager = ManagerFactory(organisation=self.competition.organisation).user
        org = OrganisationFactory()
        self.wrong_org_manager = ManagerFactory(organisation=org).user
        self.target = reverse('main/stage_endpoint', kwargs={'stage_id': self.stage.id})

    def test_authorization_block(self):
        out = self.c.post(self.target, {'type': 'set_cull_level'})
        unauthorised_message = {'success': False, 'reason': 'NotLoggedIn'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

        self.c.force_login(self.wrong_org_manager)
        out = self.c.post(self.target, {'type': 'set_cull_level'})
        unauthorised_message = {'success': False, 'reason': 'InsufficientPermissions'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

    def test_set_number_base(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'set_cull_level', 'cull_number': 5})
        self.assertJSONEqual(out.content, {'success': True})
        self.cull.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(self.cull.number, 5)
        self.assertEqual(self.stage.state, Stage.READY)

    def test_set_number_bad_state(self):
        self.c.force_login(self.manager)
        for state in [Stage.READY, Stage.STARTED, Stage.FINISHED, Stage.LOCKED]:
            self.stage.state = state
            self.stage.save()
            before = self.cull.number
            out = self.c.post(self.target, {'type': 'set_cull_level', 'cull_number': 5})
            self.assertJSONEqual(out.content, {'success': False,
                                               'reason': "incorrect state",
                                               'verbose_reason': "stage not in ready state"})
            self.cull.refresh_from_db()
            self.assertEqual(self.cull.number, before)

    def test_set_number_bad_number(self):
        self.c.force_login(self.manager)
        before = self.cull.number
        out = self.c.post(self.target, {'type': 'set_cull_level', 'cull_number': 1})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': "invalid cull number",
                                           'verbose_reason': "cull number must be > 2 and < size of stages input "})
        self.cull.refresh_from_db()
        self.assertEqual(self.cull.number, before)

        out = self.c.post(self.target, {'type': 'set_cull_level', 'cull_number': len(self.stage.input())})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': "invalid cull number",
                                           'verbose_reason': "cull number must be > 2 and < size of stages input "})
        self.cull.refresh_from_db()
        self.assertEqual(self.cull.number, before)

    def test_set_number_previous_stage_incomplete(self):
        self.c.force_login(self.manager)
        previous = Stage.objects.get(competition=self.competition, number=self.stage.number - 1)
        previous.state = Stage.READY
        previous.save()
        before = self.cull.number
        out = self.c.post(self.target, {'type': 'set_cull_level', 'cull_number': 4})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': "previous stage incomplete",
                                           'verbose_reason': "previous stage incomplete"})
        self.cull.refresh_from_db()
        self.assertEqual(self.cull.number, before)

    def test_confirm_cull_base(self):
        self.c.force_login(self.manager)
        self.stage.state = Stage.READY
        self.cull.number = 5
        self.stage.save()
        out = self.c.post(self.target, {'type': 'confirm_cull'})
        self.assertJSONEqual(out.content, {'success': True})
        self.stage.refresh_from_db()
        self.assertEqual(self.stage.state, Stage.FINISHED)

    def test_confirm_cull_unset_number(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'confirm_cull'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'number not set',
                                           'verbose_reason': 'number not set'})
        self.stage.refresh_from_db()
        self.assertEqual(self.stage.state, Stage.NOT_STARTED)

    def test_confirm_cull_already_done(self):
        self.c.force_login(self.manager)
        for state in [Stage.STARTED, Stage.FINISHED, Stage.LOCKED]:
            self.stage.state = state
            self.stage.save()
            out = self.c.post(self.target, {'type': 'confirm_cull'})
            self.assertJSONEqual(out.content, {'success': False,
                                               'reason': 'stage already complete',
                                               'verbose_reason': 'stage already complete'})
            self.stage.refresh_from_db()
            self.assertEqual(self.stage.state, state)
