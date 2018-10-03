import math
from random import sample

from django.db import models
from main.models.de_table import UnfinishedTableException


class DeStage(models.Model):
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    target = models.IntegerField(default=1)
    fight_down_to = models.IntegerField(default=1)

    def ordered_competitors(self):
        return [entry for group in self.ranked_competitors() for entry in sample(group, len(group))]

    def ranked_competitors(self):
        try:
            return self.detable_set.get(parent__isnull=True).ranked_competitors()
        except UnfinishedTableException as e:
            from main.models.stage import Stage
            raise Stage.NotCompleteError(e)

    def start(self):
        """sets up a DE by creating the first table and seeding it with entries and null entries for byes"""
        if self.detable_set.exists():
            raise AssertionError("cant start already running DE")
        ranked_entries = self.stage.input(ranked=True)
        entries = [entry for group in ranked_entries for entry in sample(group, len(group))]
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
        for index, equal_entries in enumerate(ranked_entries):
            for entry in equal_entries:
                self.deseed_set.create(entry=entry, seed=index + 1)


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

