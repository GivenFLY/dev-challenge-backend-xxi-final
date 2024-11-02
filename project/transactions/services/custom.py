from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from functools import cached_property
from typing import List

import pytest
from django.db import models
from django.db.models import QuerySet

from transactions.models import Transaction


def get_querysets(date_from: datetime, date_to: datetime) -> [QuerySet, QuerySet]:
    """
    Returns supply and sale querysets
    :param date_from: Date from
    :param date_to: Date to
    :return: [supply_queryset, sale_queryset]
    """
    queryset = Transaction.objects.all().order_by("when")

    if date_to:
        queryset = queryset.filter(when__lte=date_to)

    if date_from:
        queryset = queryset.filter(when__gte=date_from)

    supplies = queryset.filter(transaction_type="supply")
    sales = queryset.filter(transaction_type="sale")

    return supplies, sales


def group_by_sku(queryset: models.QuerySet) -> dict:
    """
    Group queryset by sku
    :param queryset: Queryset
    :return: {sku: [items]}
    """
    result = defaultdict(list)

    for item in queryset:
        result[item.sku].append(item)

    return result


class AvailabilityRetriever:
    def __init__(self, date_to: datetime = None):
        self.date_to = date_to
        self.supplies, self.sales = get_querysets(None, date_to)
        self.supplies_dict = group_by_sku(self.supplies)
        self.total_supplies = {}
        self.__available_items = None
        self.__issues = []

    @cached_property
    def available_items(self):
        if isinstance(self.__available_items, dict):
            return self.__available_items

        self.obtain_total_supplies()
        self.obtain_available_items()
        return self.__available_items

    def get_issues(self, date_from: datetime = None):
        if isinstance(self.__available_items, dict):
            issues = self.__issues

        else:
            self.obtain_total_supplies()
            self.obtain_available_items()
            issues = self.__issues

        if date_from:
            issues = [issue for issue in issues if issue[0].when >= date_from]

        return issues

    def obtain_total_supplies(self):
        for supply in self.supplies:
            total_qty = self.total_supplies.get(supply.sku, {}).get("qty", 0)
            cost = self.total_supplies.get(supply.sku, {}).get("cost", 0)

            self.total_supplies[supply.sku] = {
                "qty": total_qty + supply.qty,
                "cost": cost + (supply.price * supply.qty),
            }

    def obtain_available_items(self):
        """
        Get available items by date
        :return: {sku: {qty, cost}}
        """
        if self.__available_items:
            return self.__available_items

        total_supplies = deepcopy(self.total_supplies)
        supplies_dict = deepcopy(self.supplies_dict)

        for sale in self.sales:
            supplies = supplies_dict.get(sale.sku, [])

            if not supplies:
                self.__issues.append([sale, "out_of_stock"])
                continue

            if total_supplies[sale.sku]["qty"] < sale.qty:
                self.__issues.append([sale, "out_of_stock"])
                continue

            affected_supplies = []
            sale_qty = sale.qty
            total_supply_cost = 0

            for idx, supply in enumerate(supplies):
                affected_supplies.append(supply)
                total_supply_cost += supply.price * min(supply.qty, sale_qty)

                if supply.qty >= sale_qty:
                    break

                sale_qty -= supply.qty

            total_sale_cost = sale.qty * sale.price

            if total_supply_cost > total_sale_cost:
                self.__issues.append([sale, "negative_margin"])
                continue

            last_affected_supply = affected_supplies[-1]
            supplies_to_delete_amount = len(affected_supplies[:-1])

            if last_affected_supply.qty == sale.qty:
                supplies_to_delete_amount += 1

            else:
                last_affected_supply.qty -= sale.qty

            if supplies_to_delete_amount:
                supplies_dict[sale.sku] = supplies_dict[sale.sku][
                    supplies_to_delete_amount:
                ]

            total_supplies[sale.sku]["qty"] -= sale.qty
            total_supplies[sale.sku]["cost"] -= total_supply_cost

        self.__available_items = total_supplies
        return self.__available_items


def get_available_items(date_to: datetime = None) -> dict:
    """
    Get available items by date
    :return: {sku: {qty, cost}}
    """
    retriever = AvailabilityRetriever(date_to)
    return retriever.available_items


def get_issues(from_date: datetime, to_date: datetime):
    """
    Get issues by date
    :param from_date: Date from
    :param to_date: Date to
    :return: [[Transaction, "out_of_stock"], [Transaction, "negative_margin"] ... [...]]
    """
    retriever = AvailabilityRetriever(to_date)
    return retriever.get_issues(from_date)


def get_profit(from_date: datetime, to_date: datetime): ...
