import requests
import pandas as pd
import time
from requests.exceptions import ConnectTimeout, ReadTimeout, ConnectionError
from spotify_secrets import e_secrets, l_secrets, v_secrets


import requests
import pandas as pd
import time
from requests.exceptions import ConnectTimeout, ReadTimeout, ConnectionError
from spotify_secrets import e_secrets, l_secrets, v_secrets

# Function to retrieve all tracks from a playlist, handling pagination with retries and timeout
def get_all_playlist_tracks(playlist_id, retries=5, timeout=10):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=100"
    tracks = []
    
    while url:
        time.sleep(30)
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                tracks.extend(data['items'])  # Add the current batch of tracks to the list
                url = data['next']  # Get the next URL for pagination
                print(f"Fetched {len(tracks)} tracks so far from playlist {playlist_id}")
            else:
                print(f"Error fetching playlist {playlist_id}: {response.status_code}")
                break
        except (ConnectTimeout, ReadTimeout, ConnectionError) as e:
            if retries > 0:
                wait_time = 2 ** (5 - retries)  # Exponential backoff
                print(f"Error: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                return get_all_playlist_tracks(playlist_id, retries=retries-1)
            else:
                print(f"Failed to retrieve playlist {playlist_id} after several attempts.")
                break
    print(f'{playlist_id}: {len(tracks)} total tracks fetched.')
    return tracks


def get_audio_features_batch(track_ids, retries=5, timeout=10):
    url = f"https://api.spotify.com/v1/audio-features"
    params = {'ids': ','.join(track_ids)}  # Join up to 100 track IDs

    while retries > 0:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            
            if response.status_code == 200:
                return response.json()['audio_features']  # Return the batch of audio features

            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 30))  # Fallback to 30 seconds if not specified
                print(f"Rate limit exceeded. Waiting {retry_after} seconds before retrying...")
                time.sleep(retry_after)
            
            else:
                print(f"Error fetching audio features for batch: {response.status_code}")
                return None

        except (ConnectTimeout, ReadTimeout, ConnectionError) as e:
            if retries > 0:
                wait_time = 2 ** (5 - retries)  # Exponential backoff
                print(f"Connection error: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries -= 1
            else:
                print(f"Failed to retrieve audio features after several attempts.")
                return None
    
    return None  # If all retries failed


# Initialize data list
data = []

# Iterate through playlist IDs in the dictionary
for key, playlist_ids in ids.items():
    for playlist_id in playlist_ids:
        playlist_tracks = get_all_playlist_tracks(playlist_id)
        if playlist_tracks:
            track_ids_batch = []
            for item in playlist_tracks:
                track = item['track']
                if track:  # Ensure track is not None
                    track_id = track['id']
                    if track_id:
                        track_ids_batch.append(track_id)
                
                # If batch size reaches 100, fetch audio features for the batch
                if len(track_ids_batch) == 100:
                    time.sleep(30)
                    audio_features = get_audio_features_batch(track_ids_batch)
                    if audio_features:
                        for features in audio_features:
                            if features:
                                track_info = {
                                    'track_id': features['id'],
                                    'track_name': track['name'],
                                    'artist': track['artists'][0]['name'],
                                    'acousticness': features['acousticness'],
                                    'danceability': features['danceability'],
                                    'energy': features['energy'],
                                    'instrumentalness': features['instrumentalness'],
                                    'key': features['key'],
                                    'liveness': features['liveness'],
                                    'loudness': features['loudness'],
                                    'speechiness': features['speechiness'],
                                    'tempo': features['tempo'],
                                    'valence': features['valence'],
                                    'duration_ms': features['duration_ms'],
                                    'time_signature': features['time_signature'],
                                    'playlist_type': key
                                }
                                data.append(track_info)
                    track_ids_batch = []  # Clear batch after processing

            # Process any remaining track IDs in the final batch
            if track_ids_batch:
                audio_features = get_audio_features_batch(track_ids_batch)
                if audio_features:
                    for features in audio_features:
                        if features:
                            track_info = {
                                'track_id': features['id'],
                                'track_name': track['name'],
                                'artist': track['artists'][0]['name'],
                                'acousticness': features['acousticness'],
                                'danceability': features['danceability'],
                                'energy': features['energy'],
                                'instrumentalness': features['instrumentalness'],
                                'key': features['key'],
                                'liveness': features['liveness'],
                                'loudness': features['loudness'],
                                'speechiness': features['speechiness'],
                                'tempo': features['tempo'],
                                'valence': features['valence'],
                                'duration_ms': features['duration_ms'],
                                'time_signature': features['time_signature'],
                                'playlist_type': key
                            }
                            data.append(track_info)

# Create a DataFrame from the collected data
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('data/tracks_audio_features.csv', index=False)
