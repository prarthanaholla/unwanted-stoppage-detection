import json
import requests

# === CONFIG ===
input_file = "map_matched.geojson"
output_file = "output.geojson"
valhalla_url = "http://localhost:8002/route"

# === Load matched points ===
with open(input_file, "r") as f:
    data = json.load(f)

# Extract features (to access both coordinates and original_time)
features = data["features"]
matched_coords = [feat["geometry"]["coordinates"] for feat in features]

# === Compute road distance between each pair using Valhalla ===
route_segments = []
total_distance = 0.0

for i in range(len(matched_coords) - 1):
    start = matched_coords[i]
    end = matched_coords[i + 1]

    # Ensure timestamps exist for both points, otherwise set to None
    start_time = features[i]["properties"].get("original_time", None)
    end_time = features[i + 1]["properties"].get("original_time", None)

    # Optional: Handle missing timestamps, you can skip or assign a default
    if start_time is None or end_time is None:
        print(f"⚠️ Missing timestamp for segment {i}-{i+1}, skipping segment")
        continue  # Skip this segment or assign a default value if you wish

    body = {
        "locations": [
            {"lat": start[1], "lon": start[0]},
            {"lat": end[1], "lon": end[0]}
        ],
        "costing": "bicycle",
        "directions_options": {"units": "kilometers"}
    }

    res = requests.post(valhalla_url, json=body)
    if res.status_code != 200:
        print(f"⚠️ Failed between point {i}-{i+1}: {res.text}")
        continue

    route = res.json()["trip"]
    dist_meters = route["summary"]["length"] * 1000  # Convert km to meters
    total_distance += dist_meters

    # Create a LineString feature with route distance and original timestamps
    segment = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [start, end]
        },
        "properties": {
            "from_index": i,
            "to_index": i + 1,
            "route_distance_meters": round(dist_meters, 2),
            "start_time": start_time,
            "end_time": end_time
        }
    }
    route_segments.append(segment)

# === Write output GeoJSON ===
output_geojson = {
    "type": "FeatureCollection",
    "features": route_segments
}

with open(output_file, "w") as f:
    json.dump(output_geojson, f, indent=2)

print(f"\n✅ Total route distance: {round(total_distance, 2)} meters")
print(f"✅ Output saved to {output_file}")
