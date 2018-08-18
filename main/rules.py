import rules
from main import models


def get_organisation(object):
    if object.__class__ == models.Organisation:
        return object
    elif object.__class__ == models.Competition:
        return object.organisation
    elif object.__class__ == models.Stage:
        return object.competition.organisation
    else:
        try:
            return object.stage.competition.organisation
        except:
            raise ValueError('Unexpected object: ', object)


@rules.predicate
def is_dt(user, test_object):
    org = get_organisation(test_object)
    dt_states = [models.OrganisationMembership.MANAGER, models.OrganisationMembership.DT]
    return models.OrganisationMembership.objects.\
        filter(organisation=org, user=user, state__in=dt_states).exists()


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
def is_manager(user, test_object):
    org = get_organisation(test_object)
    return models.OrganisationMembership.objects.\
        filter(organisation=org, user=user, state=models.OrganisationMembership.MANAGER).\
        exists()


rules.add_perm('main.change_pool', is_referee_for_pool | is_dt)
rules.add_perm('main.change_de_table_entry', is_referee_for_de | is_dt)
rules.add_perm('main.create_competition', is_manager)
rules.add_perm('main.manage_competition', is_manager | is_dt)
rules.add_perm('main.manage_organisation', is_manager)
