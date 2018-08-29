from ..factories.competition_factory import BaseCompetitionFactory
from ..factories.competitor_factory import CompetitorFactory
from ..factories.club_factory import ClubFactory
from django.test import TestCase
from main.models import Competition, Club


class TestCompetition(TestCase):

    def setUp(self):
        self.competition = BaseCompetitionFactory()  # type: Competition
        self.org = self.competition.organisation

    def test_add_entry_base(self):
        c1 = CompetitorFactory(organisation=self.org)
        club = ClubFactory()
        e = self.competition.add_entry(c1.license_number, c1.name, club.name)
        self.assertEqual(e.club, club)
        self.assertEqual(e.competitor, c1)
        self.assertEqual(e.competition, self.competition)

    def test_add_entry_new_club(self):
        c1 = CompetitorFactory(organisation=self.org)
        club = ClubFactory.build()
        e = self.competition.add_entry(c1.license_number, c1.name, club.name)
        self.assertEqual(e.club.name, club.name)
        self.assertEqual(e.competitor, c1)
        self.assertEqual(e.competition, self.competition)

    def test_add_entry_new_competitor(self):
        c1 = CompetitorFactory.build(organisation=self.org)
        club = ClubFactory()
        e = self.competition.add_entry(c1.license_number, c1.name, club.name)
        self.assertEqual(e.club, club)
        self.assertEqual(e.competitor.name, c1.name)
        self.assertEqual(e.competitor.license_number, c1.license_number)
        self.assertEqual(e.competition, self.competition)

    def test_add_entry_simplified_club_name(self):
        c1 = CompetitorFactory(organisation=self.org)
        club = Club.objects.create(name="Strathallan School Fencing Club")
        e = self.competition.add_entry(c1.license_number, c1.name, "Strathallan school fc")
        self.assertEqual(e.club, club)
        self.assertEqual(e.competitor, c1)
        self.assertEqual(e.competition, self.competition)

    def test_add_entry_same_competitor_twice(self):
        c1 = CompetitorFactory(organisation=self.org)
        club1 = ClubFactory()
        club2 = ClubFactory()
        e = self.competition.add_entry(c1.license_number, c1.name, club1.name)
        e = self.competition.add_entry(c1.license_number, c1.name, club2.name)
        self.assertEqual(e.club, club2)
        self.assertEqual(e.competitor, c1)
        self.assertEqual(e.competition, self.competition)
        self.assertEqual(self.competition.entry_set.count(), 1)
