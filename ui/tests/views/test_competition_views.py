from main.tests.factories.competition_factory import BaseCompetitionFactory
from main.tests.factories.org_member_factory import ManagerFactory
from main.tests.factories.organisation_factory import OrganisationFactory
from main.tests.factories.entry_factory import EntryFactory
from ui.tests.ui_test_case import UITestCase
from django.urls import reverse
from main.models import Stage


class TestCompetitionUI(UITestCase):

    def setUp(self):
        self.organisation = OrganisationFactory()  # type: OrganisationFactory
        self.manager = ManagerFactory(organisation=self.organisation).user

    def test_competition_list_empty(self):
        target = reverse('ui/org/competitions', args=[self.organisation.slug])
        self.three_perm_check(target, self.manager, 200, 200, 200)

    def test_competition_list_one(self):
        target = reverse('ui/org/competitions', args=[self.organisation.slug])
        BaseCompetitionFactory(organisation=self.organisation)
        self.three_perm_check(target, self.manager, 200, 200, 200)

    def test_competition_list_many(self):
        target = reverse('ui/org/competitions', args=[self.organisation.slug])
        BaseCompetitionFactory.create_batch(3, organisation=self.organisation)
        self.three_perm_check(target, self.manager, 200, 200, 200)

    def test_competition_manage(self):
        comp = BaseCompetitionFactory(organisation=self.organisation)
        target = reverse('ui/manage_competition', args=[self.organisation.slug, comp.id])
        self.three_perm_check(target, self.manager, 302, 403, 200)

    def test_competition_manage_doesnt_exist(self):
        target = reverse('ui/manage_competition', args=[self.organisation.slug, 5])
        self.three_perm_check(target, self.manager, 302, 404, 404)

    def test_competition_with_stages(self):
        comp = BaseCompetitionFactory(organisation=self.organisation)
        comp.stage_set.create(type=Stage.ADD, number=0)
        target = reverse('ui/manage_competition', args=[self.organisation.slug, comp.id])
        self.three_perm_check(target, self.manager, 302, 403, 200)

    def test_competition_with_entries(self):
        comp = BaseCompetitionFactory(organisation=self.organisation)
        EntryFactory(competition=comp)
        target = reverse('ui/manage_competition', args=[self.organisation.slug, comp.id])
        self.three_perm_check(target, self.manager, 302, 403, 200)
        EntryFactory(competition=comp)
        self.three_perm_check(target, self.manager, 302, 403, 200)
