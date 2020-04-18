from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Account, Ledger, Record, Variation


def set_up_class(test_case):
    test_case.user = User.objects.create_user('Test')
    test_case.ledger = Ledger.objects.create(user=test_case.user, name='My Ledger')
    test_case.record = Record.objects.create(date=date(2019, 9, 14), ledger=test_case.ledger)
    test_case.account_cash = Account.objects.create(
        name='cash', type=Account.DESTINATION, ledger=test_case.ledger)
    test_case.account_bank = Account.objects.create(
        name="bank", type=Account.DESTINATION, ledger=test_case.ledger)
    test_case.account_expense_one = Account.objects.create(
        name='expense one', type=Account.ORIGIN, ledger=test_case.ledger)
    test_case.account_expense_two = Account.objects.create(
        name='expense two', type=Account.ORIGIN, ledger=test_case.ledger)
    test_case.account_expense_three = Account.objects.create(
        name='expense three', type=Account.ORIGIN, ledger=test_case.ledger)
    test_case.variation_cash = Variation.objects.create(
        amount=-100, record=test_case.record, account=test_case.account_cash)
    test_case.variation_expense_one = Variation.objects.create(
        amount=-40, record=test_case.record, account=test_case.account_expense_one)
    test_case.variation_expense_two = Variation.objects.create(
        amount=-60, record=test_case.record, account=test_case.account_expense_two)


def tear_down_class(test_case):
    User.objects.all().delete()
    Ledger.objects.all().delete()
    Account.objects.all().delete()
    Record.objects.all().delete()


class TestLedger(TestCase):
    @classmethod
    def setUpClass(cls):
        set_up_class(cls)
        cls.ledger_two = Ledger.objects.create(user=cls.user, name='My Second Ledger')
        cls.record_two = Record.objects.create(
            date=date(2019, 10, 1), ledger=cls.ledger_two, description='My second record')

    @classmethod
    def tearDownClass(cls):
        cls.ledger.delete()
        cls.user.delete()

    def test_ledger(self):
        ledger = Ledger.objects.all().get(name='My Ledger')

        self.assertEqual(ledger.name, 'My Ledger')

    def test_ledger_get_records(self):
        ledger = Ledger.objects.get(name='My Second Ledger')

        records = ledger.records.all()

        self.assertEqual([record.description for record in records], ['My second record'])


