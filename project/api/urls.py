from django.urls import path

from transactions.views import (
    SupplyAPIView,
    AvailabilityAPIView,
    SalesAPIView,
    FlushAPIView,
    IssuesAPIView,
)

urlpatterns = [
    path("supply/", SupplyAPIView.as_view(), name="supply"),
    path("sales/", SalesAPIView.as_view(), name="sales"),
    path("availability/", AvailabilityAPIView.as_view(), name="availability"),
    path("issues/", IssuesAPIView.as_view(), name="issues"),
    path("flush/", FlushAPIView.as_view(), name="flush"),
]
