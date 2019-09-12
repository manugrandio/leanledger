from django.db import models
from django.contrib.auth.models import User


class Ledger(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)


class AccountManager(models.Manager):
    def destination_accounts(self):
        return self.filter(parent=None, type=Account.DESTINATION)

    def origin_accounts(self):
        return self.filter(parent=None, type=Account.ORIGIN)


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

    objects = AccountManager()


# class Record(models.Model):
    # ledger = models.ForeignKey(Ledger)


# class Variation(models.Model):
    # record = models.ForeignKey(Record)
    # account = models.ForeignKey(Account)
