from rest_framework import serializers
from .models import Transaction, Investment


class TransactionSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Amount must be greater than 0."
            )

        return value

    def validate_category(self, category):
        request = self.context.get("request")

        if (
            request
            and category.user_id is not None
            and category.user_id != request.user.id
        ):
            raise serializers.ValidationError(
                "You cannot use another user's category."
            )

        return category

    class Meta:
        model = Transaction
        fields = [
            "user",
            "amount",
            "transaction_type",
            "description",
            "date",
            "category",
        ]
        read_only_fields = ["user", "date"]


class InvestmentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate_symbol(self, value):
        return value.strip().upper()

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than 0."
            )
        return value


    def validate_buy_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Buy price must be greater than 0."
            )
        return value

    class Meta:
        model = Investment
        fields = [
            "id",
            "user",
            "symbol",
            "quantity",
            "buy_price",
            "purchase_date",
        ]
        read_only_fields = ["user", "purchase_date"]