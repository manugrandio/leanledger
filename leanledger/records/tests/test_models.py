from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User

from leanledger.records.models import Account, Ledger, Record, Variation


class TestLedger(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user('Test')
        cls.ledger = Ledger.objects.create(user=cls.user, name='My Ledger')

    @classmethod
    def tearDownClass(cls):
        cls.ledger.delete()
        cls.user.delete()

    def test_ledger(self):
        ledger = Ledger.objects.all().get()

        self.assertEqual(ledger.name, 'My Ledger')


class TestAccount(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user('Test')
        cls.ledger = Ledger.objects.create(user=cls.user, name='My Ledger')
        cash = Account.objects.create(name='cash', type=Account.DESTINATION, ledger=cls.ledger)
        wealth = Account.objects.create(name='wealth', type=Account.ORIGIN, ledger=cls.ledger)
        bank_one = Account.objects.create(
            name='bank one', type=Account.DESTINATION, parent=cash, ledger=cls.ledger)
        bank_two = Account.objects.create(
            name='bank two', type=Account.ORIGIN, parent=cash, ledger=cls.ledger)
        record = Record.objects.create(date=date(2019, 9, 14), ledger=cls.ledger)
        Variation.objects.create(amount=80, record=record, account=bank_one)
        Variation.objects.create(amount=80, record=record, account=bank_two)
        Variation.objects.create(amount=160, record=record, account=wealth)

    @classmethod
    def tearDownClass(cls):
        Account.objects.all().delete()
        cls.user.delete()
        cls.ledger.delete()

    def test_query_accounts(self):
        cash = Account.objects.get(name='cash')

        children_names = {account.name for account in cash.children.all()}
        self.assertEqual(children_names, {'bank one', 'bank two'})

    def test_account_total(self):
        cash = Account.objects.get(name='cash')

        self.assertEqual(cash.total, 160)


def set_up_class(test_case):
    test_case.user = User.objects.create_user('Test')
    test_case.ledger = Ledger.objects.create(user=test_case.user, name='My Ledger')
    test_case.record = Record.objects.create(date=date(2019, 9, 14), ledger=test_case.ledger)
    test_case.account_cash = Account.objects.create(
        name='cash', type=Account.DESTINATION, ledger=test_case.ledger)
    test_case.account_expense_one = Account.objects.create(
        name='expense one', type=Account.ORIGIN, ledger=test_case.ledger)
    test_case.account_expense_two = Account.objects.create(
        name='expense two', type=Account.ORIGIN, ledger=test_case.ledger)
    test_case.variation_cash = Variation.objects.create(
        amount=-100, record=test_case.record, account=test_case.account_cash)
    test_case.variation_expense_one = Variation.objects.create(
        amount=-50, record=test_case.record, account=test_case.account_expense_one)
    test_case.variation_expense_two = Variation.objects.create(
        amount=-50, record=test_case.record, account=test_case.account_expense_two)


def tear_down_class(test_case):
    User.objects.all().delete()
    Ledger.objects.all().delete()
    Account.objects.all().delete()
    Record.objects.all().delete()


class TestRecord(TestCase):
    setUpClass = classmethod(set_up_class)
    tearDownClass = classmethod(tear_down_class)

    def test_variations_by_type(self):
        variations_by_type_iter = self.record.variations_by_type()
        variations_by_type = {
            type_: variations for type_, variations in variations_by_type_iter.items()
        }

        self.assertEqual(variations_by_type, {
            Variation.DEBIT: [
                self.variation_expense_one,
                self.variation_expense_two,
            ],
            Variation.CREDIT: [
                self.variation_cash,
            ],
        })


class TestVariation(TestCase):
    @classmethod
    def setUpClass(cls):
        set_up_class(cls)
        cls.record_2 = Record.objects.create(date=date(2019, 10, 14), ledger=cls.ledger)
        Variation.objects.create(amount=-200, record=cls.record_2, account=cls.account_cash)
        Variation.objects.create(amount=-200, record=cls.record_2, account=cls.account_expense_one)

    tearDownClass = classmethod(tear_down_class)

    def test_total(self):
        self.assertEqual(self.account_cash.variations.total, Decimal('-300'))
