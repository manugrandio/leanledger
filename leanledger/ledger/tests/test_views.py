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
        response = self.client.get('/ledger/new/')

        self.assertTemplateUsed(response, 'ledger/ledger_new.html')

    def test_post_new(self):
        self.client.login(username='joe', password='pass')
        data = {'name': self.ledger_name}

        response = self.client.post(reverse('ledger_new'), data=data, follow=True)

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
        url = reverse('records', args=[self.ledger.pk])

        response = self.client.get(url)

        self.assertTemplateUsed(response, 'ledger/records_list.html')
        self.assertContains(response, 'expense one')

    def test_record_create_get(self):
        url = reverse('record_create', args=[self.ledger.pk])

        response = self.client.get(url)

        self.assertTemplateUsed(response, 'ledger/record_create.html')
        self.assertContains(response, 'form')

    def test_record_create_post(self):
        url = reverse('record_create', args=[self.ledger.pk])
        description = 'Record Description'
        data = {
            'description': description,
            'date': '2019-10-01',
        }

        response = self.client.post(url, args=[self.ledger.pk], data=data, follow=True)

        self.assertTemplateUsed(response, 'ledger/record.html')
        self.assertContains(response, description)


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

    def test_accounts_list(self):
        url = reverse('accounts', args=[self.ledger.pk])

        response = self.client.get(url, content_type='application/json')

        self.assertTemplateUsed(response, 'ledger/accounts_list.html')

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


class TestVariationViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_data(cls)

    def test_get_partial(self):
        url = reverse('variation_create', args=[self.ledger.pk, self.record.pk])

        response = self.client.get(url)

        self.assertTemplateUsed(response, 'ledger/variation_create.html')
        self.assertContains(response, 'Amount')

    def test_get_variation_detail(self):
        args = [self.ledger.pk, self.record.pk, self.variation_cash.pk]
        url = reverse('variation_detail', args=args)

        response = self.client.get(url)

        self.assertTemplateUsed(response, 'ledger/variation_detail.html')
        self.assertContains(response, 'cash')
