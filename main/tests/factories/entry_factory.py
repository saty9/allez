import factory
from main.models import Entry
from .competitor_factory import UniqueClubCompetitorFactory
from .organisation_factory import OrganisationFactory


class EntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entry

    class Params:
        organisation = factory.SubFactory(OrganisationFactory)

    state = Entry.CHECKED_IN
    competitor = factory.LazyAttribute(lambda x: UniqueClubCompetitorFactory(organisation=x.organisation))
