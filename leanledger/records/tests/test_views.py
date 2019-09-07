from django.test import TestCase
from django.urls import reverse

from bs4 import BeautifulSoup


class TestRecordsViews(TestCase):
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
