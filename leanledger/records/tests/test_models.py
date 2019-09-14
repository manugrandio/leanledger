from datetime import date

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
        bank_one = Account.objects.create(
            name='bank one', type=Account.DESTINATION, parent=cash, ledger=cls.ledger)
        bank_two = Account.objects.create(
            name='bank two', type=Account.ORIGIN, parent=cash, ledger=cls.ledger)

    @classmethod
    def tearDownClass(cls):
        Account.objects.all().delete()
        cls.user.delete()
        cls.ledger.delete()

    def test_query_accounts(self):
        cash = Account.objects.get(name='cash')

        children_names = {account.name for account in cash.children.all()}
        self.assertEqual(children_names, {'bank one', 'bank two'})


class TestRecord(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user('Test')
        cls.ledger = Ledger.objects.create(user=cls.user, name='My Ledger')
        cls.record = Record.objects.create(date=date(2019, 9, 14), ledger=cls.ledger)
        cls.account_cash = Account.objects.create(
            name='cash', type=Account.DESTINATION, ledger=cls.ledger)
        cls.account_expense = Account.objects.create(
            name='expense', type=Account.ORIGIN, ledger=cls.ledger)
        cls.variation_cash = Variation.objects.create(
            amount=-100, record=cls.record, account=cls.account_cash)
        cls.variation_expense = Variation.objects.create(
            amount=-100, record=cls.record, account=cls.account_expense)

    def test_account_names(self):
        names = {variation.account.name for variation in self.record.variations.all()}
        self.assertEqual(names, {'cash', 'expense'})

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.ledger.delete()
        Account.objects.all().delete()
        Record.objects.all().delete()
