from unittest import TestCase
from transactions.models import Transaction

from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

TRANSACTION_URL = reverse('transaction:transaction-list')

class TransactionAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_transaction(self):
        payload = {
            'reference': '000051',
            'date': '2020-01-03',
            'amount': '-51.13',
            'type': 'outflow',
            'category': 'groceries',
            'user_email': 'janedoe@email.com'
        }

        res = self.client.post(TRANSACTION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
       
        transaction = Transaction.objects.get(reference=res.data['reference'])
        self.assertEqual(transaction.reference, payload['reference'])
        self.assertEqual(transaction.date.strftime('%Y-%m-%d'), payload['date'])
        self.assertEqual(transaction.amount, -5113)
        self.assertEqual(transaction.type, payload['type'])
        self.assertEqual(transaction.category, payload['category'])
        self.assertEqual(transaction.user_email, payload['user_email'])

    def test_invalid_amount(self):
        payload = {
            'reference': '000052',
            'date': '2020-01-03',
            'amount': '-a.13',
            'type': 'outflow',
            'category': 'groceries',
            'user_email': 'janedoe@email.com'
        }

        res = self.client.post(TRANSACTION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_multiple_transactions(self):
        payload = [{
            'reference': '000053',
            'date': '2020-01-03',
            'amount': '-51.13',
            'type': 'outflow',
            'category': 'groceries',
            'user_email': 'janedoe@email.com'
        },
        {
            'reference': '000054',
            'date': '2020-01-03',
            'amount': '-51.13',
            'type': 'outflow',
            'category': 'groceries',
            'user_email': 'janedoe@email.com'
        }
        ]

        res = self.client.post(TRANSACTION_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
       
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), len(payload))

    def test_negative_amount_with_inflow_type(self):
        payload = {
            'reference': '000052',
            'date': '2020-01-03',
            'amount': '-10.13',
            'type': 'inflow',
            'category': 'groceries',
            'user_email': 'janedoe@email.com'
        }

        res = self.client.post(TRANSACTION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_positive_amount_with_outflow_type(self):
        payload = {
            'reference': '000052',
            'date': '2020-01-03',
            'amount': '10.13',
            'type': 'outflow',
            'category': 'groceries',
            'user_email': 'janedoe@email.com'
        }

        res = self.client.post(TRANSACTION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        