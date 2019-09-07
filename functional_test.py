from unittest import TestCase

from requests import get
from selenium import webdriver


class TestDjangoServer(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()

    def test_server_is_running(self):
        body = get('http://localhost:8000').content

        self.assertIn(b'Django', body)

    def test_server_is_running_selenium(self):
        self.browser.get('http://localhost:8000/records/')

        self.assertIn('Records', self.browser.title)
