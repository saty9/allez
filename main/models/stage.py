from django.contrib.postgres.fields import JSONField
from django.db import models
from .pool_stage import PoolStage
from .add_stage import AddStage
from .cull_stage import CullStage


class Stage(models.Model):
    POOL = 'POO'
    DE = 'DEL'
    CULL = 'CUL'
    ADD = 'ADD'
    stage_types = ((POOL, "Pool"),
                   (DE, "Direct Elimination"),
                   (CULL, "Cull"),
                   (ADD, "Add Fencers"))
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
            return CullStage.objects.get(stage=self).ordered_competitors()
        elif self.type == self.ADD:
            return AddStage.objects.get(stage=self).ordered_competitors()

    def input(self):
        """returns a list of entries representing the input of this stage"""
        if not Stage.objects.filter(number__lt=self.number).exists():
            return []
        else:
            return Stage.objects.get(competition_id=self.competition_id, number=self.number-1).ordered_competitors()

    class Meta:
        unique_together = ('number', 'competition')
