import requests
import os
import random
import shutil
from PIL import Image
from io import BytesIO
from multiprocessing import Pool
import pytesseract

def calculate_bbox(lat, lon, km_radius):
    """Calculate bounding box coordinates around a central point."""
    delta = km_radius / 111.0  # Convert km to degrees approximately
    return (lon - delta, lat - delta, lon + delta, lat + delta)

def fetch_images(api_key, center_lat, center_lon, radius_km, save_path):
    """Fetch and download Google Street View images within a specified bounding box."""
    print(f"Fetching images for center at ({center_lat}, {center_lon}) with a {radius_km} km radius...")
    bbox = calculate_bbox(center_lat, center_lon, radius_km)
    step = (bbox[2] - bbox[0]) / 40  # Fine grid for more detailed coverage

    lons = [bbox[0] + i * step for i in range(21)]  # Increased grid points
    lats = [bbox[1] + i * step for i in range(21)]  # Increased grid points

    coords = [(lat, lon) for lat in lats for lon in lons]
    print(f"Generated {len(coords)} coordinate points for fetching images.")

    with Pool(processes=8) as pool:
        results = pool.starmap(fetch_and_save_image, [(api_key, lat, lon, save_path) for lat, lon in coords])

    return [img for img in results if img]

def fetch_and_save_image(api_key, lat, lon, save_path):
    """Fetch and save an individual image."""
    image_url = generate_street_view_url(api_key, lat, lon)
    print(f"Fetching image for ({lat}, {lon}) from {image_url}")
    response = requests.get(image_url)
    if response.status_code == 200:
        if image_valid(response.content):
            image_id = f"{lat}_{lon}.jpg"
            file_path = os.path.join(save_path, image_id)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Saved image: {file_path}")
            return file_path
        else:
            print(f"No valid imagery found for ({lat}, {lon})")
    else:
        print(f"Failed to fetch image for ({lat}, {lon}). Status code: {response.status_code}")
    return None

def generate_street_view_url(api_key, lat, lon):
    """Generate the URL for the Google Street View image."""
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        'size': '640x640',
        'location': f'{lat},{lon}',
        'key': api_key
    }
    return f"{base_url}?{requests.compat.urlencode(params)}"

def image_valid(content):
    """Check if the image content is valid using OCR."""
    image = Image.open(BytesIO(content))
    text = pytesseract.image_to_string(image)
    return "no imagery here" not in text.lower()

def split_into_folders(image_paths, base_path, num_folders):
    """Split the downloaded images into folders each containing about 40-60 images."""
    print(f"Splitting {len(image_paths)} images into {num_folders} folders...")
    random.shuffle(image_paths)
    folders = {i: [] for i in range(num_folders)}
    folder_index = 0

    for image_path in image_paths:
        folders[folder_index].append(image_path)
        folder_index = (folder_index + 1) % num_folders
        if all(len(f) >= 60 for f in folders.values()):
            break

    for idx, folder_images in folders.items():
        folder_path = os.path.join(base_path, f"Folder_{idx+1}")
        os.makedirs(folder_path, exist_ok=True)
        for img in folder_images:
            shutil.move(img, folder_path)
        print(f"Moved {len(folder_images)} images to {folder_path}")

def main():
    api_key = 'AIzaSyCarYhL7ehq9jk9A1bYsJPo0fB13tbOV5w' # Replace with your actual API key
    print("Starting the Google Street View image fetcher...")
    print(f"Using API key: {api_key}")
    
    base_folder = 'StreetViewImages-SAUPOLO'
    desktop_path = os.path.join(os.environ['HOME'], 'Desktop', base_folder)
    os.makedirs(desktop_path, exist_ok=True)
    print(f"Images will be saved to: {desktop_path}")
    
    centers = [
        {'lat': -23.55052, 'lon': -46.633308, 'radius_km': 5, 'name': 'Central São Paulo'},  # Central São Paulo
        {'lat': -23.673944, 'lon': -46.626778, 'radius_km': 5, 'name': 'South São Paulo'},   # South São Paulo
        {'lat': -23.486197, 'lon': -46.628372, 'radius_km': 5, 'name': 'North São Paulo'}    # North São Paulo
    ]

    all_images = []
    for center in centers:
        center_path = os.path.join(desktop_path, center['name'])
        os.makedirs(center_path, exist_ok=True)
        print(f"Processing center: {center['name']}")
        images = fetch_images(api_key, center['lat'], center['lon'], center['radius_km'], center_path)
        all_images.extend(images)

    split_into_folders(all_images, desktop_path, 10)
    print("Image fetching and organization complete.")

if __name__ == "__main__":
    main()
