import os
import requests
import pandas as pd
import time
from spotify_secrets import e_secrets, l_secrets, v_secrets

# Path to the CSV file
csv_file = '/Users/elcachorrohumano/workspace/MusicNN/data/tracks_audio_features.csv'

# Spotify API endpoint to fetch track details
SPOTIFY_TRACK_ENDPOINT = "https://api.spotify.com/v1/tracks"

# Function to get a Spotify token
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    if auth_response.status_code == 200:
        return auth_response.json().get('access_token')
    else:
        raise Exception(f"Failed to get token: {auth_response.status_code}, {auth_response.text}")

# Set up credentials rotation list
credentials = [l_secrets, e_secrets, v_secrets]
current_credentials_index = 0

# Function to rotate credentials
def rotate_credentials():
    global current_credentials_index
    current_credentials_index = (current_credentials_index + 1) % len(credentials)
    return credentials[current_credentials_index]

# Initialize the first token
current_secrets = credentials[current_credentials_index]
access_token = get_spotify_token(current_secrets['CLIENT_ID'], current_secrets['CLIENT_SECRET'])

# Function to update headers with the current access token
def update_headers(access_token):
    return {'Authorization': f'Bearer {access_token}'}

# Initialize headers
headers = update_headers(access_token)

# Function to get track details from Spotify API
def get_track_names(track_ids, retries=5, timeout=10):
    global headers
    track_names = []
    
    for idx, track_id in enumerate(track_ids, start=1):
        url = f"{SPOTIFY_TRACK_ENDPOINT}/{track_id}"
        retry_count = retries

        while retry_count > 0:
            try:
                response = requests.get(url, headers=headers, timeout=timeout)

                if response.status_code == 200:
                    track_info = response.json()
                    track_names.append(track_info['name'])  # Extract the track name
                    break

                elif response.status_code == 401:  # Invalid or expired token
                    print("Token expired or invalid. Rotating credentials...")
                    current_secrets = rotate_credentials()
                    access_token = get_spotify_token(current_secrets['CLIENT_ID'], current_secrets['CLIENT_SECRET'])
                    headers = update_headers(access_token)

                elif response.status_code == 429:  # Rate limit exceeded
                    retry_after = int(response.headers.get('Retry-After', 30))
                    print(f"Rate limit exceeded. Waiting {retry_after} seconds before retrying...")
                    time.sleep(retry_after)

                else:
                    print(f"Error fetching track name for {track_id}: {response.status_code}")
                    track_names.append(None)  # In case of an error, append None
                    break

            except (requests.ConnectTimeout, requests.ReadTimeout, requests.ConnectionError) as e:
                if retry_count > 0:
                    wait_time = 2 ** (5 - retry_count)  # Exponential backoff
                    print(f"Connection error: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    retry_count -= 1
                else:
                    print(f"Failed to retrieve track name for {track_id} after several attempts.")
                    track_names.append(None)
                    break
        
        # Progress log for every 100 tracks
        if idx % 100 == 0:
            print(f"Processed {idx}/{len(track_ids)} tracks so far...")

    return track_names


# Load the CSV file
df = pd.read_csv(csv_file)

# Check if 'id' column exists in the CSV
if 'id' not in df.columns:
    raise ValueError("'id' column not found in the CSV file.")

# Fetch track names using the 'id' column (Spotify track IDs)
track_ids = df['id'].tolist()
print(f"Fetching track names for {len(track_ids)} tracks...")

# Call the function to fetch track names
track_names = get_track_names(track_ids)

# Add the track names to the dataframe
df['track_name'] = track_names

# Save the updated CSV
updated_csv_file = '/Users/elcachorrohumano/workspace/MusicNN/data/tracks_audio_features_with_names.csv'
df.to_csv(updated_csv_file, index=False)

print(f"Track names added to CSV and saved to {updated_csv_file}")
