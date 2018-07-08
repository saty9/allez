from django.db import models


class DeTableEntry(models.Model):
    table = models.ForeignKey('main.DeTable', on_delete=models.CASCADE)
    entry = models.ForeignKey('main.Entry', on_delete=models.CASCADE, null=True)
    score = models.IntegerField(default=0)
    victory = models.BooleanField(default=False)
    table_pos = models.IntegerField()
    referee = models.ForeignKey('main.Referee', null=True, on_delete=models.PROTECT, default=None)

    def against(self):
        """returns the DeTableEntry this one is fighting against"""
        if self.table_pos % 2:
            return DeTableEntry.objects.get(table=self.table, table_pos=self.table_pos - 1)
        else:
            return DeTableEntry.objects.get(table=self.table, table_pos=self.table_pos + 1)

    def __str__(self):
        return str(self.entry)
