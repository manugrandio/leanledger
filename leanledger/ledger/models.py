from decimal import Decimal
from itertools import groupby

from django.db import models
from django.db.models.functions import Abs
from django.contrib.auth.models import User
from django.urls import reverse

from .core import DEBIT, CREDIT, record_is_balanced


class Ledger(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)


class AccountManager(models.Manager):
    def destination_accounts(self, ledger_pk):
        return self.filter(parent=None, type=Account.DESTINATION, ledger=ledger_pk)

    def origin_accounts(self, ledger_pk):
        return self.filter(parent=None, type=Account.ORIGIN, ledger=ledger_pk)

    def all_as_dict(self, ledger_pk):
        return [account.as_dict() for account in self.filter(ledger=ledger_pk)]


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

    # TODO enforce uniqueness of: name + parent
    # TODO enforce: children must be the same type as parent
    # TODO enforce: accounts with children don't have own variations
    #      - When adding children, move existing variations to a default "other" child account

    @property
    def total(self):
        if self.children.exists():
            return sum(child.total for child in self.children.all())
        else:
            return self.variations.total if self.variations.total is not None else Decimal('0')

    def get_breadcrumbs(self):
        return self.parent.get_breadcrumbs() + (self,) if self.parent else (self,)

    @property
    def full_name(self):
        return ' / '.join(account.name for account in self.get_breadcrumbs())

    def get_absolute_url(self):
        return reverse("account_detail", args=[self.ledger.pk, self.pk])

    def as_dict(self):
        return {
            "id": self.pk,
            "name": self.name,
            "full_name": self.full_name,
            "type": self.type,
            "url": self.get_absolute_url(),
        }

    def __str__(self):
        return '{}: {} ({})'.format(self.type, self.name, self.total)


class RecordManager(models.Manager):
    def variations_by_type(self):
        return [record.variations_by_type() for record in self.all()]


class Record(models.Model):
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, related_name='records')
    date = models.DateField()
    description = models.CharField(max_length=128, blank=True)
    # TODO on_delete=CASCASDE when Accounts are deleted

    objects = RecordManager()

    def variations_by_type(self):
        get_type = lambda variation: variation.type
        variations = list(self.variations.all().order_by(Abs("amount").desc(), "pk"))
        variations.sort(key=get_type)
        grouped = groupby(variations, get_type)
        return {type_: list(variations) for type_, variations in grouped}

    def as_dict(self):
        variations = self.variations_by_type()
        return {
            "id": self.pk,
            "is_balanced": self.is_balanced(),
            "date": self.date.strftime("%Y-%m-%d"),
            "description": self.description,
            "variations": {
                "debit": [variation.as_dict() for variation in variations[Variation.DEBIT]],
                "credit": [variation.as_dict() for variation in variations[Variation.CREDIT]],
            },
        }

    is_balanced = record_is_balanced


class VariationManager(models.Manager):
    @property
    def total(self):
        amount_sum = self.all().aggregate(models.Sum('amount'))['amount__sum']
        return amount_sum.quantize(Decimal('0.01')) if amount_sum is not None else None


class Variation(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='variations')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='variations')
    amount = models.DecimalField(max_digits=16, decimal_places=2)  # TODO cannot be 0

    DEBIT = DEBIT
    CREDIT = CREDIT

    objects = VariationManager()

    @property
    def type(self):
        is_increase = self.amount > 0
        if self.account.type == Account.ORIGIN:
            return self.CREDIT if is_increase else self.DEBIT
        else:
            return self.DEBIT if is_increase else self.CREDIT

    def as_dict(self):
        return {
            "id": self.pk,
            "account_id": self.account.pk,
            "account_name": self.account.name,
            "account_url": self.account.get_absolute_url(),
            "amount": abs(float(self.amount)),
        }

    def __str__(self):
        return 'Variation({}, {}, {})'.format(
            self.account.name, abs(self.amount), self.type)
