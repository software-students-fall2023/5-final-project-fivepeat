# tests/test_app.py

import pytest
from app import app
from flask import session
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

# Testing the '/login' route
def test_login_route(client):
    response = client.get('/login')
    assert response.status_code == 302  # Ensure proper redirection

