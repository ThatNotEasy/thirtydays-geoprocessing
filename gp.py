import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from modules.logging import setup_logger
import os

# === Setup logging ===
log = setup_logger()

# === 0. Ensure output folder exists ===
os.makedirs("output", exist_ok=True)
log.info("Output directory 'output' created or already exists.")

# === 1. Load the shapefile ===
log.info("Loading shapefile from 'data/my.shp'...")
gdf = gpd.read_file("data/my.shp")
log.info(f"Shapefile loaded. Total records: {len(gdf)}")

# Show available country names
country_names = gdf['name'].unique()
log.info(f"Available countries in shapefile: {country_names}")
print("Available countries:", country_names)

# === 2. Filter for Malaysia ===
log.info("Filtering for Malaysia...")
malaysia = gdf[gdf['name'] == 'Malaysia']

if malaysia.empty:
    log.error("Malaysia not found in shapefile!")
    raise ValueError("Malaysia not found in shapefile!")
log.info("Malaysia geometry extracted.")

# === 3. Simplify geometry (for performance) ===
log.info("Simplifying Malaysia geometry...")
malaysia_simplified = malaysia.copy()
malaysia_simplified['geometry'] = malaysia.geometry.simplify(tolerance=0.01, preserve_topology=True)
log.info("Geometry simplification complete.")

# === 4. Create 50 km buffer ===
log.info("Creating 50 km buffer...")
malaysia_m = malaysia.to_crs(epsg=3857)
malaysia_buffer = malaysia_m.buffer(50000)  # 50 km
malaysia_buffer_gdf = gpd.GeoDataFrame(geometry=malaysia_buffer, crs=malaysia_m.crs).to_crs(malaysia.crs)
log.info("Buffer created and reprojected to original CRS.")

# === 5. Calculate centroid ===
log.info("Calculating centroid...")
centroid_projected = malaysia_m.geometry.centroid
centroid = centroid_projected.to_crs(malaysia.crs).iloc[0]
log.info(f"Centroid coordinates (lat/lon): {centroid}")
print(f"Centroid coordinates (lat/lon): {centroid}")

# === 6. Calculate area in km² ===
log.info("Calculating area in km² using equal-area projection (EPSG:6933)...")
malaysia_equal_area = malaysia.to_crs("EPSG:6933")
area_km2 = malaysia_equal_area.geometry.area.iloc[0] / 1e6
log.info(f"Calculated area: {area_km2:.2f} km²")
print(f"Malaysia area: {area_km2:.2f} km²")

# === 7. Save output to GeoJSON ===
log.info("Saving Malaysia GeoJSON...")
malaysia.to_file("output/malaysia.geojson", driver='GeoJSON')
log.info("Saved to output/malaysia.geojson")

log.info("Saving Malaysia 50 km buffer GeoJSON...")
malaysia_buffer_gdf.to_file("output/malaysia_buffer.geojson", driver='GeoJSON')
log.info("Saved to output/malaysia_buffer.geojson")

# === 8. Plot the result ===
log.info("Plotting geometries...")
fig, ax = plt.subplots(figsize=(10, 10))
malaysia.plot(ax=ax, edgecolor='black', facecolor='lightgreen', label='Malaysia')
malaysia_buffer_gdf.plot(ax=ax, edgecolor='blue', facecolor='none', linestyle='--', label='50 km Buffer')
gpd.GeoSeries([centroid], crs=malaysia.crs).plot(ax=ax, color='red', marker='*', label='Centroid')

plt.legend()
plt.title("Malaysia Geoprocessing Example")
plt.axis('off')
plt.tight_layout()
plt.show()
log.info("Plot displayed successfully.")
