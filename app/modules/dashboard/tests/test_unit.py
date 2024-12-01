import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_dashboard(client):
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert 'Dashboard' in response.get_data(as_text=True)
    