from rest_framework import serializers


class SupplySerializer(serializers.Serializer):
    when = serializers.DateTimeField()
    sku = serializers.CharField()
    qty = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_sku(self, value: str):
        if not value.strip():
            raise serializers.ValidationError("SKU must be a string")
        return value

    def validate_qty(self, value: int):
        if value < 1:
            raise serializers.ValidationError("Quantity must be a positive integer")
        return value

    def validate_price(self, value: float):
        if value < 0:
            raise serializers.ValidationError("Price must be a non-negative number")
        return value


class SaleSerializer(serializers.Serializer):
    when = serializers.DateTimeField()
    sku = serializers.CharField()
    qty = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_sku(self, value: str):
        if not value.strip():
            raise serializers.ValidationError("SKU must be a string")
        return value

    def validate_qty(self, value: int):
        if value < 1:
            raise serializers.ValidationError("Quantity must be a positive integer")
        return value

    def validate_price(self, value: float):
        if value < 0:
            raise serializers.ValidationError("Price must be a non-negative number")
        return value


class AvailabilityResponseSerializer(serializers.Serializer):
    sku = serializers.CharField()
    qty = serializers.IntegerField()
    cost = serializers.FloatField()


class IssuesResponseSerializer(serializers.Serializer):
    when = serializers.DateTimeField()
    sku = serializers.CharField()
    qty = serializers.IntegerField()
    price = serializers.FloatField()
    message = serializers.CharField()
