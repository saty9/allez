from django.db import models
from django.utils.translation import gettext as _
from django.contrib.humanize.templatetags.humanize import ordinal


class DeTable(models.Model):
    de = models.ForeignKey('main.DeStage', on_delete=models.CASCADE)
    parent = models.ForeignKey('main.DeTable', on_delete=models.CASCADE, related_name='children', null=True)
    winners = models.BooleanField(default=True)
    complete = models.BooleanField(default=False)

    def title(self) -> str:
        """Get a title string for a DeTable"""
        max_rank = self.max_rank()
        table_size = self.detableentry_set.count()
        if max_rank == 1:
            special_titles = {2: _("Final"),
                              4: _("SemiFinal"),
                              8: _("QuarterFinal")}
            table_size = self.detableentry_set.count()
            # Translators: title for a de table e.g. Table of 64
            return special_titles.get(table_size, _("Table of %(size)i") % {'size': table_size})
        elif table_size == 2:
            # Translators: title for a de table of 2 e.g. Fight for 9th
            return _("Fight for %(max_rank)s") % {'max_rank': ordinal(max_rank)}
        else:
            # Translators: title for a de table e.g. Fights for 9th between 8
            return _("Fights for %(max_rank)s between %(table_size)i") % {'max_rank': ordinal(max_rank),
                                                                          'table_size': table_size}

    def ordered_competitors(self):
        if self.automated():
            # TODO confirm that this is safe if there are multiple DE's (and therefore seeds) in a single competition
            return list(self.detableentry_set.filter(entry__isnull=False).order_by('entry__deseed__seed').all())
        elif self.detableentry_set.count() == 2:
            x = self.detableentry_set.first()
            if x.victory or x.against().victory:
                return list(self.detableentry_set.filter(entry__isnull=False).order_by('-victory').all())
            else:
                raise UnfinishedTableException('not all fights complete')
        else:
            if not self.children.exists():
                raise UnfinishedTableException('cannot order competitors without child tables')
            winners = self.children.get(winners=True).ordered_competitors()
            losers = self.children.get(winners=False).ordered_competitors()
            winners.extend(losers)
            return winners

    def automated(self) -> bool:
        """Returns if this table can be automated.
        A table can be automated if no winners from it can be ranked >= the de's fight down to"""
        return not self.detableentry_set.filter(entry__isnull=False).exists() or \
               (not self.winners and self.max_rank() > self.de.fight_down_to)

    def max_rank(self) -> int:
        """returns the maximum rank attainable by competitors in this table"""
        if self.parent is None:
            return 1
        elif self.winners:
            return self.parent.max_rank()
        else:
            return self.parent.max_rank() + self.detableentry_set.count()

    def make_children(self):
        """adds winners and losers tables as children of this table"""
        if self.children.count() != 0:
            raise AssertionError("cant make children if children already exist")
        if self.detableentry_set.count() <= 2:
            raise RuntimeError("trying to make a child table of a table with <= 2 entries")
        for e in self.detableentry_set.all():
            if not (e.victory or e.against().victory):
                raise UnfinishedTableException('cannot make child tables until all fights in this table are completed')
            if e.victory == e.against().victory:
                if e.entry is None and e.against().entry is None:
                    e.victory = not e.victory
                    e.save()
                else:
                    raise Exception('Panic Database inconsistency')
        winners = self.children.create(de=self.de, winners=True)
        losers = self.children.create(de=self.de, winners=False)
        for e in self.detableentry_set.all():
            if e.victory:
                winners.detableentry_set.create(entry=e.entry, table_pos=e.table_pos // 2)
            else:
                losers.detableentry_set.create(entry=e.entry, table_pos=e.table_pos // 2)

        # byes automatically lose their fights
        for bye in losers.detableentry_set.filter(entry__isnull=True).all():
            if not bye.victory:
                # protecting against case where 2 byes end up against each other when fighting for all positions
                against = bye.against()
                against.victory = True
                against.save()

        self.complete = True
        self.save()
        if losers.automated():
            losers.complete = True
            losers.save()


class UnfinishedTableException(Exception):
    pass
