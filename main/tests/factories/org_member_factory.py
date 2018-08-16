import factory
from main.models import OrganisationMembership
from .user_factory import UserFactory


class OrgMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganisationMembership

    user = factory.SubFactory(UserFactory)


class DTFactory(OrgMemberFactory):
    state = OrganisationMembership.DT


class ManagerFactory(OrgMemberFactory):
    state = OrganisationMembership.MANAGER
