from transactions.serializers import TransactionBulkCreateSerializer
from transactions.serializers import TransactionGroupedByTypeSerializer
from transactions.serializers import TransactionSerializer
from transactions.models import Transaction
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Q

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def get_serializer(self, *args, **kwargs):  
        """Set `many` kwargs as True when creating multiple transactions at once"""
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
    
        return super(TransactionViewSet, self).get_serializer(*args, **kwargs)

    @action(detail=False, url_path=r'(?P<user_email>[^/]+)/summary')
    def summary(self, request, user_email: str = None):
        """
        List the sum of amounts per transaction category for transactions made by a given user.

        Parameters
        ----------
        user_email : string
            The user to show the transactions.
        """
        inflow_summary = Transaction.objects.filter(user_email=user_email, type='inflow').values('category').annotate(
            total_amount=Sum('amount')
        )

        outflow_summary = Transaction.objects.filter(user_email=user_email, type='outflow').values('category').annotate(
            total_amount=Sum('amount')
        )

        summary = {
            'inflow': {item['category']: '{:.2f}'.format(item['total_amount'] / 100) for item in inflow_summary},
            'outflow': {item['category']: '{:.2f}'.format(item['total_amount'] / 100) for item in outflow_summary},
        }

        return Response(summary)

    def list(self, request, *args, **kwargs):
        """
        Action to list transactions. Supports the group_by=type query param, returning the
        total inflow and outflow per user.

        Returns
        ----------
        Reponse
            - HTTP status code 501 for query params different than group_by=type
            - Total inflow and outflow per user for query param group_by=type
            - The default list queryset when no query params are informed
        """
        group_by = request.query_params.get('group_by', None)

        if request.query_params and group_by != 'type':
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
        elif request.query_params and group_by == 'type':
            grouped_by_type_serializer = self.group_by_type()
            return Response(grouped_by_type_serializer.data)
        else:
            return super(TransactionViewSet, self).list(request, *args, **kwargs)


    def group_by_type(self):
        summary = Transaction.objects.values('user_email').annotate(
                total_inflow=Sum('amount', filter=Q(type='inflow')),
                total_outflow=Sum('amount', filter=Q(type='outflow'))
            )
        return TransactionGroupedByTypeSerializer(summary, many=True)
