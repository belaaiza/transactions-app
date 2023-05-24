"""
Serializers for transactions API.
"""
import decimal
from transactions.models import Transaction
from rest_framework import serializers
from django.db.utils import IntegrityError


class TransactionBulkCreateSerializer(serializers.ListSerializer):
    """Serializer for multiple transactions creation."""

    def create(self, validated_data):
        """
        Create multiple transactions at once using bulk_create.

        Raises
        ------
        IntegrityError
            If the data has transactions with same reference.
        """
        try:
            data = [Transaction(**item) for item in validated_data]
            return Transaction.objects.bulk_create(data)
        except IntegrityError:
            raise serializers.ValidationError('Reference must be unique.')

    def validate(self, data):
        """Validate each transaction in a multiple transaction creation."""
        for item in data:
            self.child.initial_data = item
            self.child.is_valid(raise_exception=True)
        return data


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions."""
    amount = serializers.CharField()

    class Meta:
        model = Transaction
        fields = ['user_email', 'reference', 'date', 'amount', 'type', 'category']
        list_serializer_class = TransactionBulkCreateSerializer

    def validate_amount(self, value: str) -> int:
        """
        Check if the amount is a valid decimal and complies with business rules.

        Parameters
        ----------
        value : str
            A string representing the transaction amount (example '00.00').

        Returns
        -------
        int
            The transaction amount value in cents.

        Raises
        ------
        ValidationError
            If the amount is not a valid decimal.
        """
        try:
            amount = self.amount_to_integer(value)
        except decimal.InvalidOperation:
            raise serializers.ValidationError('Invalid amount format.')

        data = self.get_initial()
        self.check_amount_according_type(data.get('type'), amount)

        return amount

    def amount_to_integer(self, amount: str) -> int:
        """Convert an amount string (example: '00.00') into an int with its value in cents."""
        amount_decimal = decimal.Decimal(amount)
        return int(amount_decimal * 100)

    def check_amount_according_type(self, type: str, amount: int):
        """
        Function to check if the amount is positive for inflow type transactions,
        and negative for outflow type transactions.

        Parameters
        ----------
        type : string
            The transaction type. Must be either 'inflow' or 'outflow'.

        amount : int
            The transaction amount in cents.

        Raises
        ------
        ValidationError
            For inflow transactions with negative values or outflow transactions with positive values.
        """
        if type == 'inflow' and amount < 0:
            raise serializers.ValidationError('Amount should be a positive decimal for an inflow transaction.')

        if type == 'outflow' and amount > 0:
            raise serializers.ValidationError('Amount should be a negative decimal for an outflow transaction.')


class AmountField(serializers.DecimalField):
    def to_representation(self, value: int) -> str:
        """Convert a value in cents to its string representation in the format '00.00'."""
        return f'{value/100:.2f}'


class TransactionGroupedByTypeSerializer(serializers.Serializer):
    """Serializer for the transactions list grouped by type."""

    user_email = serializers.EmailField()
    total_inflow = AmountField(max_digits=10, decimal_places=2)
    total_outflow = AmountField(max_digits=10, decimal_places=2)
