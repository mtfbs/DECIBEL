# for this to work you need to have the SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables set.

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os


def search_song(song_title):
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    results = spotify.search(q='track:' + song_title, type='track')

    tracks_dict = []

    for i in range(0, len(results['tracks']['items'])):
        if results['tracks']['items'][0]['type'] == 'track':
            song_title = results['tracks']['items'][i]['name']
            artist_name = results['tracks']['items'][i]['artists'][0]['name']
            song_id = results['tracks']['items'][i]['id']

            tracks_dict.append({'song_title': song_title, 'artist_name': artist_name, 'song_id': song_id})

    return tracks_dict
