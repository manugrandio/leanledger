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
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, related_name='accounts')
    parent = models.ForeignKey(
        'self', null=True, on_delete=models.CASCADE, related_name='children')

    objects = AccountManager()


class Record(models.Model):
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, related_name='records')
    date = models.DateField()
    # TODO on_delete=CASCASDE when Accounts are deleted


class Variation(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='variations')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='variations')
    amount = models.DecimalField(max_digits=16, decimal_places=2)
