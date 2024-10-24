import os
import requests
from spotify_secrets import e_secrets, l_secrets


# Function to get Spotify access token
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    return auth_response.json().get('access_token')

def get_playlist_data(token, playlist_id):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    params = {
        'limit': 100,
        'offset': 0
    }
    all_tracks = []
    while True:
        response = requests.get(playlist_url, headers=headers, params=params)
        
        # Print the raw response for debugging
        print(f"Status Code (get playlist data): {response.status_code}")
        
        # Check if the response was successful
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            return all_tracks  # Return an empty list if there's an error
        
        data = response.json()

        # Check if 'items' is in the response
        if 'items' not in data:
            print(f"Unexpected response format: {data}")
            return all_tracks  # Return an empty list if 'items' is missing

        # Extract only track name and preview URL
        for item in data['items']:
            track = item['track']
            if track is not None and track['preview_url']:  # Check if track is not None and has preview_url
                all_tracks.append({
                    'name': track['name'],
                    'preview_url': track['preview_url']
                })

        # Check if there's another page of results
        if data['next']:
            params['offset'] += params['limit']
        else:
            break
    return all_tracks

# Function to download the 30-second preview of a track
def download_preview(preview_url, track_name, folder_path):
    try:
        # Make the request to get the preview content
        response = requests.get(preview_url, stream=True)
        print(f"Status Code (download preview): {response.status_code}")

        # Check if the request was successful
        if response.status_code == 200:
            # Sanitize the track name to use it as a file name
            track_filename = f"{track_name}.mp3".replace('/', '_').replace('\\', '_').replace(':', '_')
            file_path = os.path.join(folder_path, track_filename)

            # Write the preview file to the specified folder
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # Only write if there's data
                        file.write(chunk)
            print(f"Downloaded: {track_filename}")
        else:
            print(f"Failed to download: {track_name}. HTTP Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {track_name}: {e}")

# Function to download all 30-second previews from a playlist
def download_playlist_previews(token, playlist_id, folder_path):
    # Ensure the folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Get all tracks from the playlist
    tracks = get_playlist_data(token, playlist_id)
    print(f"Total tracks in playlist: {len(tracks)}")
    # Print track name and preview URL before downloading
    for track in tracks:
        print(f"Track Name: {track['name']}")
        print(f"Preview URL: {track['preview_url']}")
        print(track['preview_url'])
        if track['preview_url']:
            print(f"Attempting to download preview for: {track['name']}")
            download_preview(track['preview_url'], track['name'], folder_path)
        else:
            print(f"No preview available for: {track['name']}")

            
if __name__ == '__main__':


    CLIENT_ID = l_secrets['CLIENT_ID']
    CLIENT_SECRET = l_secrets['CLIENT_SECRET']

    

    # Thor and Dr. Jones playlist ID
    # PLAYLIST_ID = '4wabAppNrWpfm7222qeNV9'
    # FOLDER_PATH = '1'

    # Raeggeton
    # PLAYLIST_ID = '66jbv6VIdTAyNuGNlHhWlj'
    # FOLDER_PATH = '0'

    # Electronica
    # PLAYLIST_ID = '39nFCFRtOYIRkfx0hggGHa'
    # FOLDER_PATH = '0'

    # Heavy metal
    # PLAYLIST_ID = '6bBDGRXuUB0yj6HOGdouLc'
    # FOLDER_PATH = '0'

    # K-pop
    # PLAYLIST_ID = '2EoheVFjqIxgJMb8VnDRtZ'
    # FOLDER_PATH = '0'

    # Top hits 2019 
    # PLAYLIST_ID = '37i9dQZF1DWVRSukIED0e9'
    # FOLDER_PATH = '0'

    #  Trap
    # PLAYLIST_ID = '2AvH6y4sXfpNDOes73jyyc'
    # FOLDER_PATH = '0'

    # Corridos
    # PLAYLIST_ID = '4HMZyD1pQ6MV3ZBkn9Z0RE'
    # FOLDER_PATH = '0'

    # Pop en ingles
    # PLAYLIST_ID = '37i9dQZF1DX2oVzuo0LbVg'
    # FOLDER_PATH = '0'

    # Electronica y dance
    # PLAYLIST_ID = '37i9dQZF1DXdDh4h59PJIQ'
    # FOLDER_PATH = '0'

    # Country
    # PLAYLIST_ID = '37i9dQZF1DWTkxQvqMy4WW'
    # FOLDER_PATH = '0'

    # Baladas
    # PLAYLIST_ID = '37i9dQZF1DX09mi3a4Zmox'
    # FOLDER_PATH = '0'

    # Rap
    # PLAYLIST_ID = '2NyfQnbUQtpgeVb5SKIYrn'
    # FOLDER_PATH = '0'

    # Viva latino
    # PLAYLIST_ID = '37i9dQZF1DX10zKzsJ2jva'
    # FOLDER_PATH = '0'

    # Locked in
    # PLAYLIST_ID = '37i9dQZF1DWTl4y3vgJOXW'
    # FOLDER_PATH = '0'

    # Mariachi
    # PLAYLIST_ID = '37i9dQZF1DXdC7eRcOJUCw'
    # FOLDER_PATH = '0'

    # 2000s pop
    # PLAYLIST_ID = '2Sxd5BovYwLgRg6KyZOTer'
    # FOLDER_PATH = '0'

    # Mirrey
    # PLAYLIST_ID = '3OR6iGU8coLhDlVsydFqO5'
    # FOLDER_PATH = '0'
    


    # Get Spotify access token
    token = get_spotify_token(CLIENT_ID, CLIENT_SECRET)

    # Download all 30-second previews from the playlist
    download_playlist_previews(token, PLAYLIST_ID, FOLDER_PATH)