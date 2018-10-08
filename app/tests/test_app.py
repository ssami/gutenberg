import pytest
import src

@pytest.fixture()
def client():

    client = src.app.test_client()
