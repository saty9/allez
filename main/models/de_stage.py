import math
from django.db import models


class DeStage(models.Model):
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    target = models.IntegerField(default=1)
    fight_down_to = models.IntegerField(default=1)

    def ordered_competitors(self): 
        return list(map(lambda x: x.entry, self.detable_set.get(parent__isnull=True).ordered_competitors()))

    def start(self):
        """sets up a DE by creating the first table and seeding it with entries and null entries for byes"""
        assert not self.detable_set.exists(), "cant start already running DE"
        entries = self.stage.input()
        entries_length = len(entries)
        table = self.detable_set.create(parent=None)
        rounds = math.ceil(math.log2(entries_length))

        # creating DeTableEntries
        for table_pos, entry_index in enumerate(table_layout(rounds)):
            if entry_index > entries_length:
                # adding a bye
                table.detableentry_set.create(entry=None, table_pos=table_pos)
            else:
                table.detableentry_set.create(entry=entries[entry_index - 1], table_pos=table_pos)

        # byes automatically lose their fights
        for bye in table.detableentry_set.filter(entry__isnull=True).all():
            against = bye.against()
            against.victory = True
            against.save()

        # creating seeds
        for index, entry in enumerate(entries):
            self.deseed_set.create(entry=entry, seed=index)


def table_layout(rounds):
    """returns a list of ints representing the placement of fencers in the first table of a de

     Args:
        rounds (int): number of rounds in the DE
    """
    # based on code from: https://stackoverflow.com/questions/5770990/sorting-tournament-seeds/45572051#45572051
    matches = [1, 2]
    for r in range(1, rounds):
        round_matches = []
        s = (2 ** (r + 1)) + 1  # lowest rank in round + 1

        for i in range(len(matches) // 2):
            round_matches.append(matches[i * 2])
            round_matches.append(s - matches[i * 2])
            round_matches.append(s - matches[i * 2 + 1])
            round_matches.append(matches[i * 2 + 1])

        matches = round_matches

    return matches

