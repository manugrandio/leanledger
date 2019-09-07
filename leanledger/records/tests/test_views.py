from django.test import TestCase
from django.urls import reverse


class TestRecordsViews(TestCase):
    def test_records_page(self):
        response = self.client.get(reverse('records_list'))

        self.assertIn(b'hello', response.content)
