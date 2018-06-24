from django.db import models
from django.contrib.auth.models import User
from . import Organisation


class OrganisationMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
