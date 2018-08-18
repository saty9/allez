import factory
from main.models import Referee
from .user_factory import UserFactory


class RefereeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Referee

    user = factory.SubFactory(UserFactory)
