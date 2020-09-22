import pytest

from api.main import app
from tests.e2e import CustomClient


@pytest.fixture(scope='module')
def user_client() -> CustomClient:
    client = CustomClient(app)
    return client
