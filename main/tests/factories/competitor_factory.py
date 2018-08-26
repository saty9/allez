import factory
from main.models import Competitor


class CompetitorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Competitor

    license_number = factory.Sequence(lambda n: "TEST_LI#{0:04}".format(n))
    name = factory.Faker('name')


