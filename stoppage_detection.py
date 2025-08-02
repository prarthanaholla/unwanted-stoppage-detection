import json
import pandas as pd

# --- Load route segments GeoJSON (updated with route distances) ---
with open("output.geojson", "r") as f:
    geojson_input = json.load(f)

# --- Extract data with original index and route distances ---
locations = []
for i, feature in enumerate(geojson_input["features"]):
    start_point = feature["geometry"]["coordinates"][0]
    end_point = feature["geometry"]["coordinates"][-1]
    route_distance = feature["properties"]["route_distance_meters"]  # Already in meters
    location_time_start = feature["properties"]["start_time"]
    location_time_end = feature["properties"]["end_time"]
    locations.append({
        "index": i,
        "start_lat": start_point[1],
        "start_lon": start_point[0],
        "end_lat": end_point[1],
        "end_lon": end_point[0],
        "route_distance": route_distance,
        "start_time": location_time_start,
        "end_time": location_time_end
    })

df = pd.DataFrame(locations)

# --- Constants ---
SPEED_MPS = 20 * 1000 / 3600  # 20 km/h = 5.5556 meters per second
DISTANCE_THRESHOLD = 10       # in meters
TIME_THRESHOLD = 60           # in seconds

# --- Stop detection ---
start = 0
end = 1
stoppages = []

while end < len(df):  # Loop until the last point
    # Get start point and the next point (moving by one step instead of three)
    start_lat, start_lon = df.loc[start, ['start_lat', 'start_lon']]
    end_lat, end_lon = df.loc[end, ['end_lat', 'end_lon']]
    
    # Sum the route distances between start and end points
    route_distance = sum(df.loc[start:end+1, 'route_distance'])  # Total route distance from start to end
    
    t1 = df.loc[start, 'start_time']  # Start time of first point
    t2 = df.loc[end, 'end_time']  # End time of second point
    
    real_time_sec = t2 - t1  # Time difference between the first and the second point

    # Calculate expected time based on route distance and speed
    expected_time = route_distance / SPEED_MPS

    # Debugging output
    print(f"[{start}->{end}] Distance: {route_distance:.2f} m, Time: {real_time_sec:.2f} s, Expected Time: {expected_time:.2f} s")

    # If the vehicle has traveled more than the distance threshold
    if route_distance > DISTANCE_THRESHOLD:
        if real_time_sec > expected_time:
            # Mark as a stoppage if the actual time exceeds the expected time
            stoppages.append(df.loc[start])  # Append the start point as a stoppage
        start = end  # Shift the start pointer to the current end
        end += 1  # Move the end pointer by 1 step
    else:
        # If the distance is small, check the time threshold
        if real_time_sec > TIME_THRESHOLD:
            # Mark as a stoppage if the time threshold is exceeded
            stoppages.append(df.loc[start])  # Append the start point as a stoppage
            start = end  # Shift the start pointer to the current end
        end += 1  # Move the end pointer by 1 step

# --- Create GeoJSON output for stoppages ---
stoppage_features = []
for _, row in pd.DataFrame(stoppages).iterrows():
    stoppage_features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [row["start_lon"], row["start_lat"]]
        },
        "properties": {
            "input_index": int(row["index"]),
            "start_time": int(row["start_time"]),
            "end_time": int(row["end_time"]),
            "route_distance_meters": round(row["route_distance"], 2)
        }
    })

stoppage_geojson = {
    "type": "FeatureCollection",
    "features": stoppage_features
}

# --- Save stoppages as GeoJSON ---
with open("stoppages.geojson", "w") as f:
    json.dump(stoppage_geojson, f, indent=2)

# --- Save stoppages as CSV ---
stoppage_df = pd.DataFrame(stoppages)
stoppage_df.to_csv("stoppages.csv", index=False)

print("Saved both 'stoppages.geojson' and 'stoppages.csv'")
