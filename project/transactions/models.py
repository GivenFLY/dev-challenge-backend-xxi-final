from django.db import models


class TypeChoices(models.TextChoices):
    SUPPLY = "supply", "Supply"
    SALE = "sale", "Sale"


class Transaction(models.Model):
    transaction_type = models.CharField(max_length=16, choices=TypeChoices.choices)
    sku = models.CharField(max_length=128)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    when = models.DateTimeField()
