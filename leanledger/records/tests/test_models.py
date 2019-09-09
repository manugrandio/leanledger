from django.test import TestCase
from django.contrib.auth.models import User

from leanledger.records.models import Account, Ledger


class TestLedger(TestCase):
    @classmethod
    def setUpClass(cls):
        user = User.objects.create_user('Test')
        cls.ledger = Ledger.objects.create(user=user, name='My Ledger')

    @classmethod
    def tearDownClass(cls):
        cls.ledger.delete()

    def test_ledger(self):
        ledger = Ledger.objects.all().get()

        self.assertEqual(ledger.name, 'My Ledger')


class TestAccount(TestCase):
    @classmethod
    def setUpClass(cls):
        cash = Account.objects.create(name='cash', type=Account.DESTINATION)
        bank_one = Account.objects.create(name='bank one', type=Account.DESTINATION, parent=cash)
        bank_two = Account.objects.create(name='bank two', type=Account.ORIGIN, parent=cash)

    @classmethod
    def tearDownClass(cls):
        Account.objects.all().delete()

    def test_query_accounts(self):
        cash = Account.objects.get(name='cash')

        children_names = {account.name for account in cash.children.all()}
        self.assertEqual(children_names, {'bank one', 'bank two'})
