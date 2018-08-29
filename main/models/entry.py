from django.db import models


class Entry(models.Model):
    class Meta:
        unique_together = (('competition', 'competitor'),)
        get_latest_by = 'competition__date'
    EXCLUDED = "EX"
    DID_NOT_FINISH = "WI"  # Withdrawn
    NOT_CHECKED_IN = "NC"
    CHECKED_IN = "CI"
    DID_NOT_START = "NS"
    states = ((EXCLUDED, "Excluded"),
              (DID_NOT_FINISH, "Did Not Finish"),
              (NOT_CHECKED_IN, "Not Checked In"),
              (CHECKED_IN, "Checked In"),
              (DID_NOT_START, "Did Not Start"))

    competition = models.ForeignKey('main.Competition', on_delete=models.CASCADE)
    competitor = models.ForeignKey('main.Competitor', on_delete=models.PROTECT)
    finishing_place = models.IntegerField(null=True, default=None)
    exited_at_stage = models.ForeignKey('main.stage', on_delete=models.CASCADE, null=True, default=None)
    state = models.CharField(max_length=2, choices=states, default=NOT_CHECKED_IN)
    club = models.ForeignKey('main.Club', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return "({}) - {}".format(self.club.name, self.competitor.name)
