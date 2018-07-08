from django.db import models
from django.contrib.auth.models import User


class Referee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    competition = models.ForeignKey('main.Competition', on_delete=models.CASCADE)
