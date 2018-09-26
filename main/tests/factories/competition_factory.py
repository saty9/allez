import factory
from main.models import Competition, Stage
from django.utils import timezone
from .entry_factory import EntryFactory
from .organisation_factory import OrganisationFactory


class BaseCompetitionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Competition

    organisation = factory.SubFactory(OrganisationFactory)
    name = "Test Competition"
    date = factory.LazyFunction(timezone.now().date)


class CompetitionOfSize(BaseCompetitionFactory):

    @factory.post_generation
    def entries(self, create, extracted, **kwargs):
        if not create:
            return
        if 'num_of_entries' not in kwargs:
            num_of_entries = 1
        else:
            num_of_entries = kwargs['num_of_entries']

        for n in range(num_of_entries):
            EntryFactory(competition=self, organisation=self.organisation, seed=n)


class PreAddedCompetitionOfSize(CompetitionOfSize):

    @factory.post_generation
    def add_stage(self, create, extracted, **kwargs):
        if not create:
            return
        add_stage = self.stage_set.create(type=Stage.ADD, state=Stage.FINISHED, number=0)
        for index, x in enumerate(self.entry_set.all()):
            add_stage.addstage_set.first().addcompetitor_set.create(entry=x, sequence=index)
