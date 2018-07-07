from django.db import models


class AddStage(models.Model):
    TOP = 'TOP'
    BOTTOM = 'BOT'
    choices = ((TOP, "Top of Rankings"),
               (BOTTOM, "Bottom of Rankings"))
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    where = models.CharField(max_length=3, choices=choices, default=BOTTOM)
    run = models.BooleanField(default=False)

    def ordered_competitors(self):
        if not self.run:
            self.create_new_entries()
        input_entries = self.stage.input()
        comp = self.stage.competition
        additions = [addition.competitor.entry_set.get(competition=comp)
                     for addition in self.addcompetitor_set.order_by('sequence').all()]
        if self.where == self.TOP:
            additions.extend(input_entries)
            out = additions
        elif self.where == self.BOTTOM:
            input_entries.extend(additions)
            out = input_entries
        return out

    def create_new_entries(self):
        assert not self.run, "Cant create an add stages entries twice"
        for competitor in self.addcompetitor_set.all():
            self.stage.competition.entry_set.create(competitor=competitor.competitor)
        self.run = True
        self.save()