import os
import pandas as pd
from collections import Counter
from google.cloud import vision
import io
from google.oauth2 import service_account

# Manually provide service account credentials
credentials = service_account.Credentials.from_service_account_file('/Users/shashankramachandran/Desktop/StreetViewImages/robotic-augury-431221-b9-d9b8c0505c14.json')
# Initialize the Google Vision client with credentials
client = vision.ImageAnnotatorClient(credentials=credentials)

def parse_coordinates(filename):
    """Extracts coordinates from filename formatted as latitude_longitude.jpg."""
    base = os.path.basename(filename)
    name, ext = os.path.splitext(base)
    latitude, longitude = map(float, name.split('_'))
    return latitude, longitude

def analyze_image(image_path):
    """Analyzes an image to detect labels using Google Vision API."""
    try:
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.label_detection(image=image)
        
        # Debugging: Print full response
        #print(f"Full response for {image_path}: {response}")
        
        if response.error.message:
            raise Exception(response.error.message)
        
        return response.label_annotations
    except Exception as e:
        print(f"Failed to process image {image_path}: {e}")
        return []

# Directory containing images
image_dir = '/Users/shashankramachandran/desktop/StreetViewImages/Los_Angeles'

# Initialize the dataframe to store results
image_data = []
all_labels = set()  # To keep track of all unique labels across images

# Recursively process each image in the directory and its subdirectories
for root, dirs, files in os.walk(image_dir):
    for filename in files:
        if filename.endswith('.jpg'):
            image_path = os.path.join(root, filename)
            print(f"Processing image: {filename}")
            labels = analyze_image(image_path)
            label_descriptions = [label.description for label in labels]
            
            # Add all detected labels to the overall set
            all_labels.update(label_descriptions)
            
            # Create a binary row indicating the presence of each label
            binary_row = {label: 1 if label in label_descriptions else 0 for label in all_labels}
            binary_row["Image"] = filename  # Add the image filename to identify the row
            
            image_data.append(binary_row)

# Convert the results to a DataFrame
df = pd.DataFrame(image_data)

# Fill missing columns with 0s (for labels that may not appear in all images)
df = df.fillna(0)

# Reorder columns so 'Image' is the first column
df = df[['Image'] + list(all_labels)]

# Print information about the dataframe
print("\nDataframe created with the following columns:")
print(df.columns)

# Specify the path to save the CSV on your desktop
csv_path = '/Users/shashankramachandran/Desktop/label_analysis_binary_results_LA.csv'

# Save to CSV
df.to_csv(csv_path, index=False)

# Print the DataFrame
print(df)

print(f"\nCSV file saved successfully to: {csv_path}")
