import os
import requests
import pandas as pd
from itertools import cycle
from spotify_secrets import e_secrets, l_secrets, v_secrets

# Function to get Spotify access token
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    if auth_response.status_code != 200:
        print(f"Error getting token: {auth_response.status_code} - {auth_response.text}")
        return None
    return auth_response.json().get('access_token')

# Function to get track preview URL from Spotify by track ID
def get_track_preview(token, track_id):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    track_url = f'https://api.spotify.com/v1/tracks/{track_id}'
    response = requests.get(track_url, headers=headers)

    if response.status_code == 200:
        track_data = response.json()
        return track_data.get('preview_url', None)
    else:
        print(f"Failed to fetch track {track_id}: {response.status_code} - {response.text}")
        return None

# Function to download the 30-second preview of a track
def download_preview(preview_url, track_id, folder_path):
    try:
        response = requests.get(preview_url, stream=True)
        if response.status_code == 200:
            # Save the file as 'id.mp3'
            track_filename = f"{track_id}.mp3"
            file_path = os.path.join(folder_path, track_filename)

            # Write the preview file to the specified folder
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            print(f"Downloaded: {track_filename} to {folder_path}")
        else:
            print(f"Failed to download: {track_id}. HTTP Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {track_id}: {e}")

# Rotate through secrets to avoid request blocks
def rotate_credentials():
    credentials = [
        (e_secrets['CLIENT_ID'], e_secrets['CLIENT_SECRET']),
        (l_secrets['CLIENT_ID'], l_secrets['CLIENT_SECRET']),
        (v_secrets['CLIENT_ID'], v_secrets['CLIENT_SECRET'])
    ]
    return cycle(credentials)

# Main function to process the CSV and download previews
def download_previews_from_csv(csv_file, folder_base_path):
    # Load the CSV file with track names, IDs, and labels
    df = pd.read_csv(csv_file)

    # Rotate credentials
    credentials_cycle = rotate_credentials()

    for index, row in df.iterrows():
        track_id = row['id']
        label = row['like']  # Assuming 'like' is the column indicating 0 or 1
        track_name = row['track_name']

        # Determine the folder path based on the label (0 or 1)
        folder_path = os.path.join(folder_base_path, str(label))
        
        # Ensure the folder exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Check if the file already exists
        track_filename = f"{track_id}.mp3"
        file_path = os.path.join(folder_path, track_filename)
        
        if os.path.exists(file_path):
            print(f"Already downloaded: {track_filename}")
            continue  # Skip this track if it's already downloaded

        # Rotate through credentials for each request
        client_id, client_secret = next(credentials_cycle)
        token = get_spotify_token(client_id, client_secret)

        if token:
            preview_url = get_track_preview(token, track_id)

            if preview_url:
                print(f"Downloading preview for: {track_name} ({track_id})")
                download_preview(preview_url, track_id, folder_path)
            else:
                print(f"No preview available for: {track_name} ({track_id})")
        else:
            print("Failed to get token. Skipping this track.")


# Example usage
if __name__ == "__main__":
    csv_file = '/Users/elcachorrohumano/workspace/MusicNN/data/tracks_audio_features_with_names.csv'
    folder_base_path = '/Users/elcachorrohumano/workspace/MusicNN/data/audio_samples'
    download_previews_from_csv(csv_file, folder_base_path)
