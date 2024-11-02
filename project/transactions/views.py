from datetime import datetime

from rest_framework import generics, status
from rest_framework.response import Response

from transactions.models import Transaction
from transactions.serializers import (
    SupplySerializer,
    SaleSerializer,
    AvailabilityResponseSerializer,
    IssuesResponseSerializer,
)

from transactions.services.crud import add_supplies, add_sales
from transactions.services.custom import get_available_items, get_issues


class SupplyAPIView(generics.CreateAPIView):
    serializer_class = SupplySerializer

    def post(self, request, *args, **kwargs):
        data = request.data.get("data", [])
        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        supplies = serializer.validated_data
        success = add_supplies(supplies)

        response = {"data": {"success": success}}

        return Response(response, status=status.HTTP_201_CREATED)


class SalesAPIView(generics.CreateAPIView):
    serializer_class = SaleSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.get("data", [])
        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        sales = serializer.validated_data

        success, issues = add_sales(sales)
        response = {"data": {"success": success, "issues": issues}}

        return Response(response, status=status.HTTP_201_CREATED)


class AvailabilityAPIView(generics.ListAPIView):
    serializer_class = AvailabilityResponseSerializer

    def get(self, request, *args, **kwargs):
        to = request.query_params.get("to")

        if to:
            to = datetime.fromisoformat(to)

        else:
            to = datetime.now()

        available_items = [
            {"sku": sku, "qty": item["qty"], "cost": item["cost"]}
            for sku, item in get_available_items(to).items()
        ]

        serializer = self.get_serializer(instance=available_items, many=True)

        response = {"data": serializer.data}

        return Response(response, status=status.HTTP_200_OK)


class IssuesAPIView(generics.ListAPIView):
    serializer_class = IssuesResponseSerializer

    def get(self, request, *args, **kwargs):
        date_from = request.query_params.get("from")
        date_to = request.query_params.get("to")

        if date_from:
            date_from = datetime.fromisoformat(date_from)

        if date_to:
            date_to = datetime.fromisoformat(date_to)

        issues = get_issues(date_from, date_to)

        result = []
        for issue in issues:
            result.append(
                {
                    "sku": issue[0].sku,
                    "qty": issue[0].qty,
                    "price": issue[0].price,
                    "when": issue[0].when,
                    "message": issue[1],
                }
            )

        serializer = self.get_serializer(instance=result, many=True)

        response = {"data": serializer.data}

        return Response(response, status=status.HTTP_200_OK)


class FlushAPIView(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        num_deleted, _ = Transaction.objects.all().delete()

        return Response(
            {"data": {"success": num_deleted}}, status=status.HTTP_204_NO_CONTENT
        )
