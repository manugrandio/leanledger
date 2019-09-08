import json
from collections import namedtuple

from django.test import TestCase
from django.urls import reverse

from bs4 import BeautifulSoup


Account = namedtuple('Account', 'name, children')


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
    def test_accounts_list(self):
        accounts_destination = [
            {
                'name': 'cash',
                'children': [
                    {
                        'name': 'wallet',
                        'children': [
                            {'name': 'bank one', 'children': []},
                            {'name': 'bank two', 'children': []},
                        ],
                    },
                ],
            },
            {
                'name': 'receivable',
                'children': [],
            },
        ]
        accounts_origin = (
            Account('wage', (
                Account('job one', ()),
                Account('job two', ()),
            )),
        )
        payload = {
            'accounts_destination': accounts_destination,
            'accounts_origin': accounts_origin,
        }
        url = reverse('accounts_tree')
        content = self.client.post(url, data=payload, content_type='application/json').content

        soup = BeautifulSoup(content, 'html.parser')
        bank = soup.find('ul').find('li').find('ul').find('li')
        bank_one = bank.find('ul').find('li').string

        self.assertEqual(bank_one, 'bank one')
