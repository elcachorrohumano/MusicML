import os
import librosa
import numpy as np
import h5py
import pandas as pd

# Paths
data_dir = '/Users/elcachorrohumano/workspace/MusicNN/data/audio_samples'
output_file = '/Users/elcachorrohumano/workspace/MusicNN/data/spectrograms.h5'
csv_file = '/Users/elcachorrohumano/workspace/MusicNN/data/tracks_audio_features_with_names.csv'

# Load the CSV file with song IDs and track names
df = pd.read_csv(csv_file)

# Initialize lists to store spectrograms, labels, song names, and IDs
spectrograms = []
labels = []
song_names = []
song_ids = []
spectrogram_lengths = []

# Function to create a spectrogram from an MP3 file
def get_spectrogram(file_path, n_mels=128):
    y, sr = librosa.load(file_path)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
    S_db = librosa.power_to_db(S, ref=np.max)
    return S_db

# Iterate through each folder ('0' and '1') to find the minimum spectrogram length
for label in ['0', '1']:
    folder_path = os.path.join(data_dir, label)
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mp3'):
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing {file_path}")
            spectrogram = get_spectrogram(file_path)
            
            # Store the spectrogram length
            spectrogram_lengths.append(spectrogram.shape[1])

# Find the minimum length of the spectrograms
min_length = min(spectrogram_lengths)

# Iterate again to truncate spectrograms and store them along with names and IDs
for label in ['0', '1']:
    folder_path = os.path.join(data_dir, label)
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mp3'):
            file_path = os.path.join(folder_path, file_name)
            spectrogram = get_spectrogram(file_path)
            
            # Truncate the spectrogram to the minimum length
            truncated_spectrogram = spectrogram[:, :min_length]
            
            # Extract the song ID from the filename (assuming filename is the ID)
            song_id = os.path.splitext(file_name)[0]
            
            # Look up the corresponding track name from the CSV using the song ID
            row = df[df['id'] == song_id]
            if not row.empty:
                song_name = row['track_name'].values[0]
            else:
                song_name = ''  # Use empty string if no match found
                print(f"Song ID '{song_id}' not found in the CSV.")
            
            # Store the truncated spectrogram, label, song name, and ID
            spectrograms.append(truncated_spectrogram)
            labels.append(int(label))
            song_names.append(song_name)
            song_ids.append(song_id)  # Ensure song_id is stored as is

# Convert to numpy arrays
spectrograms = np.array(spectrograms)
labels = np.array(labels)

song_names = [str(name) for name in song_names]

# Save to HDF5 file, using UTF-8 encoding for song names and IDs
with h5py.File(output_file, 'w') as f:
    f.create_dataset('spectrograms', data=spectrograms)
    f.create_dataset('labels', data=labels)
    # Use h5py's special string type for UTF-8 support
    dt = h5py.string_dtype(encoding='utf-8')
    f.create_dataset('song_names', data=song_names, dtype=dt)
    f.create_dataset('song_ids', data=song_ids, dtype=dt)

print(f"Spectrograms, labels, song names, and IDs saved to {output_file}")
