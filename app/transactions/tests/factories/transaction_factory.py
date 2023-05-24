from datetime import datetime

import factory
from factory.django import DjangoModelFactory

from transactions.models import Transaction


class TransactionsFactory(DjangoModelFactory):
    class Meta:
        model = Transaction

    reference = factory.Faker('pystr', max_chars=5)
    date = datetime.now()
    amount = 100
    type = 'inflow'
    category = 'groceries'
    user_email = factory.Faker('email')