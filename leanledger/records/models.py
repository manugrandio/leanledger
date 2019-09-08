from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    ORIGIN = 'O'
    DESTINATION = 'D'
    ACCOUNT_TYPES = (
        (ORIGIN, 'Origin'),
        (DESTINATION, 'Destination'),
    )
    type = models.CharField(max_length=1, choices=ACCOUNT_TYPES)
    name = models.CharField(max_length=64)
    parent = models.ForeignKey(
        'self', null=True, on_delete=models.CASCADE, related_name='children')
