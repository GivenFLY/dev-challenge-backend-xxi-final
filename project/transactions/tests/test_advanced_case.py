import pytest
from datetime import datetime


@pytest.fixture
def supply_factory(supply_request):
    def wrapper():
        body = {
            "data": [
                {"when": "2024-10-28T17:41:38", "sku": "A", "qty": 2, "price": 100},
                {"when": "2024-10-29T12:22:11", "sku": "A", "qty": 2, "price": 105},
                {"when": "2024-10-29T12:22:11", "sku": "B", "qty": 5, "price": 110},
                {"when": "2024-10-29T12:33:33", "sku": "B", "qty": 5, "price": 115},
            ]
        }
        return supply_request(body)

    return wrapper


@pytest.fixture
def sale_factory(sales_request):
    def wrapper():
        body = {
            "data": [
                {"when": "2024-10-29T19:45:00", "sku": "A", "qty": 3, "price": 120},
                {"when": "2024-10-29T19:45:01", "sku": "B", "qty": 7, "price": 125},
                {"when": "2024-10-29T19:45:21", "sku": "C", "qty": 2, "price": 150},
            ]
        }
        return sales_request(body)

    return wrapper


@pytest.mark.django_db
def test_supply_create(supply_factory, assert_success_crud_response):
    response = supply_factory()
    assert_success_crud_response(response, 201, 4, 0)


@pytest.mark.django_db
def test_sale_create(supply_factory, sale_factory, assert_success_crud_response):
    supply_factory()
    response = sale_factory()
    assert_success_crud_response(response, 201, 2, 1)


@pytest.mark.django_db
def test_availability(availability_request, supply_factory, sale_factory):
    supply_factory()
    sale_factory()
    response = availability_request()
    expected_response = {
        "data": [
            {"sku": "A", "qty": 1, "cost": 105},
            {"sku": "B", "qty": 3, "cost": 345},
        ]
    }
    assert response.data == expected_response


@pytest.mark.django_db
def test_issues(issues_request, supply_factory, sale_factory):
    supply_factory()
    sale_factory()
    response = issues_request()
    expected_response = {
        "data": [
            {
                "sku": "C",
                "qty": 2,
                "price": 150,
                "when": "2024-10-29T19:45:21",
                "message": "out_of_stock",
            }
        ]
    }
    assert response.data == expected_response


@pytest.mark.django_db
def test_flush(flush_request, availability_request, supply_factory):
    supply_factory()
    response = availability_request()
    expected_response = {
        "data": [
            {"sku": "A", "qty": 4, "cost": 410},
            {"sku": "B", "qty": 10, "cost": 1125},
        ]
    }
    assert response.data == expected_response
    flush_request()
    response = availability_request()
    expected_response = {"data": []}
    assert response.data == expected_response


@pytest.mark.django_db
def test_supply_create_invalid_data(supply_request):
    body = {
        "data": [
            {"when": "invalid-date", "sku": "A", "qty": -5, "price": "one hundred"},
            {"when": "2024-10-29T12:22:11", "sku": "", "qty": 2, "price": 105},
        ]
    }
    response = supply_request(body)
    assert response.status_code == 422
    assert response.data.get("errors")


@pytest.mark.django_db
def test_sale_with_insufficient_supply(supply_factory, sales_request, issues_request):
    supply_factory()
    body = {
        "data": [
            {"when": "2024-10-30T10:00:00", "sku": "A", "qty": 10, "price": 120},
        ]
    }
    sales_request(body)
    response = issues_request()
    expected_issues = {
        "data": [
            {
                "sku": "A",
                "qty": 10,
                "price": 120,
                "when": "2024-10-30T10:00:00",
                "message": "out_of_stock",
            }
        ]
    }
    assert response.data == expected_issues


@pytest.mark.django_db
def test_sku_case_sensitivity(supply_request, sales_request, availability_request):
    supplies = {
        "data": [
            {"when": "2024-10-31T09:00:00", "sku": "a", "qty": 5, "price": 100},
            {"when": "2024-10-31T09:05:00", "sku": "A", "qty": 5, "price": 105},
        ]
    }
    supply_request(supplies)
    sales = {
        "data": [
            {"when": "2024-10-31T10:00:00", "sku": "a", "qty": 2, "price": 120},
            {"when": "2024-10-31T10:05:00", "sku": "A", "qty": 3, "price": 125},
        ]
    }
    sales_request(sales)
    response = availability_request()
    expected_response = {
        "data": [
            {"sku": "a", "qty": 3, "cost": 300},
            {"sku": "A", "qty": 2, "cost": 210},
        ]
    }
    assert response.data == expected_response


@pytest.mark.django_db
def test_sale_with_invalid_sku(supply_factory, sales_request, issues_request):
    supply_factory()
    sales = {
        "data": [
            {"when": "2024-10-31T11:00:00", "sku": "D", "qty": 1, "price": 150},
        ]
    }
    sales_request(sales)
    response = issues_request()
    expected_response = {
        "data": [
            {
                "sku": "D",
                "qty": 1,
                "price": 150,
                "when": "2024-10-31T11:00:00",
                "message": "out_of_stock",
            }
        ]
    }
    assert response.data == expected_response


@pytest.mark.django_db
def test_zero_quantity_operations(supply_request, sales_request, availability_request):
    supplies = {
        "data": [
            {"when": "2024-10-31T12:00:00", "sku": "E", "qty": 0, "price": 100},
        ]
    }
    supply_request(supplies)
    sales = {
        "data": [
            {"when": "2024-10-31T12:05:00", "sku": "E", "qty": 0, "price": 150},
        ]
    }
    sales_request(sales)
    response = availability_request()
    expected_response = {"data": []}
    assert response.data == expected_response


@pytest.mark.django_db
def test_flush_after_partial_operations(
    flush_request, availability_request, supply_factory, sale_factory, issues_request
):
    supply_factory()
    sale_factory()
    flush_request()
    response = availability_request()
    expected_response = {"data": []}
    assert response.data == expected_response
    issues_response = issues_request()
    expected_issues_response = {"data": []}
    assert issues_response.data == expected_issues_response


@pytest.mark.django_db
def test_concurrent_operations(
    supply_request, sales_request, availability_request, issues_request
):
    supplies = {
        "data": [
            {"when": "2024-11-01T09:00:00", "sku": "G", "qty": 10, "price": 100},
        ]
    }
    sales = {
        "data": [
            {"when": "2024-11-01T09:00:00", "sku": "G", "qty": 5, "price": 120},
        ]
    }
    supply_request(supplies)
    sales_request(sales)
    response = availability_request()
    expected_response = {
        "data": [
            {"sku": "G", "qty": 5, "cost": 500},
        ]
    }
    assert response.data == expected_response


@pytest.mark.django_db
def test_availability_with_future_date(supply_factory, availability_request):
    supply_factory()
    future_date = datetime(2025, 1, 1)
    response = availability_request(to=future_date)
    expected_response = {
        "data": [
            {"sku": "A", "qty": 4, "cost": 410},
            {"sku": "B", "qty": 10, "cost": 1125},
        ]
    }
    assert response.data == expected_response
