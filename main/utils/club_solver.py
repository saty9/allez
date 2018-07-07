from typing import List, Optional, Tuple, Dict
from main.models import Entry, Club


# TODO rewrite so every switch is a tree branch and use to find optimum (switching order considered important) O(n!)

def attempt_solve(pools_in: List[List[Entry]]) -> List[List[Entry]]:
    """attempts to rearrange fencers in pools by moving them up or down a single pool while retaining skill distribution
    of the pools
    This is based on code written for an A-level practical and will not always find the optimal solution"""
    pools: List[Tuple[Entry, Club, bool]] = []
    for pool in pools_in:
        pools.append(list(map(lambda z: (z, z.competitor.club, False), pool)))
    number_of_pools = len(pools)
    conflicts = conflicts_dict_list(pools)

    while True:
        swapped_large = False
        # look for swaps in each pool
        for x in range(number_of_pools):
            swapped_small = True
            while conflicts[x] and swapped_small:
                swapped_small = False
                if x > 0:
                    for conflicting_club in conflicts[x].keys():
                        if not contains_club(pools[x - 1], conflicting_club):
                            # runs when one of the conflicting clubs from pool x is not in pool x -1
                            for conflict_index in conflicts[x][conflicting_club]:
                                if len(pools[x - 1]) >= conflict_index:
                                    # there is a position I can switch the conflict into in the pool bellow
                                    current = pools[x - 1][conflict_index]
                                    if not contains_club(pools[x], current[1]) and not \
                                            current[2] and not\
                                            pools[x][conflict_index][2]:
                                        # do the switch
                                        pools[x - 1][conflict_index] = pools[x][conflict_index]
                                        pools[x][conflict_index] = current
                                        conflicts = conflicts_dict_list(pools)
                                        swapped_small = True
                                        swapped_large = True
                                        break
                if x < number_of_pools - 1:
                    # runs if not last pool
                    for conflicting_club in conflicts[x].keys():
                        if not contains_club(pools[x + 1], conflicting_club):
                            # now checking for possible swap with the pool x + 1
                            for conflict_index in conflicts[x][conflicting_club]:
                                if len(pools[x + 1]) >= conflict_index:
                                    current = pools[x + 1][conflict_index]
                                    if not contains_club(pools[x], current[1]) and not \
                                            current[2] and not \
                                            pools[x][conflict_index][2]:
                                        # do the switch
                                        pools[x + 1][conflict_index] = pools[x][conflict_index]
                                        pools[x][conflict_index] = current
                                        swapped_small = True
                                        swapped_large = True
                                        conflicts = conflicts_dict_list(pools)
                                        break
        if not swapped_large:
            break

    for index, pool in enumerate(pools):
        pools_in[index] = list(map(lambda y: y[0], pool))


def contains_club(pool: List[Tuple[Entry, Club, bool]], club: Club) -> bool:
    """returns if a pool contains a fencer from the given club"""
    for (_, entry_club, _) in pool:
        if entry_club == club:
            return True
    return False


def conflicts_dict_list(pools: List[List[Tuple[Entry, Club, bool]]]) -> List[Dict[Club, int]]:
    out = []
    for pool in pools:
        clubs = {}
        for index, (_, club, _) in enumerate(pool):
            if club in clubs:
                clubs[club].append(index)
            else:
                clubs[club] = [index]
        out.append({k: v for k, v in clubs.items() if len(v) > 1})
    return out
