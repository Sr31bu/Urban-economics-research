import os
import pandas as pd
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
        print(f"Full response for {image_path}: {response}")
        
        if response.error.message:
            raise Exception(response.error.message)
        
        return response.label_annotations
    except Exception as e:
        print(f"Failed to process image {image_path}: {e}")
        return []

# Directory containing images
image_dir = '/Users/shashankramachandran/desktop/StreetViewImages/LIMA'

# List to hold data
data = []

# Recursively process each image in the directory and its subdirectories
for root, dirs, files in os.walk(image_dir):
    for filename in files:
        if filename.endswith('.jpg'):
            image_path = os.path.join(root, filename)
            labels = analyze_image(image_path)
            latitude, longitude = parse_coordinates(filename)

            # Debugging: Print label descriptions detected
            label_descriptions = [label.description for label in labels]
            print(f"Labels detected in {filename}: {label_descriptions}")

            fire_hydrant = any(label.description == 'Fire hydrant' for label in labels)
            electricity_line = any(label.description == 'Electricity line' for label in labels)
            paved_road = any(label.description in ['Asphalt', 'Road'] for label in labels)
            tree = any(label.description == 'Tree' for label in labels)

            data.append([latitude, longitude, fire_hydrant, electricity_line, paved_road, tree])

# Create DataFrame
df = pd.DataFrame(data, columns=['Latitude', 'Longitude', 'Fire Hydrant', 'Electricity Line', 'Road', 'Tree'])

# Specify the path to save the CSV on your desktop
csv_path = '/Users/shashankramachandran/Desktop/image_analysis_results-LIMA.csv'

# Save to CSV
df.to_csv(csv_path, index=False)

# Print the DataFrame
print(df)

print(f"\nCSV file saved successfully to: {csv_path}")
