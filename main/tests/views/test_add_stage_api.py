from django.db.models import Max

from ..factories.competition_factory import CompetitionOfSize
from ..factories.org_member_factory import ManagerFactory
from ..factories.organisation_factory import OrganisationFactory
from django.test import TestCase, Client
from django.urls import reverse
from main.models import Stage


class TestAddStageAPI(TestCase):

    def setUp(self):
        self.c = Client()
        self.competition = CompetitionOfSize(entries__num_of_entries=8)
        self.stage = self.competition.stage_set.create(state=Stage.NOT_STARTED, type=Stage.ADD, number=1)
        self.add = self.stage.addstage_set.first()
        self.manager = ManagerFactory(organisation=self.competition.organisation).user
        org = OrganisationFactory()
        self.wrong_org_manager = ManagerFactory(organisation=org).user
        self.target = reverse('main/stage_endpoint', kwargs={'stage_id': self.stage.id})

    def test_authorization_block(self):
        out = self.c.post(self.target, {'type': 'something'})
        unauthorised_message = {'success': False, 'reason': 'NotLoggedIn'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

        self.c.force_login(self.wrong_org_manager)
        out = self.c.post(self.target, {'type': 'something'})
        unauthorised_message = {'success': False, 'reason': 'InsufficientPermissions'}
        self.assertJSONEqual(out.content, unauthorised_message, 'Unauthenticated posts should be blocked')

    def test_post_bad_type(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'anything_else'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'unrecognised request',
                                           'verbose_reason': 'unrecognised request'})

    def test_add_entries_base(self):
        self.c.force_login(self.manager)
        entry_ids = list(self.competition.entry_set.values_list('pk', flat=True)[:5])
        out = self.c.post(self.target, {'type': 'add_entries', 'ids': entry_ids})
        self.stage.refresh_from_db()
        self.assertJSONEqual(out.content, {'success': True})
        self.assertEqual(self.stage.state, Stage.READY)
        self.assertListEqual(entry_ids, list(self.add.addcompetitor_set.order_by('sequence').values_list('entry_id', flat=True)))

    def test_add_entries_already_added_entry(self):
        self.c.force_login(self.manager)
        entry_ids = list(self.competition.entry_set.values_list('pk', flat=True)[:5])
        e = self.competition.entry_set.get(pk=entry_ids[0])
        stage = self.competition.stage_set.create(state=Stage.FINISHED, type=Stage.ADD, number=0)
        stage.addstage_set.first().add_entries([e])
        out = self.c.post(self.target, {'type': 'add_entries', 'ids': entry_ids})
        self.stage.refresh_from_db()
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'bad_entry',
                                           'verbose_reason':
                                           'one of these entries has already been added or is not in this competition'})
        self.assertEqual(self.stage.state, Stage.NOT_STARTED)
        self.assertListEqual([], list(self.add.addcompetitor_set.values_list('entry_id', flat=True)))

    def test_add_entries_bad_entry(self):
        self.c.force_login(self.manager)
        entry_ids = list(self.competition.entry_set.values_list('pk', flat=True)[:5])
        new_id = self.competition.entry_set.aggregate(Max('pk'))['pk__max'] + 1
        entry_ids.append(new_id)
        out = self.c.post(self.target, {'type': 'add_entries', 'ids': entry_ids})
        self.stage.refresh_from_db()
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'bad_entry',
                                           'verbose_reason':
                                           'one of these entries has already been added or is not in this competition'})
        self.assertEqual(self.stage.state, Stage.NOT_STARTED)
        self.assertListEqual([], list(self.add.addcompetitor_set.values_list('entry_id', flat=True)))

    def test_add_entries_bad_state(self):
        self.c.force_login(self.manager)
        entry_ids = list(self.competition.entry_set.values_list('pk', flat=True)[:5])
        for state in [Stage.READY, Stage.STARTED, Stage.FINISHED, Stage.LOCKED]:
            self.stage.state = state
            self.stage.save()
            out = self.c.post(self.target, {'type': 'add_entries', 'ids': entry_ids})
            self.stage.refresh_from_db()
            self.assertJSONEqual(out.content, {'success': False,
                                               'reason': "incorrect state",
                                               'verbose_reason': 'Stage not in NOT_STARTED state'})
            self.assertEqual(self.stage.state, state)
            self.assertListEqual([], list(self.add.addcompetitor_set.values_list('entry_id', flat=True)))
