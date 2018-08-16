import factory
from main.models import Organisation


class OrganisationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organisation

    name = factory.Faker('company')
    email = factory.Faker('email')
    contactNumber = factory.Faker('msisdn')
    slug = factory.Faker('slug')
