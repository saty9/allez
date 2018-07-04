from django.db import models
from .de_seed import DeSeed

class DeStage(models.Model):
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    target = models.IntegerField(default=1)
    fight_down_to = models.IntegerField(default=1)

    def ordered_competitors(self): 
        return list(map(lambda x: x.entry, self.detable_set.get(parent__isnull=True).ordered_competitors()))

    def create_seeds(self):
        previous_stage = self.stage.competition.stage_set.get(number=self.stage.number - 1)
        for index, entry in enumerate(previous_stage.ordered_competitors()):
            DeSeed.objects.create(entry=entry, seed=index, de=self)
