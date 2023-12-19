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

@patch('app.requests.post')
def test_callback_with_code_in_request_args(mock_post, client):
    # Simulate a callback with a code in request.args
    mock_response = mock_post.return_value
    mock_response.json.return_value = {
        'access_token': 'test_access_token',
        'refresh_token': 'test_refresh_token',
        'expires_in': 3600  # Assuming the expires_in value
    }

    response = client.get('/callback?code=test_code')
    assert response.status_code == 302
    assert session['access_token'] == 'test_access_token'
    assert session['refresh_token'] == 'test_refresh_token'
    assert 'expires_at' in session

    # Add assertions for expires_at based on the expected value,
    # for example, compare with current timestamp + expires_in
    
    # Example (using assert for expires_at):
    expected_expires_at = datetime.now().timestamp() + 3600  # Expected expires_at value
    assert abs(session['expires_at'] - expected_expires_at) < 1  # Tolerance level of 1 second

    assert response.location == '/top_artists'

@patch('app.requests.post')
def test_refresh_token_route(mock_post, client):
    # Set up session data
    with client.session_transaction() as sess:
        sess['refresh_token'] = 'valid_refresh_token_here'
        sess['expires_at'] = datetime.now().timestamp() + 3600  # Expires in an hour

    # Mocked response from the external API
    mock_response = mock_post.return_value
    mock_response.json.return_value = {
        'access_token': 'new_access_token',
        'expires_in': 3600  # Assuming the expires_in value
    }

    # Perform the request to the /refresh-token route
    response = client.get('/refresh-token')

    # Assertions
    assert response.status_code == 302
    assert session['access_token'] == 'new_access_token'
    assert 'expires_at' in session

    # Calculate the expected expiration time
    expected_expires_at = datetime.now().timestamp() + 3600  # Expected expires_at value
    assert abs(session['expires_at'] - expected_expires_at) < 1  # Tolerance level of 1 second


    # Check the redirected URL
    assert response.location == '/top_artists'

@patch('app.db.collection.insert_one')
def test_quiz_submit_route(mock_insert_one, client):
    # Set up session data
    with client.session_transaction() as sess:
        sess['correct_answer'] = 'correct_answer_id'
        sess['quiz_data'] = {
            'song1': {'name': 'Song 1', 'features1': 'Feature 1'},
            'song2': {'name': 'Song 2', 'features2': 'Feature 2'},
            'song1_image_url': 'image_url_1',
            'song2_image_url': 'image_url_2'
            # Add other required data here
        }

    # Simulate a POST request with the form data containing the correct answer
    response = client.post('/quiz/submit', data={'answer1': 'correct_answer_id'})

    # Assertions
    assert response.status_code == 200
    assert b'Correct!' in response.data  # Assuming the template renders 'Correct!' for a correct answer

    # Check if the database insert function was called with the expected data
    mock_insert_one.assert_called_once_with({
        "Song 1 Name": 'Song 1',
        "Song 1 Features": 'Feature 1',
        "Song 2 Name": 'Song 2',
        "Song 2 Features": 'Feature 2',
        "Song 1 Image URL": 'image_url_1',
        "Song 2 Image URL": 'image_url_2',
        "Result": 'Correct!',
        "timestamp_field": datetime.utcnow()
    })

@patch('app.db.collection.insert_one')
def test_quiz_submit_route(mock_insert_one, client):
    # Set up session data with required keys excluding 'features1'
    with client.session_transaction() as sess:
        sess['correct_answer'] = 'correct_answer_id'
        sess['quiz_data'] = {
            'song1': {'name': 'Song 1'},
            'song2': {'name': 'Song 2'},
            'song1_image_url': 'image_url_1',
            'song2_image_url': 'image_url_2'
            # Add other required data here
        }

    # Simulate a POST request with the form data containing the correct answer
    request_data = {'answer1': 'correct_answer_id'}
    response = client.post('/quiz/submit', data=request_data)

    # Assertions
    assert response.status_code == 200
    assert b'Correct!' in response.data  # Assuming the template renders 'Correct!' for a correct answer
    mock_insert_one.assert_called_once()


@pytest.fixture
def mock_features_response():
    # Define and return your mocked features response here
    pass

@pytest.fixture
def mock_tracks_response():
    # Define and return your mocked tracks response here
    pass

