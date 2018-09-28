from main.tests.factories.competition_factory import PreAddedCompetitionOfSize
from main.tests.factories.org_member_factory import ManagerFactory
from ui.tests.ui_test_case import UITestCase
from django.urls import reverse
from main.models import Stage, Competition, Organisation


class TestDeStageManagementUI(UITestCase):

    def setUp(self):
        self.comp = PreAddedCompetitionOfSize(entries__num_of_entries=8)  # type: Competition
        self.organisation = self.comp.organisation  # type: Organisation
        self.manager = ManagerFactory(organisation=self.organisation).user
        self.stage = self.comp.stage_set.create(type=Stage.DE, number=1, state=Stage.NOT_STARTED)
        self.target = reverse('ui/manage_stage', args=[self.organisation.slug, self.comp.id, self.stage.id])

    def test_de_stage_management(self):
        self.three_perm_check(self.target, self.manager, 302, 403, 200)

    def test_de_stage_management_started(self):
        self.stage.state = Stage.STARTED
        self.stage.save()
        self.stage.destage_set.first().start()
        self.three_perm_check(self.target, self.manager, 302, 403, 200)

    def test_de_table_management(self):
        self.stage.state = Stage.STARTED
        self.stage.save()
        self.stage.destage_set.first().start()
        table = self.stage.destage_set.first().detable_set.first()
        target = reverse('ui/dt_manage_de', args=[table.id])
        self.three_perm_check(target, self.manager, 302, 403, 200)
