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

    def update_from_dict(self, new_record_state):
        # TODO move to serializer

        # Update record
        new_date, new_description = new_record_state["date"], new_record_state["description"]
        update_fields = []
        if new_date != self.date:
            self.date = new_date
            update_fields.append("date")

        if new_description != self.description:
            self.description = new_description
            update_fields.append("description")

        self.save(update_fields=update_fields)
        self.refresh_from_db()

        variations_from_state = new_record_state["variations"]
        existing_variations = self.variations_by_type()

        Variation.objects.create_variations_from_dict(
            self, existing_variations, variations_from_state
        )
        Variation.objects.update_variations_from_dict(existing_variations, variations_from_state)
        Variation.objects.delete_variations_from_dict(existing_variations, variations_from_state)

        return self

    is_balanced = record_is_balanced


class VariationManager(models.Manager):
    @property
    def total(self):
        amount_sum = self.all().aggregate(models.Sum('amount'))['amount__sum']
        return amount_sum.quantize(Decimal('0.01')) if amount_sum is not None else None

    def create_variations_from_dict(self, record, existing_variations, variations_state):
        """
        ids in ``variations_state` are generated in the front-end by increasing in one the max
        existing id within a variation type in a record. So there is no risk of generating an
        existing id.
        """
        variations_to_create = {}
        for variation_type, variations in variations_state.items():
            existing_variations_pks = [v.pk for v in existing_variations[variation_type]]
            variations_to_create[variation_type] = [
                Variation(
                    amount=v["amount"],
                    account=Account.objects.get(pk=v["account_id"]),
                    record=record,
                ) for v in variations if v["id"] not in existing_variations_pks
            ]

        Variation.objects.bulk_create(variations_to_create[Variation.DEBIT])
        Variation.objects.bulk_create(variations_to_create[Variation.CREDIT])

    def update_variations_from_dict(self, existing_variations, variations_state):
        for variation_type, variations in existing_variations.items():
            for variation in variations:
                variation_state = [
                    v for v in variations_state[variation_type] if v["id"] == variation.pk
                ]
                if variation_state:
                    variation.update_from_dict(variation_state[0], variation_type)

    def delete_variations_from_dict(self, existing_variations, variations_state):
        to_delete = []
        for variation_type, variations in existing_variations.items():
            pks_from_state = [v["id"] for v in variations_state[variation_type]]
            for variation in [v for v in variations if v.pk not in pks_from_state]:
                variation.delete()


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

    @classmethod
    def is_increase(cls, account, type_):
        # TODO does it need to be a classmethod?
        if account.type == Account.ORIGIN:
            return type_ == cls.CREDIT
        else:
            return type_ == cls.DEBIT

    def as_dict(self):
        return {
            "id": self.pk,
            "account_id": self.account.pk,
            "account_name": self.account.name,
            "account_url": self.account.get_absolute_url(),
            "amount": abs(float(self.amount)),
        }

    def update_from_dict(self, variation_dict, type_):
        update_fields = []

        account_id = variation_dict["account_id"]
        if account_id != self.account.pk:
            self.account = Account.objects.get(pk=account_id)
            update_fields.append("account")

        # Note that account could have already changed and change `is_increase` output
        amount = variation_dict["amount"] * (1 if self.is_increase(self.account, type_) else -1)
        if amount != self.amount:
            self.amount = amount
            update_fields.append("amount")

        self.save(update_fields=update_fields)

    def __str__(self):
        return 'Variation({}, {}, {})'.format(
            self.account.name, abs(self.amount), self.type)
