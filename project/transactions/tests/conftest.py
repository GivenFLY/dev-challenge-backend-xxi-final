from datetime import datetime

import pytest
from django.urls import reverse


@pytest.fixture
def supply_request(api_client):
    def wrapper(body):
        url = reverse("api:supply")
        response = api_client.post(url, body, format="json")
        return response

    return wrapper


@pytest.fixture
def sales_request(api_client):
    def wrapper(body):
        url = reverse("api:sales")
        response = api_client.post(url, body, format="json")
        return response

    return wrapper


@pytest.fixture
def availability_request(api_client):
    def wrapper(to: datetime = None):
        if to is None:
            to = datetime.now()

        params = {"to": to.isoformat()}
        url = reverse("api:availability")
        response = api_client.get(url, params, format="json")
        return response

    return wrapper


@pytest.fixture
def flush_request(api_client):
    def wrapper():
        url = reverse("api:flush")
        response = api_client.delete(url, format="json")
        return response

    return wrapper


@pytest.fixture
def issues_request(api_client):
    def wrapper(from_date=None, to_date=None):
        params = {}
        if from_date:
            params["from"] = from_date.isoformat()

        if to_date:
            params["to"] = to_date.isoformat()

        url = reverse("api:issues")
        response = api_client.get(url, params, format="json")
        return response

    return wrapper


@pytest.fixture
def assert_success_crud_response():
    def wrapper(response, status, success, issues):
        assert response.status_code == status

        data = response.data.get("data")

        assert data is not None

        assert data.get("success", 0) == success
        assert data.get("issues", 0) == issues

    return wrapper
