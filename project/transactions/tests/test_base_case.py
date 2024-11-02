import time

import pytest


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
