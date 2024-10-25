import os
import torch
import pandas as pd
from collections import Counter
from PIL import Image

# Load YOLOv5 model (pre-trained on COCO dataset)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def parse_coordinates(filename):
    """Extracts coordinates from filename formatted as latitude_longitude.jpg."""
    base = os.path.basename(filename)
    name, ext = os.path.splitext(base)
    latitude, longitude = map(float, name.split('_'))
    return latitude, longitude

def analyze_image(image_path):
    """Analyzes an image to detect objects using YOLOv5."""
    try:
        # Load the image
        img = Image.open(image_path)
        results = model(img)  # Perform object detection with YOLOv5
        
        # Extract detected objects' names and confidence scores
        labels = results.pandas().xyxy[0]['name'].tolist()
        
        return labels
    except Exception as e:
        print(f"Failed to process image {image_path}: {e}")
        return []

# Directory containing images
image_dir = '/Users/shashankramachandran/desktop/StreetViewImages/LIMA'

# List to hold detected labels across all images
all_labels = []

# Recursively process each image in the directory and its subdirectories
for root, dirs, files in os.walk(image_dir):
    for filename in files:
        if filename.endswith('.jpg'):
            image_path = os.path.join(root, filename)
            labels = analyze_image(image_path)
            all_labels.extend(labels)

# Count the occurrences of each unique label
label_counts = Counter(all_labels)

# Convert the counts to a DataFrame
df = pd.DataFrame(label_counts.items(), columns=['Label', 'Count'])

# Specify the path to save the CSV on your desktop
csv_path = '/Users/shashankramachandran/Desktop/label_analysis_results-LIMA.csv'

# Save to CSV
df.to_csv(csv_path, index=False)

# Print the DataFrame
print(df)

print(f"\nCSV file saved successfully to: {csv_path}")
