from rest_framework.test import APIClient

from transactions.tests.conftest import *


@pytest.fixture
def api_client():
    return APIClient()
