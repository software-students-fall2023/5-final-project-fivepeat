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

# Test if unauthorized access to restricted pages redirects to login
def test_top_artists_route_unauthorized(client):
    response = client.get('/top_artists')
    assert response.status_code == 302
    assert b'/login' in response.data  # Check if redirected to login page

# Test if valid access token grants access to '/top_artists' route
def test_top_artists_route_authorized(client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'valid_token_here'
        sess['expires_at'] = 9999999999  # Future timestamp

    response = client.get('/top_artists')
    assert response.status_code == 200

# Test handling of callback with an error
def test_callback_error_handling(client):
    response = client.get('/callback?error=some_error')
    assert response.status_code == 200  # Check if it handles error

# Testing the '/refresh-token' route for unauthorized access
def test_refresh_token_route_unauthorized(client):
    response = client.get('/refresh-token')
    assert response.status_code == 302
    assert b'/login' in response.data  # Check if redirected to login page

# Test if valid refresh token grants access to '/refresh-token' route
'''def test_refresh_token_route_authorized(client):
    with client.session_transaction() as sess:
        sess['refresh_token'] = 'valid_refresh_token_here'
        sess['expires_at'] = 9999999999  # Future timestamp

    response = client.get('/refresh-token')
    assert response.status_code == 302
    assert b'/top_artists' in response.data  # Check if redirected to top_artists'''

# Testing the '/quiz' route for unauthorized access
def test_quiz_route_unauthorized(client):
    response = client.get('/quiz')
    assert response.status_code == 302
    assert b'/login' in response.data  # Check if redirected to login page

# Test if valid access token grants access to '/quiz' route
'''def test_quiz_route_authorized(client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'valid_token_here'
        sess['expires_at'] = 9999999999  # Future timestamp

    response = client.get('/quiz')
    assert response.status_code == 200'''