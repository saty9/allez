from main.tests.factories.competition_factory import BaseCompetitionFactory
from main.tests.factories.org_member_factory import ManagerFactory
from main.tests.factories.organisation_factory import OrganisationFactory
from main.tests.factories.entry_factory import EntryFactory
from ui.tests.ui_test_case import UITestCase
from django.urls import reverse


class TestCheckInUI(UITestCase):

    def setUp(self):
        self.organisation = OrganisationFactory()  # type: OrganisationFactory
        self.manager = ManagerFactory(organisation=self.organisation).user

    def test_check_in_no_competition(self):
        target = reverse('ui/check_in', args=[self.organisation.slug, 5])
        self.three_perm_check(target, self.manager, 302, 404, 404)

    def test_check_in_no_entries(self):
        c = BaseCompetitionFactory(organisation=self.organisation)
        target = reverse('ui/check_in', args=[self.organisation.slug, c.id])
        self.three_perm_check(target, self.manager, 302, 403, 200)

    def test_check_in_one_entry(self):
        c = BaseCompetitionFactory(organisation=self.organisation)
        EntryFactory(competition=c)
        target = reverse('ui/check_in', args=[self.organisation.slug, c.id])
        self.three_perm_check(target, self.manager, 302, 403, 200)

    def test_check_in_many_entries(self):
        c = BaseCompetitionFactory(organisation=self.organisation)
        EntryFactory.create_batch(5, competition=c)
        target = reverse('ui/check_in', args=[self.organisation.slug, c.id])
        self.three_perm_check(target, self.manager, 302, 403, 200)
