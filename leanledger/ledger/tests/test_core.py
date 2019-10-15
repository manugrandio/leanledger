from unittest import TestCase
from unittest.mock import Mock


from ..core import record_is_balanced


class TestRecordIsBalanced(TestCase):
    def test_increases_ok(self):
        record = Mock(variations=[
            Mock(amount=100, type='debit'),
            Mock(amount=80, type='credit'),
            Mock(amount=20, type='credit'),
        ])

        self.assertTrue(record_is_balanced(record))

    def test_increases_ko(self):
        record = Mock(variations=[
            Mock(amount=100, type='debit'),
            Mock(amount=80, type='credit'),
            Mock(amount=40, type='credit'),
        ])

        self.assertFalse(record_is_balanced(record))

    def test_decreases_ok(self):
        record = Mock(variations=[
            Mock(amount=-100, type='debit'),
            Mock(amount=-80, type='credit'),
            Mock(amount=-20, type='credit'),
        ])

        self.assertTrue(record_is_balanced(record))

    def test_decreases_ko(self):
        record = Mock(variations=[
            Mock(amount=-100, type='debit'),
            Mock(amount=-80, type='credit'),
            Mock(amount=-30, type='credit'),
        ])

        self.assertFalse(record_is_balanced(record))

    def test_mixed_ok(self):
        record = Mock(variations=[
            Mock(amount=100, type='debit'),
            Mock(amount=-80, type='debit'),
            Mock(amount=20, type='credit'),
        ])

        self.assertTrue(record_is_balanced(record))

    def test_mixed_ko(self):
        record = Mock(variations=[
            Mock(amount=100, type='debit'),
            Mock(amount=-70, type='credit'),
            Mock(amount=20, type='credit'),
        ])

        self.assertFalse(record_is_balanced(record))
