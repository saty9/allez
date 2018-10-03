from main.tests.factories.competition_factory import CompetitionOfSize
from main.tests.factories.org_member_factory import ManagerFactory
from main.tests.factories.organisation_factory import OrganisationFactory
from main.tests.factories.entry_factory import EntryFactory
from ui.tests.ui_test_case import UITestCase
from django.urls import reverse
from main.models import Stage, Competition, Organisation


class TestAddStageManagementUI(UITestCase):

    def setUp(self):
        self.comp = CompetitionOfSize(entries__num_of_entries=8)  # type: Competition
        self.organisation = self.comp.organisation  # type: Organisation
        self.manager = ManagerFactory(organisation=self.organisation).user
        self.stage = self.comp.stage_set.create(type=Stage.ADD, number=0, state=Stage.NOT_STARTED)
        self.target = reverse('ui/manage_stage', args=[self.organisation.slug, self.comp.id, self.stage.id])

    def test_add_stage_management(self):
        self.three_perm_check(self.target, self.manager, 302, 403, 200)

    def test_add_stage_management_ready(self):
        self.stage.state = Stage.READY
        self.stage.save()
        self.three_perm_check(self.target, self.manager, 302, 403, 200)

    def test_add_stage_management_ready_with_entries(self):
        self.stage.state = Stage.READY
        self.stage.save()
        self.stage.addstage_set.first().add_entries(map(lambda x: [x], self.comp.entry_set.all()))
        self.three_perm_check(self.target, self.manager, 302, 403, 200)

    def test_add_stage_management_finished(self):
        self.stage.state = Stage.FINISHED
        self.stage.save()
        self.stage.addstage_set.first().add_entries(map(lambda x: [x], self.comp.entry_set.all()))
        self.three_perm_check(self.target, self.manager, 302, 403, 200)
