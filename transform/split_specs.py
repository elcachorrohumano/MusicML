import h5py
import pandas as pd
import numpy as np

# Load IDs from the CSV files
train_ids = pd.read_csv('/Users/elcachorrohumano/workspace/MusicNN/data/train/train.csv')['id'].astype(str).tolist()
test_ids = pd.read_csv('/Users/elcachorrohumano/workspace/MusicNN/data/test/test.csv')['id'].astype(str).tolist()
validation_ids = pd.read_csv('/Users/elcachorrohumano/workspace/MusicNN/data/validation/validation.csv')['id'].astype(str).tolist()

# Load spectrogram data from the HDF5 file
with h5py.File('/Users/elcachorrohumano/workspace/MusicNN/data/spectrograms.h5', 'r') as f:
    spectrograms = f['spectrograms'][:]
    labels = f['labels'][:]
    song_names = f['song_names'][:]
    song_ids = f['song_ids'][:].astype(str)  # Convert song_ids to string for matching

# Create Boolean masks for train, test, and validation sets
train_mask = np.isin(song_ids, train_ids)
test_mask = np.isin(song_ids, test_ids)
validation_mask = np.isin(song_ids, validation_ids)

# Convert song_ids to np.string_ type for HDF5 compatibility
song_ids_str_train = np.array(song_ids[train_mask], dtype=np.string_)
song_ids_str_test = np.array(song_ids[test_mask], dtype=np.string_)
song_ids_str_validation = np.array(song_ids[validation_mask], dtype=np.string_)

# Write train data to spec_train.h5
with h5py.File('/Users/elcachorrohumano/workspace/MusicNN/data/train/spec_train.h5', 'w') as f_train:
    f_train.create_dataset('spectrograms', data=spectrograms[train_mask])
    f_train.create_dataset('labels', data=labels[train_mask])
    f_train.create_dataset('song_names', data=song_names[train_mask], dtype=h5py.string_dtype(encoding='utf-8'))
    f_train.create_dataset('song_ids', data=song_ids_str_train)  # Using np.string_ for compatibility

# Write test data to spec_test.h5
with h5py.File('/Users/elcachorrohumano/workspace/MusicNN/data/test/spec_test.h5', 'w') as f_test:
    f_test.create_dataset('spectrograms', data=spectrograms[test_mask])
    f_test.create_dataset('labels', data=labels[test_mask])
    f_test.create_dataset('song_names', data=song_names[test_mask], dtype=h5py.string_dtype(encoding='utf-8'))
    f_test.create_dataset('song_ids', data=song_ids_str_test)  # Using np.string_ for compatibility

# Write validation data to spec_validation.h5
with h5py.File('/Users/elcachorrohumano/workspace/MusicNN/data/validation/spec_validation.h5', 'w') as f_validation:
    f_validation.create_dataset('spectrograms', data=spectrograms[validation_mask])
    f_validation.create_dataset('labels', data=labels[validation_mask])
    f_validation.create_dataset('song_names', data=song_names[validation_mask], dtype=h5py.string_dtype(encoding='utf-8'))
    f_validation.create_dataset('song_ids', data=song_ids_str_validation)  # Using np.string_ for compatibility

print("Train, test, and validation HDF5 files created successfully.")
