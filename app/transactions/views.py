from transactions.models import Transaction
from transactions.serializers import TransactionSerializer
from rest_framework import viewsets

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()