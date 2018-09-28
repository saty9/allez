from main.tests.factories.competition_factory import PreAddedCompetitionOfSize
from main.tests.factories.org_member_factory import ManagerFactory
from ui.tests.ui_test_case import UITestCase
from django.urls import reverse
from main.models import Stage, Competition, Organisation


class TestPoolStageManagementUI(UITestCase):

    def setUp(self):
        self.comp = PreAddedCompetitionOfSize(entries__num_of_entries=8)  # type: Competition
        self.organisation = self.comp.organisation  # type: Organisation
        self.manager = ManagerFactory(organisation=self.organisation).user
        self.stage = self.comp.stage_set.create(type=Stage.CULL, number=1, state=Stage.NOT_STARTED)
        self.target = reverse('ui/manage_stage', args=[self.organisation.slug, self.comp.id, self.stage.id])

    def test_cull_stage_management(self):
        self.three_perm_check(self.target, self.manager, 302, 403, 200)

    def test_cull_stage_management_ready(self):
        self.stage.state = Stage.READY
        self.stage.save()
        cull = self.stage.cullstage_set.first()
        cull.number = 3
        cull.save()
        self.three_perm_check(self.target, self.manager, 302, 403, 200)

    def test_cull_stage_management_finished(self):
        self.stage.state = Stage.FINISHED
        self.stage.save()
        cull = self.stage.cullstage_set.first()
        cull.number = 3
        cull.save()
        self.three_perm_check(self.target, self.manager, 302, 403, 200)
