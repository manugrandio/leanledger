from django.test import TestCase

from ..forms import LedgerForm


class RecordFormTest(TestCase):
    def test_form_create(self):
        form = LedgerForm({'name': 'My Ledger'})

        self.assertTrue(form.is_valid())

    def test_form_create_empty_not_valid(self):
        form = LedgerForm({'name': ''})

        self.assertFalse(form.is_valid())
