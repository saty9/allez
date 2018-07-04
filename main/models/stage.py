from django.contrib.postgres.fields import JSONField
from django.db import models
from .pool_stage import PoolStage


class Stage(models.Model):
    POOL = 'POO'
    DE = 'DEL'
    CULL = 'CUL'
    stage_types = ((POOL, "Pool"),
                   (DE, "Direct Elimination"),
                   (CULL, "Cull"))
    NOT_STARTED = 'STD'
    READY = 'RDY'
    STARTED = 'GO'
    FINISHED = 'FIN'
    LOCKED = 'LCK'
    states = ((NOT_STARTED, "Not Started"),
              (READY, "Ready to Start"),
              (STARTED, "Running"),
              (FINISHED, "Finished"),
              (LOCKED, "Finished and Confirmed"))
    type = models.CharField(max_length=3, choices=stage_types)
    state = models.CharField(max_length=3, choices=states, default=NOT_STARTED)
    data = JSONField()
    competition = models.ForeignKey('main.Competition', on_delete=models.CASCADE)
    number = models.IntegerField()

    def ordered_competitors(self):
        if self.type == self.POOL:
            return PoolStage.objects.get(stage=self).ordered_competitors()
        elif self.type == self.CULL:
            lst2 = None  # fencers who survived the cull
            lst1 = None  # previous stages ordered fencer
            temp = set(lst2)
            lst3 = [value for value in lst1 if value in temp]
            return lst3

    class Meta:
        unique_together = ('number', 'competition')
