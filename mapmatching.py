import json
import requests

# --- Load GeoJSON trace ---
with open("gpsdata.geojson") as f:
    data = json.load(f)

points = []
for feature in data["features"]:
    lon, lat = feature["geometry"]["coordinates"]
    timestamp_ms = feature["properties"]["locationTime"]
    timestamp_sec = timestamp_ms // 1000  # Convert ms to seconds
    points.append({"lat": lat, "lon": lon, "time": timestamp_sec})

# --- Send to Valhalla ---
valhalla_url = "http://localhost:8002/trace_attributes"
headers = {"Content-Type": "application/json"}

locations = [{"lat": pt["lat"], "lon": pt["lon"], "time": pt["time"]} for pt in points]

payload = {
    "shape": locations,
    "costing": "bicycle",
    "shape_match": "map_snap",
    "use_timestamps": True,
    "trace_options": {
        "gps_accuracy": 5.0,
        "breakage_distance": 200,
        "interpolation_distance": 10,
        "search_radius": 30
    },
    "filters": {
        "attributes": ["matched.point"]
    }
}

response = requests.post(valhalla_url, headers=headers, json=payload)

if response.status_code != 200:
    raise Exception("Valhalla map-matching failed: " + response.text)

result = response.json()

# --- Process matched points only ---
matched_features = []
matched_points = result["matched_points"]

for i, pt in enumerate(matched_points):
    matched_features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [pt["lon"], pt["lat"]]
        },
        "properties": {
            "original_time": points[i]["time"]
        }
    })

# --- Save matched GeoJSON ---
output_geojson = {
    "type": "FeatureCollection",
    "features": matched_features
}

with open("map_matched.geojson", "w") as f:
    json.dump(output_geojson, f, indent=2)

print(" Done! Output saved to map_matched.geojson")
