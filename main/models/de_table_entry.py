from django.db import models


class DeTableEntry(models.Model):
    table = models.ForeignKey('main.DeTable', on_delete=models.CASCADE)
    entry = models.ForeignKey('main.Entry', on_delete=models.CASCADE)
    score = models.IntegerField()
    victory = models.BooleanField()
    table_pos = models.IntegerField()

    def against(self):
        """returns the DeTableEntry this one is fighting against"""
        if self.table_pos % 2:
            return DeTableEntry.objects.get(table=self.table, table_pos=self.table_pos - 1)
        else:
            return DeTableEntry.objects.get(table=self.table, table_pos=self.table_pos + 1)

