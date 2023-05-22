"""
Serializers for transactions API.
"""
import re
from decimal import Decimal
from transactions.models import Transaction
from rest_framework import serializers

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions."""
    amount = serializers.CharField()

    class Meta:
        model = Transaction
        fields = ['user_email', 'reference', 'date', 'amount', 'type', 'category']

    def create(self, validated_data):
        """
        Create and return a new `Transaction` instance, given the validated data.
        """
        validated_data['amount'] = self.amount_to_integer(validated_data['amount'])
        return Transaction.objects.create(**validated_data)

    def validate_amount(self, value):
        pattern = r'^-?\d*\.?\d*$'
        match = re.match(pattern, value)
        if not match:
            raise serializers.ValidationError('Invalid amount format.')

        return value

    def amount_to_integer(self, amount):
        amount_decimal = Decimal(amount)
        return int(amount_decimal * 100)
