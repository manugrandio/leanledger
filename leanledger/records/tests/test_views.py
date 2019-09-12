import json
from collections import namedtuple

from django.test import TestCase
from django.urls import reverse
from bs4 import BeautifulSoup

from leanledger.records.models import Account


class TestRecordsView(TestCase):
    @classmethod
    def setUpClass(cls):
        print('setUp')

    @classmethod
    def tearDownClass(cls):
        print('tearDown')

    def test_records_page(self):
        url = reverse('records_list')
        content = self.client.get(url).content

        soup = BeautifulSoup(content, 'html.parser')
        rows = soup.find('table').find('tbody').find_all('tr')
        total = sum(int(row.find_all('td')[-1].string) for row in rows)

        self.assertEqual(total, 100)


class TestAccountsView(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.account_cash = Account.objects.create(name='cash', type=Account.DESTINATION)
        cls.account_wallet = Account.objects.create(
            name='wallet', type=Account.DESTINATION, parent=cls.account_cash)
        cls.account_bank_one = Account.objects.create(
            name='bank one', type=Account.DESTINATION, parent=cls.account_wallet)
        cls.account_bank_two = Account.objects.create(
            name='bank two', type=Account.DESTINATION, parent=cls.account_wallet)

    @classmethod
    def tearDownClass(cls):
        Account.objects.all().delete()

    def test_accounts_list(self):
        url = reverse('accounts_tree')
        content = self.client.post(url, content_type='application/json').content

        soup = BeautifulSoup(content, 'html.parser')
        bank = soup.find('ul').find('li').find('ul').find('li')
        bank_one = bank.find('ul').find('li').string

        self.assertEqual(bank_one.strip(), 'bank one')
