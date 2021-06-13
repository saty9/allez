import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType

from main.models import Pool, PoolBout, Entry
from .entry_type import EntryType
from .pool_results_type import PoolResultsType


class PoolType(DjangoObjectType):
    results = graphene.List(PoolResultsType)
    participants = graphene.List(EntryType, required=True)
    class Meta:
        model = Pool
        fields = ("number",)

    @staticmethod
    def resolve_participants(root, info, **kwargs):
        return Entry.objects.order_by("poolentry__number").filter(poolentry__pool=root)

    def resolve_results(root: Pool, info, **kwargs):
        return PoolBout.objects.filter(Q(fencerA__pool=root) | Q(fencerB__pool=root))