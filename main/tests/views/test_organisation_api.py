import json

from main.tests.factories.org_member_factory import ManagerFactory, OrgMemberFactory, DTFactory
from main.tests.factories.organisation_factory import OrganisationFactory
from main.tests.factories.user_factory import UserFactory
from main.tests.factories.entry_factory import EntryFactory
from main.tests.factories.competition_factory import BaseCompetitionFactory
from main.settings import MAX_AUTOCOMPLETE_RESPONSES
from django.test import TestCase, Client
from django.urls import reverse
from main.models import OrganisationMembership


class TestOrganisationAPI(TestCase):

    def setUp(self):
        self.c = Client()
        self.organisation = OrganisationFactory()  # type: Organisation
        self.manager = ManagerFactory(organisation=self.organisation).user
        self.target = reverse('main/organisation_endpoint', kwargs={'org_id': self.organisation.id})

    def test_accept_application_base(self):
        self.c.force_login(self.manager)
        applicant = OrgMemberFactory(organisation=self.organisation)
        out = self.c.post(self.target, {'type': 'accept_application',
                                        'user_id': applicant.user.id})
        self.assertJSONEqual(out.content, {'success': True})
        applicant.refresh_from_db()
        self.assertEqual(applicant.state, OrganisationMembership.DT)

    def test_accept_application_unauthorised(self):
        applicant = OrgMemberFactory(organisation=self.organisation)
        for user in [applicant.user, DTFactory(organisation=self.organisation).user]:
            self.c.force_login(user)
            out = self.c.post(self.target, {'type': 'accept_application',
                                            'user_id': applicant.user.id})
            self.assertJSONEqual(out.content, {'success': False,
                                               'reason': 'InsufficientPermissions'})
            applicant.refresh_from_db()
            self.assertEqual(applicant.state, OrganisationMembership.APPLICANT)

    def test_accept_application_already_full_member(self):
        applicant = ManagerFactory(organisation=self.organisation)
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'accept_application',
                                        'user_id': applicant.user.id})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': "already_full_member",
                                           'verbose_reason': "User is already a full member"})
        applicant.refresh_from_db()
        self.assertEqual(applicant.state, OrganisationMembership.MANAGER)

    def test_join_organisation_base(self):
        applicant = UserFactory()
        self.c.force_login(applicant)
        out = self.c.post(self.target, {'type': 'join_request',
                                        'user_id': applicant.id})
        self.assertJSONEqual(out.content, {'success': True})
        application = applicant.organisationmembership_set.get(organisation=self.organisation)
        self.assertEqual(application.state, OrganisationMembership.APPLICANT)

    def test_join_organisation_manager(self):
        applicant = UserFactory()
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'join_request',
                                        'user_id': applicant.id})
        self.assertJSONEqual(out.content, {'success': True})
        application = applicant.organisationmembership_set.get(organisation=self.organisation)
        self.assertEqual(application.state, OrganisationMembership.DT)

    def test_join_organisation_unauthorised(self):
        applicant = UserFactory()
        user = DTFactory(organisation=self.organisation).user
        self.c.force_login(user)
        out = self.c.post(self.target, {'type': 'join_request',
                                        'user_id': applicant.id})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'InsufficientPermissions'})
        self.assertEqual(applicant.organisationmembership_set.count(), 0)

    def test_join_organisation_already_applied(self):
        applicant = UserFactory()
        user = DTFactory(organisation=self.organisation).user
        self.c.force_login(user)
        out = self.c.post(self.target, {'type': 'join_request',
                                        'user_id': applicant.id})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'InsufficientPermissions'})
        self.assertEqual(applicant.organisationmembership_set.count(), 0)

    def test_competitor_autocomplete(self):
        user = DTFactory(organisation=self.organisation).user
        competition = BaseCompetitionFactory(organisation=self.organisation)
        for _ in range(8):
            EntryFactory(organisation=self.organisation, competition=competition)
        expected = self.organisation.competitor_set.first()
        self.c.force_login(user)
        out = self.c.get(self.target, {'type': 'autocomplete_competitor',
                                       'name': expected.name[0:5]})
        result = json.loads(out.content)
        expected_values = {'name': expected.name, 'license_number': expected.license_number,
                           'club_name': expected.entry_set.latest().club.name}
        self.assertIn(expected_values, result['competitors'])

    def test_competitor_autocomplete_short_string(self):
        user = DTFactory(organisation=self.organisation).user
        competition = BaseCompetitionFactory(organisation=self.organisation)
        for _ in range(8):
            EntryFactory(organisation=self.organisation, competition=competition)
        expected = self.organisation.competitor_set.first()
        self.c.force_login(user)
        out = self.c.get(self.target, {'type': 'autocomplete_competitor',
                                       'name': expected.name[0:2]})
        result = json.loads(out.content)
        self.assertEqual(len(result['competitors']), 0)

    def test_competitor_limit_response_length(self):
        user = DTFactory(organisation=self.organisation).user
        competition = BaseCompetitionFactory(organisation=self.organisation)
        for _ in range(MAX_AUTOCOMPLETE_RESPONSES + 1):
            EntryFactory(organisation=self.organisation, competition=competition)
        self.organisation.competitor_set.update(name="Roger Rabbit")
        self.c.force_login(user)
        out = self.c.get(self.target, {'type': 'autocomplete_competitor',
                                       'name': 'roger'})
        result = json.loads(out.content)
        self.assertEqual(len(result['competitors']), MAX_AUTOCOMPLETE_RESPONSES)

    def test_competitor_autocomplete_unauthorised(self):
        user = OrgMemberFactory(organisation=self.organisation).user
        competition = BaseCompetitionFactory(organisation=self.organisation)
        for _ in range(8):
            EntryFactory(organisation=self.organisation, competition=competition)
        expected = self.organisation.competitor_set.first()
        self.c.force_login(user)
        out = self.c.get(self.target, {'type': 'autocomplete_competitor',
                                       'name': expected.name[:5]})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'InsufficientPermissions'})

    def test_post_bad_type(self):
        self.c.force_login(self.manager)
        out = self.c.post(self.target, {'type': 'anything_else'})
        self.assertJSONEqual(out.content, {'success': False,
                                           'reason': 'unrecognised request',
                                           'verbose_reason': 'Unrecognised request'})
