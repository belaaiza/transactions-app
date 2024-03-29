import signal

from transactions.models import Transaction

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from transactions.tests.factories.transaction_factory import TransactionsFactory
from transactions.tests.fixtures.transaction_payload import test_payload
from transactions.tests.fixtures.big_transactions_payload import big_transactions_test_payload

TRANSACTION_URL = reverse('transaction:transaction-list')


class TransactionAPITests(APITestCase):
    factory = TransactionsFactory

    def handle_timeout(self, signum, frame):
        raise TimeoutError("Test execution exceeded the timeout.")

    def setUp(self):
        super().setUp()
        self.basic_payload = {
            'reference': '000001',
            'date': '2020-01-03',
            'amount': '-51.13',
            'type': 'outflow',
            'category': 'groceries',
            'user_email': 'janedoe@email.com'
        }

    def test_create_transaction(self):
        res = self.client.post(TRANSACTION_URL, self.basic_payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        transaction = Transaction.objects.get(reference=res.data['reference'])
        self.assertEqual(transaction.reference, self.basic_payload['reference'])
        self.assertEqual(transaction.date.strftime('%Y-%m-%d'), self.basic_payload['date'])
        self.assertEqual(transaction.amount, -5113)
        self.assertEqual(transaction.type, self.basic_payload['type'])
        self.assertEqual(transaction.category, self.basic_payload['category'])
        self.assertEqual(transaction.user_email, self.basic_payload['user_email'])
        self.assertNumQueries(1)

    def test_create_duplicated_transaction_should_return_400(self):
        self.factory.create(reference='000001')

        res = self.client.post(TRANSACTION_URL, self.basic_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['reference'][0], 'transaction with this reference already exists.')

    def test_create_multiple_invalid_transactions_should_return_400(self):
        self.basic_payload['type'] = 'inflow'
        self.basic_payload['amount'] = '-51.13'

        another_transaction = dict(self.basic_payload)
        another_transaction['reference'] = '000002'
        another_transaction['type'] = 'inflow'
        another_transaction['amount'] = '-51.13'

        payload = [
            self.basic_payload,
            another_transaction
        ]

        res = self.client.post(TRANSACTION_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['amount'][0], 'Amount should be a positive decimal for an inflow transaction.')

    def test_create_multiple_valid_transactions_successfully(self):
        another_transaction = dict(self.basic_payload)
        another_transaction['reference'] = '000002'

        payload = [
            self.basic_payload,
            another_transaction
        ]

        res = self.client.post(TRANSACTION_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), len(payload))
        self.assertNumQueries(1)

    def test_invalid_amount_should_return_400(self):
        self.basic_payload['amount'] = '-a.13'

        res = self.client.post(TRANSACTION_URL, self.basic_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['amount'][0], 'Invalid amount format.')

    def test_negative_amount_with_inflow_type_should_return_400(self):
        self.basic_payload['type'] = 'inflow'
        self.basic_payload['amount'] = '-51.13'

        res = self.client.post(TRANSACTION_URL, self.basic_payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['amount'][0], 'Amount should be a positive decimal for an inflow transaction.')

    def test_positive_amount_with_outflow_type_should_return_400(self):
        self.basic_payload['type'] = 'outflow'
        self.basic_payload['amount'] = '51.13'

        res = self.client.post(TRANSACTION_URL, self.basic_payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['amount'][0], 'Amount should be a negative decimal for an outflow transaction.')

    def test_list_transactions_grouped_by_type_and_user_succesfully(self):
        for data in test_payload:
            self.factory.create(**data)

        res = self.client.get(TRANSACTION_URL + '?group_by=type', vHTTP_ACCEPT='application/json')

        expected_data = [
            {
                'user_email': 'janedoe@email.com',
                'total_inflow': '2651.44',
                'total_outflow': '-761.85'
            }
        ]

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_data)
        self.assertNumQueries(1)

    def test_list_transactions_with_invalid_groupe_by_param_should_return_501(self):
        res = self.client.get(TRANSACTION_URL + '?group_by=random', vHTTP_ACCEPT='application/json')

        self.assertEqual(res.status_code, status.HTTP_501_NOT_IMPLEMENTED)

    def test_list_user_transactions_grouped_by_category_succesfully(self):
        for data in test_payload:
            self.factory.create(**data)

        url = reverse('transaction:transaction-summary', kwargs={'user_email': 'janedoe@email.com'})
        res = self.client.get(url)

        expected_data = {
            'inflow': {
                'salary': '2500.72',
                'savings': '150.72'
            },
            'outflow': {
                'groceries': '-51.13',
                'rent': '-560.00',
                'transfer': '-150.72'
            }
        }

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_data)
        self.assertNumQueries(1)

    def test_performance(self):
        timeout_seconds = 8
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(timeout_seconds)

        try:
            res = self.client.post(TRANSACTION_URL, big_transactions_test_payload, format='json')
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            self.assertNumQueries(1)
        finally:
            signal.alarm(0)

