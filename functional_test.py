from unittest import TestCase

from requests import get


class TestDjangoServer(TestCase):
    def test_server_is_running(self):
        body = get('http://localhost:8000').content

        self.assertIn(b'Django', body)
