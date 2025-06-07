import requests
import os
import geopandas as gpd
from shapely.geometry import Point
import gzip
import shutil

address = "5 rue Choron, 75009 Paris"
response = requests.get(f"https://api-adresse.data.gouv.fr/search/?q={address}&limit=1")
data = response.json()

feature = data['features'][0]
lon, lat = feature['geometry']['coordinates']
insee_code = feature['properties']['citycode']

print(f"Coordinates: {lat}, {lon}")
print(f"INSEE code: {insee_code}")

department_code = insee_code[:2]
url = f"https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/communes/{department_code}/{insee_code}/cadastre-{insee_code}-parcelles.json.gz"
filename = f"cadastre-{insee_code}-parcelles.json.gz"

# Download the file if it doesn't exist
if not os.path.exists(filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
        
# Unzip the downloaded file
unzipped_filename = filename.replace('.gz', '')
if not os.path.exists(unzipped_filename):
    with gzip.open(filename, 'rb') as f_in:
        with open(unzipped_filename, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


gdf = gpd.read_file(unzipped_filename)
gdf = gdf.to_crs(epsg=4326)
point = Point(lon, lat)
matching_parcels = gdf[gdf.geometry.contains(point)]

if not matching_parcels.empty:
    if os.path.exists(filename):  # the .gz file
        os.remove(filename)
    if os.path.exists(unzipped_filename):  # the extracted .json file
        os.remove(unzipped_filename)
    print(f"  IDU: {matching_parcels['commune'].values[0] + matching_parcels['section'].values[0]}")
else:
    print("No matching parcel found.")