class TestAccount(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user('Test')
        cls.ledger = Ledger.objects.create(user=cls.user, name='My Ledger')
        cls.cash = Account.objects.create(name='cash', type=Account.DESTINATION, ledger=cls.ledger)
        wealth = Account.objects.create(name='wealth', type=Account.ORIGIN, ledger=cls.ledger)
        bank_one = Account.objects.create(
            name='bank one', type=Account.DESTINATION, parent=cls.cash, ledger=cls.ledger)
        cls.bank_two = Account.objects.create(
            name='bank two', type=Account.ORIGIN, parent=cls.cash, ledger=cls.ledger)
        cls.bank_two_sub = Account.objects.create(
            name='sub bank two', type=Account.ORIGIN, parent=cls.bank_two, ledger=cls.ledger)
        record = Record.objects.create(date=date(2019, 9, 14), ledger=cls.ledger)
        Variation.objects.create(amount=80, record=record, account=bank_one)
        Variation.objects.create(amount=80, record=record, account=cls.bank_two_sub)
        Variation.objects.create(amount=160, record=record, account=wealth)

    tearDownClass = classmethod(tear_down_class)

    def test_query_accounts(self):
        cash = Account.objects.get(name='cash')

        children_names = {account.name for account in cash.children.all()}
        self.assertEqual(children_names, {'bank one', 'bank two'})

    def test_account_total(self):
        cash = Account.objects.get(name='cash')

        self.assertEqual(cash.total, Decimal('160'))

    def test_breadcrumbs(self):
        breadcrumbs = (self.cash, self.bank_two, self.bank_two_sub)
        self.assertEqual(self.bank_two_sub.get_breadcrumbs(), breadcrumbs)

    def test_full_name(self):
        self.assertEqual(self.bank_two_sub.full_name, 'cash / bank two / sub bank two')

    def test_as_dict(self):
        account_dict = self.cash.as_dict()

        self.assertEqual(account_dict, {
            "id": self.cash.pk,
            "name": "cash",
            "full_name": "cash",
            "type": "D",
            "url": self.cash.get_absolute_url(),
        })


class TestRecord(TestCase):
    setUp = set_up_class

    def test_variations_by_type(self):
        variations_by_type_iter = self.record.variations_by_type()
        variations_by_type = {
            type_: variations for type_, variations in variations_by_type_iter.items()
        }

        self.assertEqual(variations_by_type, {
            Variation.DEBIT: [
                self.variation_expense_two,
                self.variation_expense_one,
            ],
            Variation.CREDIT: [
                self.variation_cash,
            ],
        })

    def test_as_dict(self):
        record_dict = self.record.as_dict()

        expected = {
            "id": self.record.pk,
            "is_balanced": True,
            "date": "2019-09-14",
            "description": "",
            "variations": {
                "debit": [
                    {
                        "id": self.variation_expense_two.pk,
                        "account_id": self.account_expense_two.pk,
                        "account_name": "expense two",
                        "account_url": self.account_expense_two.get_absolute_url(),
                        "amount": 60,
                    },
                    {
                        "id": self.variation_expense_one.pk,
                        "account_id": self.account_expense_one.pk,
                        "account_name": "expense one",
                        "account_url": self.account_expense_one.get_absolute_url(),
                        "amount": 40,
                    },
                ],
                "credit": [
                    {
                        "id": self.variation_cash.pk,
                        "account_id": self.account_cash.pk,
                        "account_name": "cash",
                        "account_url": self.account_cash.get_absolute_url(),
                        "amount": 100
                    },
                ],
            },
        }
        self.assertEqual(record_dict, expected)

    def test_update_from_dict_record(self):
        new_record_state = {
            "date": "2020-01-01",
            "id": self.record.pk,
            "is_balanced": True,
            "description": "New description",
            "variations": {"credit": [{"account_name": "cash",
                                       "account_url": self.account_cash.get_absolute_url(),
                                       "account_id": self.account_cash.pk,
                                       "amount": 100.0,
                                       "id": self.variation_cash.pk}],
                           "debit": [{"account_name": "expense two",
                                      "account_url": self.account_expense_two.get_absolute_url(),
                                      "account_id": self.account_expense_two.pk,
                                      "amount": 60.0,
                                      "id": self.variation_expense_two.pk},
                                     {"account_name": "expense one",
                                      "account_url": self.account_expense_one.get_absolute_url(),
                                      "account_id": self.account_expense_one.pk,
                                      "amount": 40.0,
                                      "id": self.variation_expense_one.pk}]}
        }

        with patch.object(Variation, "objects") as variation_objects:
            self.record.update_from_dict(new_record_state)

        variation_objects.create_variations_from_dict.assert_called_once()
        variation_objects.update_variations_from_dict.assert_called_once()
        variation_objects.delete_variations_from_dict.assert_called_once()
        self.assertEqual(self.record.date, date(2020, 1, 1))
        self.assertEqual(self.record.description, "New description")


class TestVariation(TestCase):
    def setUp(self):
        set_up_class(self)
        self.record_2 = Record.objects.create(date=date(2019, 10, 14), ledger=self.ledger)
        self.variation_cash_2 = Variation.objects.create(
            amount=-200, record=self.record_2, account=self.account_cash
        )
        self.variation_expense_one_2 = Variation.objects.create(
            amount=-200, record=self.record_2, account=self.account_expense_one
        )

    tearDownClass = classmethod(tear_down_class)

    def test_create_variations_from_dict(self):
        variations_state = {"credit": [{"account_name": "cash",
                                       "account_url": self.account_cash.get_absolute_url(),
                                       "account_id": self.account_cash.pk,
                                       "amount": 100.0,
                                       "id": self.variation_cash.pk},
                                      # New variation:
                                      {"account_name": "bank",
                                       "account_url": self.account_bank.get_absolute_url(),
                                       "account_id": self.account_bank.pk,
                                       "amount": 50.0,
                                       # Non-existing id in "credit" group
                                       "id": self.variation_cash.pk + 1}],
                           "debit": [{"account_name": "expense two",
                                      "account_url": self.account_expense_two.get_absolute_url(),
                                      "account_id": self.account_expense_two.pk,
                                      "amount": 60.0,
                                      "id": self.variation_expense_two.pk},
                                     {"account_name": "expense one",
                                      "account_url": self.account_expense_one.get_absolute_url(),
                                      "account_id": self.account_expense_one.pk,
                                      "amount": 40.0,
                                      "id": self.variation_expense_one.pk}]}
        existing_variations = self.record.variations_by_type()
        n_variations = self.record.variations.count()

        Variation.objects.create_variations_from_dict(
            self.record, existing_variations, variations_state
        )

        # If it doesn't exist, an exception will be raised:
        new_variation = self.record.variations.get(account__name="bank")
        # Amount sign is changed according to account type and variation type (debit/credit)
        self.assertEqual(new_variation.amount, -50)
        self.assertEqual(self.record.variations.count(), n_variations + 1)

    def test_update_variations_from_dict(self):
        variations_state = {"credit": [{"account_name": "cash",
                                       "account_url": self.account_cash.get_absolute_url(),
                                       "account_id": self.account_cash.pk,
                                       "amount": 100.0,
                                       "id": self.variation_cash.pk}],
                           "debit": [{"account_name": "expense three",
                                      # Same variation, but new account and amount
                                      "account_url": self.account_expense_three.get_absolute_url(),
                                      "account_id": self.account_expense_three.pk,
                                      "amount": 70.0,
                                      "id": self.variation_expense_two.pk},
                                     {"account_name": "expense one",
                                      "account_url": self.account_expense_one.get_absolute_url(),
                                      "account_id": self.account_expense_one.pk,
                                      "amount": 30.0,
                                      "id": self.variation_expense_one.pk}]}
        existing_variations = self.record.variations_by_type()

        Variation.objects.update_variations_from_dict(existing_variations, variations_state)

        self.variation_expense_two.refresh_from_db()
        self.assertEqual(self.variation_expense_two.amount, -70)
        self.assertEqual(self.variation_expense_two.account.pk, self.account_expense_three.pk)

    def test_delete_variations_from_dict(self):
        variations_state = {"credit": [{"account_name": "cash",
                                       "account_url": self.account_cash.get_absolute_url(),
                                       "account_id": self.account_cash.pk,
                                       "amount": 100.0,
                                       "id": self.variation_cash.pk}],
                           # Expense one is deleted
                           "debit": [{"account_name": "expense two",
                                      "account_url": self.account_expense_two.get_absolute_url(),
                                      "account_id": self.account_expense_two.pk,
                                      "amount": 60,
                                      "id": self.variation_expense_two.pk}]}
        existing_variations = self.record.variations_by_type()

        Variation.objects.delete_variations_from_dict(existing_variations, variations_state)

        self.assertFalse(Variation.objects.filter(pk=self.variation_expense_one.pk).exists())

    def test_total(self):
        self.assertEqual(self.account_cash.variations.total, Decimal('-300'))

    def test_from_dict(self):
        """
        A credit of an account of type "destination" means it's a balance decrease
        """
        variation_dict = {
            "account_name": "cash",
            "account_url": self.account_cash.get_absolute_url(),
            "account_id": self.account_cash.pk,
            "amount": 70,
            "id": 1,
        }

        variation = Variation.from_dict(variation_dict, Variation.CREDIT, self.record)

        self.assertEqual(variation.amount, -70)

    def test_type(self):
        # TODO
        pass

    def test_is_increase(self):
        types = [
            (Mock(type=Account.DESTINATION), Variation.DEBIT, True),
            (Mock(type=Account.DESTINATION), Variation.CREDIT, False),
            (Mock(type=Account.ORIGIN), Variation.DEBIT, False),
            (Mock(type=Account.ORIGIN), Variation.CREDIT, True),
        ]
        for account, variation_type, expected in types:
            is_increase = Variation.is_increase(account, variation_type)
            with self.subTest(account_type=account.type, variation_type=variation_type):
                self.assertTrue(is_increase is expected)

    def test_update_from_dict_amount(self):
        new_variation_state = {
            "account_name": "cash",
            "account_url": self.account_cash.get_absolute_url(),
            "account_id": self.account_cash.pk,
            "amount": 50.0,
            "id": self.variation_cash.pk
        }

        self.variation_cash.update_from_dict(new_variation_state, Variation.CREDIT)

        self.assertEqual(self.variation_cash.amount, -50)
        self.assertEqual(self.variation_cash.account.pk, self.account_cash.pk)

    def test_update_from_dict_account(self):
        new_variation_state = {
            "account_name": "expense two",
            "account_url": self.account_expense_two.get_absolute_url(),
            "account_id": self.account_expense_two.pk,
            "amount": 200,
            "id": self.variation_expense_one.pk
        }

        self.variation_expense_one.update_from_dict(new_variation_state, Variation.DEBIT)

        self.assertEqual(self.variation_expense_one.account.pk, self.account_expense_two.pk)
        self.assertEqual(self.variation_expense_one.amount, -200)
