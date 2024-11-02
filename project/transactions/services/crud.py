import logging
from datetime import datetime

import pytest

from transactions.models import Transaction
from transactions.services.custom import get_available_items


def add_supplies(supplies: list) -> int:
    """
    Creates transactions
    :param supplies: list of {sku; qty; price; when}
    :return: number of insertions
    """

    for supply in supplies:
        Transaction.objects.create(
            transaction_type="supply",
            sku=supply["sku"],
            qty=supply["qty"],
            price=supply["price"],
            when=supply["when"],
        )

    return len(supplies)


def add_sales(sales: list) -> [int, int]:
    """
    Creates transactions
    :param sales: list of {sku; qty; price; when}
    :return: [number of successful insertions, number of failed insertions]
    """

    issues = 0

    for sale in sales:
        items = get_available_items(sale["when"])

        Transaction.objects.create(
            transaction_type="sale",
            sku=sale["sku"],
            qty=sale["qty"],
            price=sale["price"],
            when=sale["when"],
        )

        item = items.get(sale["sku"], {})
        item_qty = item.get("qty", 0)

        # Check if there is enough quantity
        if sale["qty"] > item_qty:
            logging.error(f"Insufficient quantity for {sale['sku']}")
            issues += 1
            continue

        total_price = sale.get("price", 0) * sale.get("qty", 0)

        item_price = item.get("cost", 0)

        # Check if there is enough price
        if total_price > item_price:
            logging.error(f"Insufficient price for {sale['sku']}")
            issues += 1
            continue

    return len(sales) - issues, issues
