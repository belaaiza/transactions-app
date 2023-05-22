from transactions.models import Transaction
from transactions.serializers import TransactionSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def get_serializer(self, *args, **kwargs):  
        if isinstance(kwargs.get('data', {}), list):  
            kwargs['many'] = True  
    
        return super(TransactionViewSet, self).get_serializer(*args, **kwargs) 

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
