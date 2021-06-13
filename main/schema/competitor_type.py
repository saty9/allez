from graphene_django.types import DjangoObjectType

from main.models import Competitor


class CompetitorType(DjangoObjectType):
    class Meta:
        model = Competitor
        fields = ("name",)