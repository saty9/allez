from main.tests.factories.competition_factory import PreAddedCompetitionOfSize
from main.tests.factories.org_member_factory import ManagerFactory
from main.tests.factories.organisation_factory import OrganisationFactory
from main.tests.factories.entry_factory import EntryFactory
from ui.tests.ui_test_case import UITestCase
from django.urls import reverse


class TestCheckInUI(UITestCase):

    def setUp(self):
        self.competition = PreAddedCompetitionOfSize(entries__num_of_entries=10)
        self.manager = ManagerFactory(organisation=self.competition.organisation).user

    def test_stage_ranking(self):
        stage = self.competition.stage_set.first()
        target = reverse('ui/stage_ranking', args=[self.competition.organisation.slug, self.competition.id, stage.id])
        self.three_perm_check(target, self.manager, 200, 200, 200)
