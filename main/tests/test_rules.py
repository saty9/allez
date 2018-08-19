from main.tests.factories.competition_factory import PreAddedCompetitionOfSize
from main.tests.factories.org_member_factory import ManagerFactory, DTFactory, OrgMemberFactory
from main.tests.factories.organisation_factory import OrganisationFactory
from main.tests.factories.referee_factory import RefereeFactory
from django.test import TestCase, Client
from main.models import Stage
from main import rules

class TestRules(TestCase):

    def setUp(self):
        self.c = Client()
        self.competition = PreAddedCompetitionOfSize(entries__num_of_entries=8)
        self.org = self.competition.organisation
        self.manager = ManagerFactory(organisation=self.org).user
        self.dt = DTFactory(organisation=self.org).user
        self.applicant = OrgMemberFactory(organisation=self.org).user
        org = OrganisationFactory()
        self.wrong_org_manager = ManagerFactory(organisation=org).user

    def test_get_organisation(self):
        num = 1
        # Organisation
        result = rules.get_organisation(self.org)
        self.assertEqual(result, self.org)
        # Competition
        result = rules.get_organisation(self.competition)
        self.assertEqual(result, self.org)
        # Stage
        stage = self.competition.stage_set.first()
        result = rules.get_organisation(stage)
        self.assertEqual(result, self.org)
        # Pool stage
        stage = self.competition.stage_set.create(type=Stage.POOL, number=num)
        test_object = stage.poolstage_set.first()
        result = rules.get_organisation(test_object)
        self.assertEqual(result, self.org)
        num += 1
        # Cull Stage
        stage = self.competition.stage_set.create(type=Stage.CULL, number=num)
        test_object = stage.cullstage_set.first()
        result = rules.get_organisation(test_object)
        self.assertEqual(result, self.org)
        num += 1
        # De Stage
        stage = self.competition.stage_set.create(type=Stage.DE, number=num)
        test_object = stage.destage_set.first()
        result = rules.get_organisation(test_object)
        self.assertEqual(result, self.org)
        num += 1
        # Add Stage
        stage = self.competition.stage_set.create(type=Stage.ADD, number=num)
        test_object = stage.addstage_set.first()
        result = rules.get_organisation(test_object)
        self.assertEqual(result, self.org)
        num += 1

    def test_get_organisation_pool(self):
        # Pool
        stage = self.competition.stage_set.create(type=Stage.POOL, number=1)
        pool_stage = stage.poolstage_set.first()
        pool_stage.start(1)
        test_object = pool_stage.pool_set.first()
        result = rules.get_organisation(test_object)
        self.assertEqual(result, self.org)

    def test_get_organisation_de(self):
        # DeTable
        stage = self.competition.stage_set.create(type=Stage.DE, number=1)
        de_stage = stage.destage_set.first()
        de_stage.start()
        test_object = de_stage.detable_set.first()
        result = rules.get_organisation(test_object)
        self.assertEqual(result, self.org)

    def test_predicate_is_dt(self):
        assert rules.is_dt(self.manager, self.competition)
        assert rules.is_dt(self.dt, self.competition)
        self.assertFalse(rules.is_dt(self.applicant, self.competition))
        self.assertFalse(rules.is_dt(self.wrong_org_manager, self.competition))

    def test_predicate_is_manager(self):
        assert rules.is_manager(self.manager, self.competition)
        self.assertFalse(rules.is_manager(self.dt, self.competition))
        self.assertFalse(rules.is_manager(self.applicant, self.competition))
        self.assertFalse(rules.is_manager(self.wrong_org_manager, self.competition))

    def test_predicate_is_referee_for_pool(self):
        ref = RefereeFactory(competition=self.competition)
        other_ref = RefereeFactory(competition=self.competition)
        stage = self.competition.stage_set.create(state=Stage.STARTED, type=Stage.POOL, number=1)
        pool_stage = stage.poolstage_set.first()
        pool_stage.start(1)
        pool = pool_stage.pool_set.first()
        pool.referee = ref
        pool.save()
        assert rules.is_referee_for_pool(ref.user, pool)
        self.assertFalse(rules.is_referee_for_pool(other_ref.user, pool))
        self.assertFalse(rules.is_referee_for_pool(self.manager, pool))

    def test_predicate_is_referee_for_de(self):
        ref = RefereeFactory(competition=self.competition)
        other_ref = RefereeFactory(competition=self.competition)
        stage = self.competition.stage_set.create(state=Stage.STARTED, type=Stage.DE, number=1)
        de_stage = stage.destage_set.first()
        de_stage.start()
        de_table = de_stage.detable_set.first()
        de_table_entry = de_table.detableentry_set.first()
        de_table_entry.referee = ref
        assert rules.is_referee_for_de(ref.user, de_table_entry)
        self.assertFalse(rules.is_referee_for_de(other_ref.user, de_table_entry))
        self.assertFalse(rules.is_referee_for_de(self.manager, de_table_entry))
