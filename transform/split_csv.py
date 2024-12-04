import pandas as pd
from sklearn.model_selection import train_test_split

def split_csv(data_file, output_file_train, output_file_val, output_file_test, split_ratio):
    """
    Splits a CSV file into train, validation, and test sets, ensuring the same distribution of the target variable.
    
    Parameters:
        data_file (str): Path to the input CSV file.
        output_file_train (str): Path to save the training set CSV.
        output_file_val (str): Path to save the validation set CSV.
        output_file_test (str): Path to save the test set CSV.
        split_ratio (tuple): Tuple of floats representing the split ratio (train, val, test).
                             For example, (0.6, 0.2, 0.2) for 60% train, 20% val, and 20% test.
    """
    # Load the data
    data = pd.read_csv(data_file)
    
    if 'like' not in data.columns:
        raise ValueError("The target variable 'like' is not found in the dataset.")
    
    # Ensure the split ratios sum to 1
    if not round(sum(split_ratio), 2) == 1.0:
        raise ValueError("The split ratios must sum to 1.")
    
    # Split into train and temp (val + test)
    train_ratio = split_ratio[0]
    temp_ratio = split_ratio[1] + split_ratio[2]
    val_ratio = split_ratio[1] / temp_ratio
    test_ratio = split_ratio[2] / temp_ratio

    train_data, temp_data = train_test_split(data, test_size=temp_ratio, stratify=data['like'], random_state=42)
    val_data, test_data = train_test_split(temp_data, test_size=test_ratio, stratify=temp_data['like'], random_state=42)
    
    # Save the splits
    train_data.to_csv(output_file_train, index=False)
    val_data.to_csv(output_file_val, index=False)
    test_data.to_csv(output_file_test, index=False)
    
    print(f"Data split completed:")
    print(f"  Train set saved to {output_file_train} with {len(train_data)} samples")
    print(f"  Validation set saved to {output_file_val} with {len(val_data)} samples")
    print(f"  Test set saved to {output_file_test} with {len(test_data)} samples")

data_file = '/Users/elcachorrohumano/workspace/MusicNN/data/tracks_audio_features_with_names.csv'
output_file_train = '/Users/elcachorrohumano/workspace/MusicNN/data/train/train.csv'
output_file_val = '/Users/elcachorrohumano/workspace/MusicNN/data/validation/validation.csv'
output_file_test = '/Users/elcachorrohumano/workspace/MusicNN/data/test/test.csv'
split_ratio= (0.7, 0.2, 0.1)

split_csv(data_file, output_file_train, output_file_val, output_file_test, split_ratio)

