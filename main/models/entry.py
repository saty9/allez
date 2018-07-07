from django.db import models


class Entry(models.Model):
    class Meta:
        unique_together = (('competition', 'competitor'),)
    EXCLUDED = "EX"
    DID_NOT_FINISH = "WI"  # Withdrawn
    NOT_CHECKED_IN = "NC"
    CHECKED_IN = "CI"
    DID_NOT_START = "NS"
    states = ((EXCLUDED, "Excluded"),
              (DID_NOT_FINISH, "Did Not Finish"),
              (NOT_CHECKED_IN, "Not Checked In"),
              (CHECKED_IN, "Check In"),
              (DID_NOT_START, "Did Not Start"))

    competition = models.ForeignKey('main.Competition', on_delete=models.CASCADE)
    competitor = models.ForeignKey('main.Competitor', on_delete=models.PROTECT)
    finishing_place = models.IntegerField(null=True, default=None)
    exited_at_stage = models.ForeignKey('main.stage', on_delete=models.CASCADE, null=True, default=None)
    state = models.CharField(max_length=2, choices=states, default=NOT_CHECKED_IN)

    def __str__(self):
        return "({}) - {}".format(self.competition_id, self.competitor.name)