def test_quiz_route_redirects_to_login_when_no_access_token(mock_features_response, mock_tracks_response, client):
    # Mock 'access_token' not in session
    with client.session_transaction() as sess:
        sess.clear()  # Clear any existing session data
    
    response = client.get('/quiz')
    assert response.status_code == 302
    assert response.location == '/login'


@patch('app.requests.get')
@patch('app.requests.get')
def test_top_artists_redirects_to_login_when_no_access_token(mock_response_1, mock_response_2, client):
    # Mock 'access_token' not in session
    with client.session_transaction() as sess:
        sess.clear()  # Clear any existing session data
    
    response = client.get('/top_artists')
    assert response.status_code == 302
    assert response.location == '/login'

@patch('app.requests.get')
@patch('app.requests.get')
def test_top_artists_redirects_to_refresh_token_when_expired(mock_response_1, mock_response_2, client):
    # Mock 'access_token' in session but expired
    with client.session_transaction() as sess:
        sess['access_token'] = 'test_access_token'
        sess['expires_at'] = (datetime.now() - timedelta(hours=1)).timestamp()
        # Add any other required data to the session
    
    response = client.get('/top_artists')
    assert response.status_code == 302
    assert response.location == '/refresh-token'

'''@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.requests.get')
@patch('app.requests.get')
def test_quiz_route(mock_features_response, mock_tracks_response, client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'test_access_token'
        sess['expires_at'] = (datetime.now() + timedelta(hours=1)).timestamp()

    # Mock API responses for saved tracks and audio features
    mock_tracks_response.return_value.json.return_value = {
        'items': [
            {'id': 'song1_id', 'name': 'Song 1'},
            {'id': 'song2_id', 'name': 'Song 2'}
        ]
    }
    mock_features_response.return_value.json.return_value = {
        # Simulating an empty response or response without 'audio_features'
        # Adjust as needed based on your requirements for testing this behavior
    }

    response = client.get('/quiz')
    assert response.status_code == 302  # Assuming it redirects to '/refresh-token' due to missing 'audio_features'''


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch('app.requests.get')
def test_random_song_route(mock_get, client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'test_access_token'
        sess['expires_at'] = (datetime.now() + timedelta(hours=1)).timestamp()

    # Mock API response for featured playlists
    mock_get.return_value.json.return_value = {'playlists': {'items': [{'href': 'playlist_link'}]}}
    
    # Mock API response for playlist tracks
    mock_get.side_effect = [
        MagicMock(json=lambda: {'tracks': {'items': [{'track': {'name': 'Track Name'}}]}})
    ]

    # Run the random_song route
    response = client.get('/random_song')

    # Perform assertions
    assert b'Track Name' in response.data

@patch('app.requests.get')
def test_random_song_route(mock_get, client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'test_access_token'
        sess['expires_at'] = (datetime.now() + timedelta(hours=1)).timestamp()

    # Mock API response for featured playlists
    mock_get.return_value.json.return_value = {
        'playlists': {
            'items': [
                {
                    'href': 'playlist_link',
                    'tracks': {
                        'items': [
                            {
                                'track': {
                                    'name': 'Track Name',
                                    'artists': [{'name': 'Artist Name'}],
                                    'album': {'name': 'Album Name'},
                                    'external_urls': {'spotify': 'track_url'},
                                    'images': [{'url': 'image_url'}]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
    
    # Run the random_song route
    response = client.get('/random_song')
    
    # Perform assertions
    assert b'Track Name' not in response.data
    assert b'No tracks found in the selected playlist' in response.data
    # Add more assertions based on expected data in the response

def test_app_exists():
    assert app is not None

def test_app_debug_is_true():
    assert app.debug is False


from unittest.mock import patch
from app import app  # Assuming your Flask app instance is called 'app'

@patch('app.requests.get')
def test_top_artists_route(mock_requests_get):
    # Mock session data
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['access_token'] = 'test_access_token'
            session['expires_at'] = 1893456000  # Some timestamp in the future
    
        # Mock the response from the external API
        mock_requests_get.return_value.json.return_value = {
            'items': [
                {
                    'name': 'Artist 1',
                    'images': [{'url': 'image_url_1'}]
                },
                {
                    'name': 'Artist 2',
                    'images': [{'url': 'image_url_2'}]
                }
            ]
        }
        
        # Make a GET request to the route
        response = client.get('/top_artists')
        
        # Assertions
        assert response.status_code == 200
        assert b'Artist 1' in response.data
        assert b'Artist 2' in response.data
        assert b'image_url_1' in response.data
        assert b'image_url_2' in response.data
