from transactions.serializers import TransactionSummarySerializer
from transactions.serializers import TransactionSerializer
from transactions.models import Transaction
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db.models import Sum, Q

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def get_serializer(self, *args, **kwargs):  
        """Set `many` kwargs as True when creating multiple transactions at once"""
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
    
        return super(TransactionViewSet, self).get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        group_by = request.query_params.get('group_by', None)

        if group_by == 'type':
            grouped_by_type_serializer = self.group_by_type()
            return Response(grouped_by_type_serializer.data)
        else:
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def group_by_type(self):
        summary = Transaction.objects.values('user_email').annotate(
                total_inflow=Sum('amount', filter=Q(type='inflow')),
                total_outflow=Sum('amount', filter=Q(type='outflow'))
            )
        return TransactionSummarySerializer(summary, many=True)

