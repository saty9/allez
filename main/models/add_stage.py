from itertools import groupby
from random import sample

from django.db import models
from django.db.models import Max

from .entry import Entry


class AddStage(models.Model):
    TOP = 'TOP'
    BOTTOM = 'BOT'
    choices = ((TOP, "Top of Rankings"),
               (BOTTOM, "Bottom of Rankings"))
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    where = models.CharField(max_length=3, choices=choices, default=TOP)

    def ordered_competitors(self):
        return [entry for group in self.ranked_competitors() for entry in sample(group, len(group))]

    def ranked_competitors(self):
        """ get ordered list of lists of entries where entries of the same ranking are in a list together
        highest ranks first

        :return:
        :rtype: list[list[Entry]]
        """
        from .stage import Stage
        if self.stage.state in [Stage.READY, Stage.NOT_STARTED]:
            raise Stage.NotCompleteError("Stage not finished yet")
        input_entries = self.stage.input(ranked=True)
        ungrouped_additions = self.addcompetitor_set.order_by('sequence')\
            .exclude(entry__state=Entry.NOT_CHECKED_IN).values('entry', 'sequence').all()
        additions = []
        for _, equal_fencers in groupby(ungrouped_additions, lambda x: x['sequence']):
            additions.append(list(map(lambda fencer: Entry.objects.get(pk=fencer['entry']), equal_fencers)))
        if self.where == self.TOP:
            additions.extend(input_entries)
            out = additions
        elif self.where == self.BOTTOM:
            input_entries.extend(additions)
            out = input_entries
        return out

    def possible_additions(self):
        """get entries that can be added in this stage

        :return: query filtered to correct Entries
        """
        query = self.stage.competition.entry_set.filter(state__in=[Entry.NOT_CHECKED_IN, Entry.CHECKED_IN])
        return query.filter(addcompetitor=None)

    def add_entries(self, entries):
        """Add entries to this stages list of entries to add

        :param list[list[Entry]] entries: entries to add in the order they should be added in entries that are already
            set to be added elsewhere will not be added to this stage
        """
        sequence_num = 1
        if self.addcompetitor_set.exists():
            sequence_num = self.addcompetitor_set.aggregate(Max('sequence'))['sequence__max'] + 1

        for equal_entries in entries:
            for entry in equal_entries:
                if entry.addcompetitor_set.exists():
                    continue
                self.addcompetitor_set.create(entry=entry, sequence=sequence_num)
            sequence_num += 1
