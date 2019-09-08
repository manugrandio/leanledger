from django.test import TestCase

from leanledger.records.models import Account


class TestAccount(TestCase):
    @classmethod
    def setUpClass(cls):
        cash = Account(name='cash', type=Account.DESTINATION)
        cash.save()

        bank_one = Account(name='bank one', type=Account.DESTINATION, parent=cash)
        bank_one.save()

        bank_two = Account(name='bank two', type=Account.ORIGIN, parent=cash)
        bank_two.save()

    @classmethod
    def tearDownClass(cls):
        Account.objects.all().delete()

    def test_query_accounts(self):
        cash = Account.objects.get(name='cash')

        children_names = {account.name for account in cash.children.all()}
        self.assertEqual(children_names, {'bank one', 'bank two'})
