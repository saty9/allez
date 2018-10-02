from random import sample

from django.db import models


class CullStage(models.Model):
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    number = models.IntegerField(null=True, default=None)  # worst position that should survive
    # TODO investigate if some competitions cull on other parameters than just position e.g. ind v/m or a certain %

    def ordered_competitors(self):
        return [entry for group in self.ranked_competitors() for entry in sample(group, len(group))]

    def ranked_competitors(self):
        fencers = self.stage.input(ranked=True)
        count = 0
        index = 0
        out = []
        while count < self.number:
            out.append(fencers[index])
            count += len(fencers[index])
            index += 1
        return fencers[:self.number]
