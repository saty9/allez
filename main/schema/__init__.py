import graphene
from graphene_django.types import DjangoObjectType

from main.models import Organisation, Competition, Stage, CullStage, PoolStage
from .pool_type import PoolType

class StageInterface(graphene.Interface):
    id = graphene.ID(required=True)
    state = graphene.Enum("StageState", Stage.states)
    stage_number = graphene.Int(required=True)

    @classmethod
    def resolve_type(cls, instance, info):
        if isinstance(instance, CullStage):
            return CullStageType
        if isinstance(instance, PoolStage):
            return PoolStageType
        return None


class StageTypeHelper(DjangoObjectType):
    class Meta:
        model = Stage
        interfaces = (StageInterface, )

    def resolve_id(root, info):
        return root.stage.id

    def resolve_stage_number(root, info):
        return root.stage.number


class CullStageType(StageTypeHelper):
    class Meta:
        model = CullStage
        interfaces = (StageInterface, )
        fields = ("number",)


class PoolStageType(StageTypeHelper):
    pools = graphene.List(PoolType)

    class Meta:
        model = PoolStage
        interfaces = (StageInterface,)
        fields = ("carry_previous_results",)

    def resolve_pools(root: PoolStage, info, **kwargs):
        return root.pool_set.all()


class StageType(graphene.ObjectType):
    class Meta:
        interfaces = (StageInterface,)
        possible_types = (CullStageType, PoolStageType)

    @classmethod
    def resolve_type(cls, instance: Stage, info):
        if (instance.type == Stage.CULL):
            return CullStageType
        if instance.type == Stage.POOL:
            return PoolStageType
        return None


class CompetitionType(DjangoObjectType):
    stages = graphene.List(StageInterface)

    class Meta:
        model = Competition
        fields = ("id", "name", "date")

    def resolve_stages(root: Competition, info, **kwargs):
        return map(lambda x: x.get_concrete_type(), root.stage_set.filter(type__in=[Stage.CULL, Stage.POOL]).all())


class OrganisationType(DjangoObjectType):
    competitions = graphene.List(CompetitionType)
    competition = graphene.Field(CompetitionType, id=graphene.ID(required=True))

    class Meta:
        model = Organisation
        fields = ("id", "name", "competitions")


    def resolve_competitions(root, info, **kwargs):
        return root.competition_set.all()

    def resolve_competition(root, info, id):
        return root.competition_set.get(pk=id)


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")
    organisations = graphene.List(OrganisationType)
    organisation = graphene.Field(OrganisationType, id=graphene.ID(required=True))

    def resolve_organisations(root, info, **kwargs):
        return Organisation.objects.all()

    def resolve_organisation(root, info, id):
        org = Organisation.objects.get(pk=id)
        return org


schema = graphene.Schema(query=Query, types=[CullStageType, PoolStageType])
