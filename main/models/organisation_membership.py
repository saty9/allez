from django.db import models
from django.contrib.auth.models import User
from . import Organisation


class OrganisationMembership(models.Model):
    MANAGER = 'MG'
    DT = 'DT'
    APPLICANT = "AP"
    states = ((MANAGER, "Manager"),
              (DT, "DT"),
              (APPLICANT, "AP"))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    last_active = models.DateTimeField(auto_now_add=True)
    state = models.CharField(choices=states, max_length=2, default=APPLICANT)
