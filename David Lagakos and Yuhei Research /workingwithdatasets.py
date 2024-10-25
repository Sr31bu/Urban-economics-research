import pandas as pd
import os

# Load the CSV file into a DataFrame
csv_file_path = 'results /Merged_Data_on_Common_Image_Names.csv'
df = pd.read_csv(csv_file_path)

# Filter rows where 'Asphalt' is 0 and 'paved_road' is 1
filtered_df = df[(df['Asphalt'] == 0) & (df['paved_road'] == 1)]

# Filter rows where 'fire_hydrant' is 1
fire_hydrant_df = df[df['fire_hydrant'] == 1]

# Filter rows where 'street_light' is 1 and 'Street Light' is 0
street_light_df = df[(df['street_light'] == 1) & (df['Street light'] == 0)]

# Select relevant columns to save
filtered_df_selected_columns = filtered_df[['image_name', 'Asphalt', 'paved_road']]
fire_hydrant_images = fire_hydrant_df[['image_name', 'fire_hydrant']]
street_light_images = street_light_df[['image_name', 'street_light', 'Street light']]

# Specify the output file paths on your Desktop
desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
asphalt_paved_road_csv = os.path.join(desktop_path, 'filtered_asphalt_paved_road.csv')
fire_hydrant_csv = os.path.join(desktop_path, 'fire_hydrant_images.csv')
street_light_csv = os.path.join(desktop_path, 'street_light_images.csv')

# Save the filtered data to CSV files on the desktop
#filtered_df_selected_columns.to_csv(asphalt_paved_road_csv, index=False)
#fire_hydrant_images.to_csv(fire_hydrant_csv, index=False)
street_light_images.to_csv(street_light_csv, index=False)

print(f"Filtered asphalt/paved road data saved to {asphalt_paved_road_csv}")
print(f"Fire Hydrant images saved to {fire_hydrant_csv}")
print(f"Street Light images saved to {street_light_csv}")
