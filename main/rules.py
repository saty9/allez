import rules
from main import models


def is_dt(user, competition):
    org_mem = models.OrganisationMembership
    dt_states = [org_mem.MANAGER, org_mem.DT]
    return models.OrganisationMembership.objects.\
        filter(organisation=competition.organisation, user=user, state__in=dt_states).exists()


@rules.predicate
def is_referee_for_pool(user, pool):
    if pool.referee:
        return pool.referee.user == user
    else:
        return False


@rules.predicate
def is_referee_for_de(user, de_entry):
    if de_entry.referee:
        return de_entry.referee.user == user
    else:
        return False


@rules.predicate
def is_dt_pool(user, pool):
    return is_dt(user, pool.stage.stage.competition)


@rules.predicate
def is_dt_de_table_entry(user, de_entry):
    return is_dt(user, de_entry.table.de.stage.competition)


@rules.predicate
def is_manager(user, test_object):
    if test_object.__class__ == models.Organisation:
        return models.OrganisationMembership.objects.\
            filter(organisation=test_object, user=user, state=models.OrganisationMembership.MANAGER).\
            exists()
    elif test_object.__class__ == models.Competition:
        return models.OrganisationMembership.objects.\
            filter(organisation=test_object.organisation, user=user, state=models.OrganisationMembership.MANAGER).\
            exists()
    raise ValueError('Unexpected object: ', test_object)


rules.add_perm('main.change_pool', is_referee_for_pool | is_dt_pool)
rules.add_perm('main.change_de_table_entry', is_referee_for_de | is_dt_de_table_entry)
rules.add_perm('main.create_competition', is_manager)
rules.add_perm('main.manage_competition', is_manager)
rules.add_perm('main.manage_organisation', is_manager)
