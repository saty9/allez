from main.tests.factories.org_member_factory import ManagerFactory
from main.tests.factories.organisation_factory import OrganisationFactory
from main.tests.factories.user_factory import UserFactory
from ui.tests.ui_test_case import UITestCase
from django.urls import reverse


class TestOrganisationUI(UITestCase):

    def test_organisation_list(self):
        user = UserFactory()
        target = reverse('ui/organisation/list')
        self.three_perm_check(target, user, 200, 200, 200)

    def test_organisation_list_one(self):
        organisation = OrganisationFactory()  # type: Organisation
        manager = ManagerFactory(organisation=organisation).user
        target = reverse('ui/organisation/list')
        self.three_perm_check(target, manager, 200, 200, 200)

    def test_organisation_list_many(self):
        organisation = OrganisationFactory.create_batch(5)  # type: Organisation
        manager = ManagerFactory(organisation=organisation[0]).user
        target = reverse('ui/organisation/list')
        self.three_perm_check(target, manager, 200, 200, 200)

    def test_organisation_show(self):
        organisation = OrganisationFactory()  # type: Organisation
        manager = ManagerFactory(organisation=organisation).user
        target = reverse('ui/organisation/show', args=[organisation.slug])
        self.three_perm_check(target, manager, 302, 200, 200)
