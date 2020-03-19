import json
from collections import namedtuple
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..models import Account, Ledger, Variation, Record


class TestLedgerViews(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger_name = 'Other Ledger'
        cls.user = User.objects.create_user(username='joe', password='pass')

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        Ledger.objects.all().delete()

    def setUp(self):
        self.ledger_two = Ledger.objects.create(name='Ledger Two', user=self.user)

    def tearDown(self):
        self.ledger_two.delete()

    def test_get_new(self):
        response = self.client.get(reverse('ledger_create'))

        self.assertTemplateUsed(response, 'ledger/ledger_create.html')

    def test_post_new(self):
        self.client.login(username='joe', password='pass')
        data = {'name': self.ledger_name}

        response = self.client.post(reverse('ledger_create'), data=data, follow=True)

        self.assertIn(self.ledger_name, response.content.decode())

    def test_update_with_get_does_not_update(self):
        self.client.login(username='joe', password='pass')
        new_name = 'New Ledger Name'

        response = self.client.get(reverse('ledger_update', args=[self.ledger_two.pk]))

        ledger = Ledger.objects.get(pk=self.ledger_two.pk)
        self.assertNotEqual(ledger.name, new_name)

    def test_update_with_post_does_update(self):
        self.client.login(username='joe', password='pass')
        url = reverse('ledger_update', args=[self.ledger_two.pk])
        new_name = 'New Ledger Name'

        response = self.client.post(url, data={'name': new_name})

        ledger = Ledger.objects.get(pk=self.ledger_two.pk)
        self.assertEqual(ledger.name, new_name)

    def test_delete_with_get_does_not_delete(self):
        self.client.login(username='joe', password='pass')
        url = reverse('ledger_delete', args=[self.ledger_two.pk])

        response = self.client.get(url)

        self.assertTrue(Ledger.objects.filter(pk=self.ledger_two.pk).exists())

    def test_delete_with_confirm_does_delete(self):
        self.client.login(username='joe', password='pass')
        url = reverse('ledger_delete', args=[self.ledger_two.pk])

        response = self.client.post(url)

        self.assertFalse(Ledger.objects.filter(pk=self.ledger_two.pk).exists())


def create_test_data(test):
    test.username, test.password = 'joe', 'pass'
    test.user = User.objects.create_user(username=test.username, password=test.password)
    test.ledger = Ledger.objects.create(user=test.user, name='My Ledger')
    test.record = Record.objects.create(date=date(2019, 9, 14), ledger=test.ledger)
    test.account_cash = Account.objects.create(
        name='cash', type=Account.DESTINATION, ledger=test.ledger)
    test.account_expense_one = Account.objects.create(
        name='expense one', type=Account.ORIGIN, ledger=test.ledger)
    test.account_expense_two = Account.objects.create(
        name='expense two', type=Account.ORIGIN, ledger=test.ledger)
    test.variation_cash = Variation.objects.create(
        amount=-100, record=test.record, account=test.account_cash)
    test.variation_expense_one = Variation.objects.create(
        amount=-40, record=test.record, account=test.account_expense_one)
    test.variation_expense_two = Variation.objects.create(
        amount=-60, record=test.record, account=test.account_expense_two)


class TestRecordViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_data(cls)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.ledger.delete()
        super().tearDownClass()

    def test_records_page(self):
        url = reverse('record_list', args=[self.ledger.pk])

        response = self.client.get(url)

        self.assertTemplateUsed(response, 'ledger/record_list.html')
        self.assertContains(response, 'expense one')

    def test_record_detail_json(self):
        url = reverse('record_detail_json', args=[self.ledger.pk, self.record.pk])

        response = self.client.get(url)

        expected = {
            "date": "2019-09-14",
            "id": 1,
            "is_balanced": True,
            "variations": {"credit": [{"account_name": "cash",
                                       "account_url": "/ledger/1/account/1/",
                                       "amount": 100.0,
                                       "id": 1}],
                           "debit": [{"account_name": "expense two",
                                      "account_url": "/ledger/1/account/3/",
                                      "amount": 60.0,
                                      "id": 3},
                                     {"account_name": "expense one",
                                      "account_url": "/ledger/1/account/2/",
                                      "amount": 40.0,
                                      "id": 2}]}
        }
        self.assertEqual(json.loads(response.content), expected)


class TestAccountViews(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='joe', password='pass')
        cls.ledger = Ledger.objects.create(user=cls.user, name='My Ledger')
        cls.account_cash = Account.objects.create(
            name='cash', type=Account.DESTINATION, ledger=cls.ledger)
        cls.account_wallet = Account.objects.create(
            name='wallet', type=Account.DESTINATION, parent=cls.account_cash, ledger=cls.ledger)
        cls.account_bank_one = Account.objects.create(
            name='bank one', type=Account.DESTINATION,
            parent=cls.account_wallet, ledger=cls.ledger)
        cls.account_bank_two = Account.objects.create(
            name='bank two', type=Account.DESTINATION,
            parent=cls.account_wallet, ledger=cls.ledger)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_account_list(self):
        url = reverse('account_list', args=[self.ledger.pk])

        response = self.client.get(url, content_type='application/json')

        self.assertTemplateUsed(response, 'ledger/account_list.html')

    def test_account_get_create(self):
        response = self.client.get(reverse('account_create', args=[self.ledger.pk]))

        self.assertTemplateUsed(response, 'ledger/account_create.html')

    def test_account_post_create(self):
        account_name = 'bank three'
        data = {
            'name': account_name,
            'parent': self.account_cash.pk,
        }

        response = self.client.post(reverse('account_create', args=[self.ledger.pk]), data=data)

        exists = Account.objects.filter(name=account_name).exists()
        self.assertTrue(exists)

    def test_account_get_delete(self):
        account = Account.objects.create(name='account', type=Account.DESTINATION, ledger=self.ledger)
        url = reverse('account_delete', args=[self.ledger.pk, account.pk])

        response = self.client.get(url)

        self.assertTemplateUsed(response, 'ledger/account_delete.html')
        self.assertContains(response, account.name)
        self.assertTrue(Account.objects.filter(name='account').exists())

        account.delete()

    def test_account_delete_post(self):
        account = Account.objects.create(name='account two', type=Account.DESTINATION, ledger=self.ledger)
        url = reverse('account_delete', args=[self.ledger.pk, account.pk])

        response = self.client.post(url, follow=True)

        self.assertTemplateUsed(response, 'ledger/account_list.html')
        self.assertFalse(Account.objects.filter(name='account').exists())
