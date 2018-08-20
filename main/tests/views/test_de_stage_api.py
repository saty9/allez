from ..factories.competition_factory import PreAddedCompetitionOfSize
from ..factories.org_member_factory import ManagerFactory
from ..factories.organisation_factory import OrganisationFactory
from django.test import TestCase, Client
from django.urls import reverse
from main.models import Stage, DeStage


class TestDeStageAPI(TestCase):

    def setUp(self):
        self.c = Client()
        self.competition = PreAddedCompetitionOfSize(entries__num_of_entries=30)
        self.stage = self.competition.stage_set.create(state=Stage.NOT_STARTED, type=Stage.DE, number=1)
        self.de_stage = self.stage.destage_set.first()  # type: DeStage
        self.manager = ManagerFactory(organisation=self.competition.organisation).user
        org = OrganisationFactory()
        self.wrong_org_manager = ManagerFactory(organisation=org).user
        self.target = reverse('main/stage_endpoint', kwargs={'stage_id': self.stage.id})

    def test_authorization_block(self):
        out = self.c.post(self.target, {'type': 'start'})
        unauthorised_message = {'success': False, 'reason': 'NotLoggedIn'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

        self.c.force_login(self.wrong_org_manager)
        out = self.c.post(self.target, {'type': 'start'})
        unauthorised_message = {'success': False, 'reason': 'InsufficientPermissions'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

    def test_generate_start_base(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'start_stage'})
        self.assertJSONEqual(out.content, {'success': True})
        self.de_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(self.de_stage.detable_set.count(), 1)
        self.assertEqual(self.stage.state, Stage.STARTED)

    def test_generate_start_previous_unfinished(self):
        self.c.force_login(self.manager)
        add_stage = self.competition.stage_set.get(number=0)
        add_stage.state = Stage.READY
        add_stage.save()
        out = self.c.post(self.target, {'type': 'start_stage'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'previous stage incomplete',
                                           'verbose_reason': 'Previous stage not finished yet'})
        self.de_stage.refresh_from_db()
        self.stage.refresh_from_db()
        self.assertEqual(self.de_stage.detable_set.count(), 0)
        self.assertEqual(self.stage.state, Stage.NOT_STARTED)

    def test_generate_start_bad_state(self):
        self.c.force_login(self.manager)
        for state in [Stage.READY, Stage.STARTED, Stage.FINISHED, Stage.LOCKED]:
            self.stage.state = state
            self.stage.save()
            out = self.c.post(self.target, {'type': 'start_stage'})
            self.assertJSONEqual(out.content, {'success': False,
                                               'reason': 'invalid state',
                                               'verbose_reason': 'Stage has already started'})
            self.de_stage.refresh_from_db()
            self.stage.refresh_from_db()
            self.assertEqual(self.de_stage.detable_set.count(), 0)
            self.assertEqual(self.stage.state, state)
