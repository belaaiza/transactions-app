"""
Test for models.
"""

from datetime import datetime
from decimal import Decimal
from django.test import TestCase

from transactions import models

class ModelTests(TestCase):
    """Test models."""

    def test_create_transaction_successfully(self):
        """Tests the creation of a successfull transaction for valid data"""
        transaction = models.Transaction.objects.create(
            user_email='janedoe@email.com',
            reference='000051',
            date=datetime.strptime('2020-01-13', '%Y-%m-%d').date(),
            amount=-5113,
            type='outflow',
            category='groceries'
        )
        self.assertEqual(str(transaction), transaction.reference)