import graphene

from main.models import Entry
from main.schema.competitor_type import CompetitorType


class EntryType(graphene.ObjectType):
    competitor = graphene.Field(CompetitorType, required=True)
    id = graphene.ID(required=True)

    @staticmethod
    def resolve_id(root: Entry, info, **kwargs):
        return root.id

    @staticmethod
    def resolve_competitor(root: Entry, info, **kwargs):
        return root.competitor