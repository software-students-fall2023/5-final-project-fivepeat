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

def test_login_route(client):
    response = client.get('/login')
    assert response.status_code == 302  

def test_top_artists_route_unauthorized(client):
    response = client.get('/top_artists')
    assert response.status_code == 302
    assert b'/login' in response.data  

def test_top_artists_route_authorized(client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'valid_token_here'
        sess['expires_at'] = 9999999999  

    response = client.get('/top_artists')
    assert response.status_code == 200

def test_callback_error_handling(client):
    response = client.get('/callback?error=some_error')
    assert response.status_code == 200  

def test_refresh_token_route_unauthorized(client):
    response = client.get('/refresh-token')
    assert response.status_code == 302
    assert b'/login' in response.data  

def test_quiz_route_unauthorized(client):
    response = client.get('/quiz')
    assert response.status_code == 302
    assert b'/login' in response.data 

def test_random_song_route_unauthorized(client):
    response = client.get('/random_song')
    assert response.status_code == 302
    assert b'/login' in response.data 

def test_random_song_route_authorized(client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'valid_token_here'
        sess['expires_at'] = 9999999999  

    response = client.get('/random_song')
    assert response.status_code == 200

def test_history_route_unauthorized(client):
    response = client.get('/history')
    assert response.status_code == 302
    assert b'/login' in response.data  

'''def test_history_route_authorized(client):
    with client.session_transaction() as sess:
        sess['access_token'] = 'valid_token_here'
        sess['expires_at'] = 9999999999  

    response = client.get('/history')
    assert response.status_code == 200'''

def test_quiz_route_redirects_when_access_token_not_in_session(client, monkeypatch):

    with client.session_transaction() as sess:
        sess.clear()  
        
    response = client.get('/quiz')
    assert response.status_code == 302
    assert response.location == '/login'  

def test_quiz_route_redirects_when_token_expired(client, monkeypatch):
    
    with client.session_transaction() as sess:
        sess['access_token'] = 'valid_access_token_here'
        sess['expires_at'] = 1000  
        
    response = client.get('/quiz')
    assert response.status_code == 302
    assert response.location == '/refresh-token'  

def test_random_song_redirects_to_login_when_no_access_token(client):
    with client.session_transaction() as sess:
        sess.pop('access_token', None)

    response = client.get('/random_song')
    assert response.status_code == 302
    assert response.location == '/login'  

def test_random_song_redirects_to_refresh_token_when_token_expired(client):
    with client.session_transaction() as sess:
        sess['expires_at'] = datetime.now() - timedelta(hours=1)

    response = client.get('/random_song')
    assert response.status_code == 302
    assert response.location == '/login' 

def test_callback_with_error_in_request_args(client):
    
    response = client.get('/callback?error=test_error')
    assert response.status_code == 200
    assert response.json == {"error": "test_error"}

@patch('app.requests.post')
def test_callback_with_code_in_request_args(mock_post, client):
    
    mock_response = mock_post.return_value
    mock_response.json.return_value = {
        'access_token': 'test_access_token',
        'refresh_token': 'test_refresh_token',
        'expires_in': 3600  
    }

    response = client.get('/callback?code=test_code')
    assert response.status_code == 302
    assert session['access_token'] == 'test_access_token'
    assert session['refresh_token'] == 'test_refresh_token'
    assert 'expires_at' in session

    expected_expires_at = datetime.now().timestamp() + 3600  
    assert abs(session['expires_at'] - expected_expires_at) < 1  

    assert response.location == '/top_artists'

@patch('app.requests.post')
def test_refresh_token_route(mock_post, client):
    
    with client.session_transaction() as sess:
        sess['refresh_token'] = 'valid_refresh_token_here'
        sess['expires_at'] = datetime.now().timestamp() + 3600  

    mock_response = mock_post.return_value
    mock_response.json.return_value = {
        'access_token': 'new_access_token',
        'expires_in': 3600  
    }

    response = client.get('/refresh-token')

    assert response.status_code == 302
    assert session['access_token'] == 'new_access_token'
    assert 'expires_at' in session

    expected_expires_at = datetime.now().timestamp() + 3600  
    assert abs(session['expires_at'] - expected_expires_at) < 1  

    assert response.location == '/top_artists'

@patch('app.db.collection.insert_one')
def test_quiz_submit_route(mock_insert_one, client):
    
    with client.session_transaction() as sess:
        sess['correct_answer'] = 'correct_answer_id'
        sess['quiz_data'] = {
            'song1': {'name': 'Song 1', 'features1': 'Feature 1'},
            'song2': {'name': 'Song 2', 'features2': 'Feature 2'},
            'song1_image_url': 'image_url_1',
            'song2_image_url': 'image_url_2'
        }

    response = client.post('/quiz/submit', data={'answer1': 'correct_answer_id'})

    assert response.status_code == 200
    assert b'Correct!' in response.data  #

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
    
    with client.session_transaction() as sess:
        sess['correct_answer'] = 'correct_answer_id'
        sess['quiz_data'] = {
            'song1': {'name': 'Song 1'},
            'song2': {'name': 'Song 2'},
            'song1_image_url': 'image_url_1',
            'song2_image_url': 'image_url_2'
        }

    request_data = {'answer1': 'correct_answer_id'}
    response = client.post('/quiz/submit', data=request_data)
   
    assert response.status_code == 200
    assert b'Correct!' in response.data  
    mock_insert_one.assert_called_once()

@pytest.fixture
def mock_features_response():
    pass

@pytest.fixture
def mock_tracks_response():
    pass

def test_quiz_route_redirects_to_login_when_no_access_token(mock_features_response, mock_tracks_response, client):
    
    with client.session_transaction() as sess:
        sess.clear()  
    
    response = client.get('/quiz')
    assert response.status_code == 302
    assert response.location == '/login'

@patch('app.requests.get')
@patch('app.requests.get')
def test_top_artists_redirects_to_login_when_no_access_token(mock_response_1, mock_response_2, client):
   
    with client.session_transaction() as sess:
        sess.clear()  
    
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
    
    response = client.get('/top_artists')
    assert response.status_code == 302
    assert response.location == '/refresh-token'

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

    response = client.get('/random_song')

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

def test_app_exists():
    assert app is not None

def test_app_debug_is_true():
    assert app.debug is False

@patch('app.requests.get')
def test_top_artists_route(mock_requests_get):
   
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['access_token'] = 'test_access_token'
            session['expires_at'] = 1893456000 
    
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
        
        response = client.get('/top_artists')
        
        assert response.status_code == 200
        assert b'Artist 1' in response.data
        assert b'Artist 2' in response.data
        assert b'image_url_1' in response.data
        assert b'image_url_2' in response.data
