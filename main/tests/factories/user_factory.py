import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('username')
    password = factory.Faker('sha256')


class SuperUserFactory(UserFactory):
    is_superuser = True
    is_staff = True
