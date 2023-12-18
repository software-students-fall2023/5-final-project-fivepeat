import requests
from flask import Flask, redirect, request, jsonify, session, render_template
from datetime import datetime
import urllib.parse
import random
import db

app = Flask(__name__)
app.secret_key = 'a1w12lje-df2jgd45kjg-s2fs3d8'

CLIENT_ID = 'ebd35c5b8a8644bc9eb08657951956ac'
CLIENT_SECRET = '9a0a789fc56b4a9fa43c66a093dfdd84'
REDIRECT_URI = 'http://localhost:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@app.route('/')
def index():
    return render_template('welcome.html')
     
@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-top-read user-library-read' 
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        return redirect('/top_artists')
    
@app.route('/top_artists')
def top_artists():
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    user_info = requests.get(API_BASE_URL + 'me', headers=headers)
    display_name = user_info.json().get('display_name')
    response = requests.get(API_BASE_URL + 'me/top/artists?limit=3', headers=headers)
    artists_data = response.json().get('items', [])
    if artists_data:
        artists_info = []
        for artist in artists_data:
            artist_info = {
                'name': artist.get('name', 'Unknown Artist'),
                'image_url': artist['images'][0]['url'] if artist.get('images') else None
            }
            artists_info.append(artist_info)

        return render_template('top_artists.html', display_name=display_name, artists=artists_info)
    else:
        return "empty response"
  

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
    response = requests.post(TOKEN_URL, data=req_body)
    new_token_info = response.json()
    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
    return redirect('/top_artists')

@app.route('/quiz')
def quiz():
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    saved_tracks_response = requests.get(API_BASE_URL + 'me/top/tracks?limit=100', headers=headers)
    saved_tracks = saved_tracks_response.json()['items']
    selected_tracks = random.sample(saved_tracks, 2)

    track_ids = ','.join([track['id'] for track in selected_tracks])
    features_response = requests.get(API_BASE_URL + f'audio-features?ids={track_ids}', headers=headers)
    audio_features = features_response.json()['audio_features']

    song1, song2 = selected_tracks
    if random.choice([True, False]):
        features1 = [feature for feature in audio_features if feature['id'] == song1['id']][0]
        features2 = [feature for feature in audio_features if feature['id'] == song2['id']][0]
        session['correct_answer'] = song1['id']
    else:
        features1 = [feature for feature in audio_features if feature['id'] == song2['id']][0]
        features2 = [feature for feature in audio_features if feature['id'] == song1['id']][0]
        session['correct_answer'] = song2['id']
    
    session['quiz_data'] = {
        'song1': song1,
        'song2': song2,
        'features1': features1,
        'features2': features2
    }

    return render_template('quiz.html', song1_name=song1, song2_name=song2, features1=features1, features2=features2)

@app.route('/quiz/submit', methods=['POST'])
def quiz_submit():
    submitted_answer = request.form['answer1']
    correct_answer = session.get('correct_answer')
    quiz_data = session.get('quiz_data', {})
    
    if submitted_answer == correct_answer:
        result = "Correct!"
    else:
        result = "Incorrect!"
    
    """Saves quiz into the MongoDB database"""
    data = {
        "Song 1 Name": quiz_data['song1']['name'],
        "Song 1 Features": quiz_data['features1'],
        "Song 2 Name": quiz_data['song2']['name'],
        "Song 2 Features": quiz_data['features2'],
        "Result": result
    }

    db.collection.insert_one(data)

    return render_template('quiz_result.html', result=result)

@app.route('/random_song')
def random_song():
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(API_BASE_URL + 'browse/featured-playlists', headers=headers)
    featured_playlists_data = response.json().get('playlists', {}).get('items', [])
    if featured_playlists_data:
        selected_playlist = random.choice(featured_playlists_data)
        playlist_endpoint = selected_playlist['href']
        playlist_response = requests.get(playlist_endpoint, headers=headers)
        playlist_data = playlist_response.json()

        tracks_data = playlist_data.get('tracks', {}).get('items', [])
        if tracks_data:
            random_track = random.choice(tracks_data)['track']
            track_info = {
                'name': random_track.get('name', 'Unknown Track'),
                'artists': [artist['name'] for artist in random_track.get('artists', [])],
                'album': random_track.get('album', {}).get('name', 'Unknown Album'),
                'image_url': random_track.get('album', {}).get('images', [])[0]['url'] if random_track.get('album') else None,
                'external_url': random_track.get('external_urls', {}).get('spotify', '')
            }

            return render_template('song_gen.html', track_info=track_info)
        else:
            return jsonify({"message": "No tracks found in the selected playlist"})
    else:
        return jsonify({"message": "No featured playlists available"})

@app.route('/history')
def history():
    if 'access_token' not in session:
        return redirect('/login')
    quiz_history = db.collection.find()
    return render_template('history.html', quiz_history=quiz_history)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)