import pandas as pd

# Load the two CSV files into DataFrames
file1 = '/Users/elcachorrohumano/workspace/MusicNN/data/tracks_audio_features.csv'
file2 = '/Users/elcachorrohumano/workspace/MusicNN/data/tracks_audio_features_with_names.csv'

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

# Assuming the track names or IDs are in a column named 'id' (adjust if different)
df1_tracks_0 = df1[df1['like'] == 0]['id']
df1_tracks_1 = df1[df1['like'] == 1]['id']

df2_tracks_0 = df2[df2['like'] == 0]['id']
df2_tracks_1 = df2[df2['like'] == 1]['id']

# Find common tracks between 0 and 1 categories in both files
repeated_tracks_file1 = set(df1_tracks_0).intersection(set(df1_tracks_1))
repeated_tracks_file2 = set(df2_tracks_0).intersection(set(df2_tracks_1))

# Assuming there are 5 repeated tracks, we'll combine them into one set
repeated_tracks = repeated_tracks_file1.union(repeated_tracks_file2)

# Update the 'like' column to 1 for the repeated tracks in both DataFrames
df1.loc[df1['id'].isin(repeated_tracks), 'like'] = 1
df2.loc[df2['id'].isin(repeated_tracks), 'like'] = 1

df1_columns = ['id', 'danceability','energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature', 'like']
df2_columns = ['id', 'track_name', 'danceability','energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature', 'like']

df1 = df1[df1_columns]
df2 = df2[df2_columns]

# Save the modified DataFrames back to CSV files
df1.to_csv(file1, index=False)
df2.to_csv(file2, index=False)

df1.drop_duplicates(subset='id', keep='first', inplace=True)
df2.drop_duplicates(subset='id', keep='first', inplace=True)

print(f"Updated 'like' column to 1 for {len(repeated_tracks)} repeated tracks in both files.")

"""
Repeated tracks ids:
2SiXAy7TuUkycRVbbWDEpo
5CQ30WqJwcep0pYcV4AMNc
1f2V8U1BiWaC9aJWmpOARe
1RKUoGiLEbcXN4GY4spQDx
6hFHsQWB7HdVrSe7efRR82
19ScoKGqnfUggyqOVQjsoH

Links:
https://open.spotify.com/track/2SiXAy7TuUkycRVbbWDEpo?si=9e1995cef7414f3f
https://open.spotify.com/track/5CQ30WqJwcep0pYcV4AMNc?si=9e1995cef7414f3f
https://open.spotify.com/track/1f2V8U1BiWaC9aJWmpOARe?si=9e1995cef7414f3f
https://open.spotify.com/track/1RKUoGiLEbcXN4GY4spQDx?si=9e1995cef7414f3f
https://open.spotify.com/track/6hFHsQWB7HdVrSe7efRR82?si=9e1995cef7414f3f
https://open.spotify.com/track/19ScoKGqnfUggyqOVQjsoH?si=9e1995cef7414f3f

Names:
You shook me all night long
Stairway to heaven
By the Way
Clint Eastwood
Como te extraño mi amor
La ingrata
"""
