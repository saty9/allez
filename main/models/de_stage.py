from django.db import models


class DeStage(models.Model):
    stage = models.ForeignKey('main.Stage', on_delete=models.CASCADE)
    target = models.IntegerField(default=1)
    fight_down_to = models.IntegerField(default=1)

    def ordered_competitors(self): 
        pass
