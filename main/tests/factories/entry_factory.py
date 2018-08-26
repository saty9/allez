import factory
from main.models import Entry
from .competitor_factory import CompetitorFactory
from .organisation_factory import OrganisationFactory
from .club_factory import ClubFactory


class EntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entry

    class Params:
        organisation = factory.SubFactory(OrganisationFactory)

    state = Entry.CHECKED_IN
    competitor = factory.LazyAttribute(lambda x: CompetitorFactory(organisation=x.organisation))
    club = factory.SubFactory(ClubFactory)
