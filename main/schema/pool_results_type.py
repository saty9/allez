import graphene

from .entry_type import EntryType
from ..models import PoolBout


class PoolResultsType(graphene.ObjectType):
    a = graphene.Field(EntryType, required=True)
    b = graphene.Field(EntryType, required=True)
    a_score = graphene.Int()
    a_victory = graphene.Boolean()

    @staticmethod
    def resolve_a(root: PoolBout, info, **kwargs):
        return root.fencerA.entry

    @staticmethod
    def resolve_b(root: PoolBout, info, **kwargs):
        return root.fencerB.entry

    @staticmethod
    def resolve_a_score(root: PoolBout, info, **kwargs):
        return root.scoreA

    @staticmethod
    def resolve_a_victory(root: PoolBout, info, **kwargs):
        return root.victoryA
