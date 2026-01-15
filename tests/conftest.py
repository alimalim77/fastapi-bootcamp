import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add project root to sys.path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from index import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
