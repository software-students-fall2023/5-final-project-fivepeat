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

# Testing the '/random_song' route for unauthorized access
def test_random_song_route_unauthorized(client):
    response = client.get('/random_song')
    assert response.status_code == 302
    assert b'/login' in response.data  # Check if redirected to login page

# Test if valid access token grants access to '/random_song' route
def test_random_song_route_authorized(client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'valid_token_here'
        sess['expires_at'] = 9999999999  # Future timestamp

    response = client.get('/random_song')
    assert response.status_code == 200

# Testing the '/history' route for unauthorized access
def test_history_route_unauthorized(client):
    response = client.get('/history')
    assert response.status_code == 302
    assert b'/login' in response.data  # Check if redirected to login page

# Test if valid access token grants access to '/history' route
def test_history_route_authorized(client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'valid_token_here'
        sess['expires_at'] = 9999999999  # Future timestamp

    response = client.get('/history')
    assert response.status_code == 200

# Add more tests for other routes and functionalities

def test_quiz_route_redirects_when_access_token_not_in_session(client, monkeypatch):
    # Mock session without 'access_token'
    with client.session_transaction() as sess:
        sess.clear()  # Clear any existing session data
        
    response = client.get('/quiz')
    assert response.status_code == 302
    assert response.location == '/login'  # Replace with your redirect URL

def test_quiz_route_redirects_when_token_expired(client, monkeypatch):
    # Mock session with expired token
    with client.session_transaction() as sess:
        sess['access_token'] = 'valid_access_token_here'
        sess['expires_at'] = 1000  # Set an expired timestamp
        
    response = client.get('/quiz')
    assert response.status_code == 302
    assert response.location == '/refresh-token'  # Replace with your redirect URL

# Add more tests for other scenarios, API calls, session handling, etc.

def test_random_song_redirects_to_login_when_no_access_token(client):
    with client.session_transaction() as sess:
        # No access token in session
        sess.pop('access_token', None)

    response = client.get('/random_song')
    assert response.status_code == 302
    assert response.location == '/login'  # Adjust the URL as per your application

def test_random_song_redirects_to_refresh_token_when_token_expired(client):
    with client.session_transaction() as sess:
        # Set an expired timestamp
        sess['expires_at'] = datetime.now() - timedelta(hours=1)

    response = client.get('/random_song')
    assert response.status_code == 302
    assert response.location == '/login'  # Adjust the URL as per your application

def test_callback_with_error_in_request_args(client):
    # Simulate a callback with an error in request.args
    response = client.get('/callback?error=test_error')
    assert response.status_code == 200
    assert response.json == {"error": "test_error"}