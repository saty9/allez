from django.db import models
from .entry import Entry


class AddStage(models.Model):
    TOP = 'TOP'
    BOTTOM = 'BOT'
    choices = ((TOP, "Top of Rankings"),
               (BOTTOM, "Bottom of Rankings"))
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    where = models.CharField(max_length=3, choices=choices, default=TOP)
    run = models.BooleanField(default=False)

    def ordered_competitors(self):
        input_entries = self.stage.input()
        additions = [addition.entry
                     for addition in self.addcompetitor_set.order_by('sequence')
                     .exclude(entry__state=Entry.NOT_CHECKED_IN).all()]
        if self.where == self.TOP:
            additions.extend(input_entries)
            out = additions
        elif self.where == self.BOTTOM:
            input_entries.extend(additions)
            out = input_entries
        return out