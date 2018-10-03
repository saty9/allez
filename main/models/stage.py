from random import sample, seed
from django.db import models
from .pool_stage import PoolStage
from .add_stage import AddStage
from .cull_stage import CullStage
from .de_stage import DeStage


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
    states = ((NOT_STARTED, "Not Ready"),
              (READY, "Ready to Start"),
              (STARTED, "Running"),
              (FINISHED, "Finished"),
              (LOCKED, "Finished and Confirmed"))
    type = models.CharField(max_length=3, choices=stage_types)
    state = models.CharField(max_length=3, choices=states, default=NOT_STARTED)
    competition = models.ForeignKey('main.Competition', on_delete=models.CASCADE)
    number = models.IntegerField()

    def ordered_competitors(self):
        if self.type == self.POOL:
            return PoolStage.objects.get(stage=self).ordered_competitors()
        elif self.type == self.CULL:
            return CullStage.objects.get(stage=self).ordered_competitors()
        elif self.type == self.ADD:
            return AddStage.objects.get(stage=self).ordered_competitors()
        elif self.type == self.DE:
            return DeStage.objects.get(stage=self).ordered_competitors()

    def ranked_competitors(self):
        if self.type == self.POOL:
            return PoolStage.objects.get(stage=self).ranked_competitors()
        elif self.type == self.CULL:
            return CullStage.objects.get(stage=self).ranked_competitors()
        elif self.type == self.ADD:
            return AddStage.objects.get(stage=self).ranked_competitors()
        elif self.type == self.DE:
            return DeStage.objects.get(stage=self).ranked_competitors()

    def input(self, ranked=False):
        """returns a list of entries representing the input of this stage"""
        if not Stage.objects.filter(number__lt=self.number).exists():
            return []
        else:
            ranking = Stage.objects.get(competition_id=self.competition_id,
                                        number=self.number - 1).ranked_competitors()
            if ranked:
                return ranking
            else:
                seed(self.competition.id << 30 + self.id)  # Set random number generator seed for consistent results
                return [entry for group in ranking for entry in sample(group, len(group))]

    def deletable(self):
        """returns whether a stage can be deleted or not"""
        return self.state in [self.NOT_STARTED, self.READY]

    def appendable_to(self):
        """returns whether a stage can be added after this one"""
        return self.state not in [self.LOCKED, self.FINISHED] or \
            not Stage.objects.filter(competition=self.competition, number__gt=self.number)

    def save(self, *args, **kwargs):
        creating = False
        if not self.pk:
            creating = True
        super(Stage, self).save(*args, **kwargs)
        if creating:
            if self.type == Stage.POOL:
                self.poolstage_set.create()
            elif self.type == Stage.DE:
                self.destage_set.create()
            elif self.type == Stage.ADD:
                self.addstage_set.create()
            elif self.type == Stage.CULL:
                self.cullstage_set.create()

    class Meta:
        unique_together = ('number', 'competition')
        get_latest_by = 'number'

    class NotCompleteError(Exception):
        def __init__(self, message):
            super().__init__(message)
