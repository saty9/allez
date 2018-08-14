from django.db import models


class CullStage(models.Model):
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    number = models.IntegerField(null=True, default=None)  # worst position that should survive
    # TODO investigate if some competitions cull on other parameters than just position e.g. ind v/m or a certain %

    def ordered_competitors(self):
        fencers = self.stage.input()
        return fencers[:self.number]
