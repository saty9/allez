import rules
from main import models


@rules.predicate
def is_referee_for_pool(user, pool: models.Pool):
    return pool.referee.user == user


@rules.predicate
def is_referee_for_de(user, de_entry: models.DeTableEntry):
    return de_entry.referee.user == user


@rules.predicate
def is_dt_pool(user, pool):
    return is_dt(user, pool.stage.competition)


@rules.predicate
def is_dt_de_table_entry(user, de_entry: models.DeTableEntry):
    return is_dt(user, de_entry.table.de.stage.competition)


def is_dt(user, competition):
    return models.OrganisationMembership.objects.filter(organisation=competition.organisation, user=user).exists()


rules.add_perm('main.change_pool', is_referee_for_pool | is_dt_pool)
rules.add_perm('main.change_de_table_entry', is_referee_for_de | is_dt_de_table_entry)
