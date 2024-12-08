import os
import csv
import torch
from torch.utils.data import DataLoader, TensorDataset
import h5py
import torch.nn as nn

# File paths
model_path = '/Users/elcachorrohumano/workspace/MusicNN/ml/specs/fine_tuning/models/model_9.pth'
val_data_path = '/Users/elcachorrohumano/workspace/MusicNN/data/validation/spec_validation.h5'
output_csv_path = '/Users/elcachorrohumano/workspace/MusicNN/ml/ensemble/predictions_model_rnn.csv'

# Define batch size
batch_size = 64

# Load val data
def load_val_data(filepath):
    with h5py.File(filepath, 'r') as f:
        spectrograms = torch.tensor(f['spectrograms'][:], dtype=torch.float32).unsqueeze(1)
        labels = torch.tensor(f['labels'][:], dtype=torch.long)
        song_ids = f['song_ids'][:].astype(str)  # Ensure song IDs are strings
    return spectrograms, labels, song_ids

val_spectrograms, val_labels, val_song_ids = load_val_data(val_data_path)

# Create DataLoader for val data
val_dataset = TensorDataset(val_spectrograms, val_labels)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)


class ImprovedCNN(nn.Module):
    def __init__(self, input_height, input_width, num_classes, conv_channels=[32, 64, 128], fc_units=[512, 256], dropout_rate=0.25):
        super(ImprovedCNN, self).__init__()
        self.conv_layers = nn.ModuleList()
        in_channels = 1

        for out_channels in conv_channels:
            self.conv_layers.append(nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
                nn.BatchNorm2d(out_channels),
                nn.ReLU(),
                nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
                nn.BatchNorm2d(out_channels),
                nn.ReLU(),
                nn.MaxPool2d(2, 2),
                nn.Dropout2d(dropout_rate)
            ))
            in_channels = out_channels

        self.height_after_conv = input_height // (2 ** len(conv_channels))
        self.width_after_conv = input_width // (2 ** len(conv_channels))

        fc_layers = []
        in_features = conv_channels[-1] * self.height_after_conv * self.width_after_conv

        for units in fc_units:
            fc_layers.extend([
                nn.Linear(in_features, units),
                nn.ReLU(),
                nn.Dropout(dropout_rate),
            ])
            in_features = units

        fc_layers.append(nn.Linear(in_features, num_classes))
        self.fc = nn.Sequential(*fc_layers)

    def forward(self, x):
        for conv_layer in self.conv_layers:
            x = conv_layer(x)
        x = x.view(-1, x.size(1) * self.height_after_conv * self.width_after_conv)
        return self.fc(x)

num_classes = len(set(val_labels.numpy()))
_, channels, height, width = val_spectrograms.shape

# Define the device for PyTorch
device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
print("Using device:", device)

model = ImprovedCNN(height, width, num_classes,
                    conv_channels=[32, 64, 128],  # Adjust to saved model parameters
                    fc_units=[1024, 512],        # Match saved model fc_units
                    dropout_rate=0.25).to(device)
model.load_state_dict(torch.load(model_path, weights_only=True,map_location=device))
model.eval()

# Perform predictions and save to CSV
results = []

with torch.no_grad():
    for i, (inputs, labels) in enumerate(val_loader):
        inputs = inputs.to(device)
        labels = labels.to(device)

        outputs = model(inputs)
        probabilities = torch.softmax(outputs, dim=1)[:, 1].cpu().numpy()  # Probability of class 1
        predictions = torch.argmax(outputs, dim=1).cpu().numpy()  # Class predictions
        
        # Get song IDs for the current batch
        start_idx = i * batch_size
        end_idx = start_idx + len(labels)
        batch_song_ids = val_song_ids[start_idx:end_idx]
        
        # Collect results
        for song_id, prediction, label, probability in zip(batch_song_ids, predictions, labels.cpu().numpy(), probabilities):
            results.append((song_id, prediction, label, probability))

# Save results to CSV
with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['song_id', 'prediction', 'true_label', 'probability'])  # Updated header
    writer.writerows(results)

print(f"Predictions saved to {output_csv_path}")