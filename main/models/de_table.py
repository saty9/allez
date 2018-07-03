from django.db import models


class DeTable(models.Model):
    de = models.ForeignKey('main.De', on_delete=models.CASCADE)
    parent = models.ForeignKey('main.DeTable', on_delete=models.CASCADE)
    winners = models.BooleanField()

    def ordered_competitors(self):
        pass

    def automated(self) -> bool:
        """Returns if this table can be automated.
        A table can be automated if no winners from it can be ranked >= the de's fight down to"""
        pass
