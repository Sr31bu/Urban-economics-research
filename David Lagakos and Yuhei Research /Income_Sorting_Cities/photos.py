import requests
import os
import random
import shutil
from PIL import Image
from io import BytesIO
from multiprocessing import Pool

def calculate_bbox(lat, lon, km_radius):
    """Calculate bounding box coordinates around a central point with higher precision."""
    delta = km_radius / 111.0  # Convert km to degrees approximately
    return (lon - delta, lat - delta, lon + delta, lat + delta)

def fetch_images(api_key, center_lat, center_lon, radius_km, save_path):
    """Fetch and download Google Street View images with increased grid density."""
    bbox = calculate_bbox(center_lat, center_lon, radius_km)
    step = (bbox[2] - bbox[0]) / 30  # Increased density of the grid

    lons = [bbox[0] + i * step for i in range(31)]
    lats = [bbox[1] + i * step for i in range(31)]

    coords = [(lat, lon) for lat in lats for lon in lons]
    
    with Pool(processes=8) as pool:
        results = pool.starmap(fetch_and_save_image, [(api_key, lat, lon, save_path) for lat, lon in coords])

    # Filter out None values representing failed fetches
    valid_images = [img for img in results if img]
    print(f"Total valid images fetched: {len(valid_images)}")
    random.shuffle(valid_images)
    split_into_folders(valid_images, save_path)

def fetch_and_save_image(api_key, lat, lon, save_path):
    """Fetch and save an individual image."""
    image_url = generate_street_view_url(api_key, lat, lon)
    if image_exists(image_url):
        image_id = f"{lat}_{lon}"
        return download_image(image_url, save_path, image_id)
    else:
        print(f"No image available at coordinates: {lat}, {lon}")
        return None

def generate_street_view_url(api_key, lat, lon):
    """Generate the URL for the Google Street View image."""
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        'size': '640x640',  # Define the size of the image
        'location': f'{lat},{lon}',
        'key': api_key
    }
    return f"{base_url}?{requests.compat.urlencode(params)}"

def image_exists(image_url):
    """Check for the actual presence of imagery data by analyzing multiple points in the image."""
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        points_to_check = [
            (image.width // 2, image.height // 2),  # Center
            (image.width // 4, image.height // 4),  # Top-left quarter
            (3 * image.width // 4, 3 * image.height // 4),  # Bottom-right quarter
            (image.width // 4, 3 * image.height // 4),  # Bottom-left quarter
            (3 * image.width // 4, image.height // 4)   # Top-right quarter
        ]
        # Typical color of the "no imagery" image is (230, 230, 230)
        for point in points_to_check:
            if image.getpixel(point) == (230, 230, 230):
                return False
        return True
    return False


def download_image(image_url, save_path, image_id):
    """Download an image and save it to a specified directory."""
    response = requests.get(image_url)
    if response.status_code == 200:
        file_path = os.path.join(save_path, f"{image_id}.jpg")
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded image saved to {file_path}")
        return file_path
    else:
        print(f"Failed to download image {image_id}")
    return None

def split_into_folders(image_paths, base_path):
    """Split the downloaded images into 10 random folders."""
    num_folders = 10
    for i in range(num_folders):
        folder_path = os.path.join(base_path, f"Folder_{i+1}")
        os.makedirs(folder_path, exist_ok=True)
    
    for idx, image_path in enumerate(image_paths):
        folder_index = idx % num_folders
        folder_path = os.path.join(base_path, f"Folder_{folder_index+1}")
        shutil.move(image_path, folder_path)
        print(f"Moved {image_path} to {folder_path}")

def main():
    api_key = 'AIzaSyCarYhL7ehq9jk9A1bYsJPo0fB13tbOV5w'  # Replace with your actual API key
    base_folder = 'StreetViewImages'
    desktop_path = os.path.join(os.environ['HOME'], 'Desktop', base_folder)

    # Coordinates for Los Angeles
    locations = {
        'Lima':{'lat':-12.046374,'lon': -77.042793}
    }
    radius_km = 25  # Define the radius in kilometers
    # Process each location and create separate folders
    for city, coords in locations.items():
        city_path = os.path.join(desktop_path, city.replace(" ", "_"))  # Create a valid folder name
        os.makedirs(city_path, exist_ok=True)  # Create the city-specific folder if it does not exist
        print(f"Fetching images for {city}")
        fetch_images(api_key, coords['lat'], coords['lon'], radius_km, city_path)

if __name__ == "__main__":
    main()