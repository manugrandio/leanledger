from itertools import groupby

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

    def variations_by_type(self):
        get_type = lambda variation: variation.type
        variations = list(self.variations.all())
        variations.sort(key=get_type)
        grouped = groupby(variations, get_type)
        return {type_: list(variations) for type_, variations in grouped}


class Variation(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='variations')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='variations')
    amount = models.DecimalField(max_digits=16, decimal_places=2)

    CREDIT = 'credit'
    DEBIT = 'debit'

    @property
    def type(self):
        # TODO could it be expressed in a better way with if-else blocks?
        account_types = {
            (Account.ORIGIN, True): self.CREDIT,
            (Account.ORIGIN, False): self.DEBIT,
            (Account.DESTINATION, True): self.DEBIT,
            (Account.DESTINATION, False): self.CREDIT,
        }
        is_increase = self.amount > 0
        return account_types[(self.account.type, is_increase)]
