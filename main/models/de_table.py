from django.db import models


class DeTable(models.Model):
    de = models.ForeignKey('main.DeStage', on_delete=models.CASCADE)
    parent = models.ForeignKey('main.DeTable', on_delete=models.CASCADE, related_name='children', null=True)
    winners = models.BooleanField(default=True)

    def ordered_competitors(self):
        if self.automated():
            return list(self.detableentry_set.filter(entry__isnull=False).order_by('entry__deseed__seed').all())
        elif self.detableentry_set.count() == 2:
            return list(self.detableentry_set.filter(entry__isnull=False).order_by('-victory').all())
        else:
            winners = self.children.get(winners=True).ordered_competitors()
            losers = self.children.get(winners=False).ordered_competitors()
            winners.extend(losers)
            return winners

    def automated(self) -> bool:
        """Returns if this table can be automated.
        A table can be automated if no winners from it can be ranked >= the de's fight down to"""
        return not self.winners and self.max_rank() > self.de.fight_down_to

    def max_rank(self) -> int:
        """returns the maximum rank attainable by competitors in this table"""
        if self.parent is None:
            return 1
        elif self.winners:
            return self.parent.max_rank()
        else:
            return self.parent.max_rank() + self.detableentry_set.count()
