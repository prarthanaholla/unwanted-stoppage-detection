import json
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import numpy as np

# --- Haversine Distance ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# --- Calculate Speeds ---
def compute_speeds(df):
    speeds = [0]
    for i in range(1, len(df)):
        lat1, lon1 = df.iloc[i-1][['latitude', 'longitude']]
        lat2, lon2 = df.iloc[i][['latitude', 'longitude']]
        t1 = df.iloc[i-1]['locationTime']
        t2 = df.iloc[i]['locationTime']
        time_diff = (t2 - t1) / 1000  # seconds
        dist = haversine(lat1, lon1, lat2, lon2)
        speed = dist / time_diff if time_diff > 0 else 0
        speeds.append(speed)
    return speeds

# --- Enhanced Douglas–Peucker Recursive Function ---
def edp_recursive(df, start_idx, end_idx, threshold, keep_set):
    max_dist = 0
    index = -1
    for i in range(start_idx + 1, end_idx):
        x0, y0 = df.iloc[i][['longitude', 'latitude']]
        x1, y1 = df.iloc[start_idx][['longitude', 'latitude']]
        x2, y2 = df.iloc[end_idx][['longitude', 'latitude']]
        num = abs((y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 - y2*x1)
        den = sqrt((y2 - y1)**2 + (x2 - x1)**2)
        dist = num / den if den != 0 else 0
        if dist > max_dist:
            max_dist = dist
            index = i
    if max_dist > threshold and index != -1:
        keep_set.add(index)
        edp_recursive(df, start_idx, index, threshold, keep_set)
        edp_recursive(df, index, end_idx, threshold, keep_set)

# --- Main Simplification Logic Using ESTC ---
def simplify_with_estc(df, dp_threshold=10, speed_change_thresh=2.0, time_gap_thresh=90):
    df = df.copy()
    df['speed'] = compute_speeds(df)
    keep_indices = set([0, len(df)-1])

    for i in range(1, len(df)-1):
        prev_speed = df.iloc[i-1]['speed']
        curr_speed = df.iloc[i]['speed']
        next_speed = df.iloc[i+1]['speed']

        # Local speed extrema
        if (curr_speed > prev_speed and curr_speed > next_speed) or \
           (curr_speed < prev_speed and curr_speed < next_speed):
            keep_indices.add(i)

        # Sudden speed change
        if abs(curr_speed - prev_speed) > speed_change_thresh or \
           abs(next_speed - curr_speed) > speed_change_thresh:
            keep_indices.add(i)

    # Stay points by time gap
    for i in range(1, len(df)-1):
        t_gap1 = (df.iloc[i]['locationTime'] - df.iloc[i-1]['locationTime']) / 1000
        t_gap2 = (df.iloc[i+1]['locationTime'] - df.iloc[i]['locationTime']) / 1000
        if t_gap1 > time_gap_thresh or t_gap2 > time_gap_thresh:
            keep_indices.add(i)

    # Apply Douglas–Peucker for geometry
    edp_recursive(df, 0, len(df)-1, dp_threshold, keep_indices)

    simplified_df = df.iloc[sorted(keep_indices)].copy().reset_index(drop=True)
    return simplified_df

# --- Load Cleaned GeoJSON ---
with open("rawgpsdata.geojson", "r") as f:
    geojson_data = json.load(f)

# --- Parse to DataFrame ---
points = []
for feat in geojson_data["features"]:
    lon, lat = feat["geometry"]["coordinates"]
    ts = feat["properties"]["locationTime"]
    idx = feat["properties"].get("input_index", -1)
    points.append({
        "index": idx,
        "latitude": lat,
        "longitude": lon,
        "locationTime": ts
    })

df = pd.DataFrame(points)

# --- Apply ESTC-EDP Simplification ---
simplified_df = simplify_with_estc(df)

# --- Save to GeoJSON ---
simplified_features = []
for _, row in simplified_df.iterrows():
    simplified_features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [row["longitude"], row["latitude"]]
        },
        "properties": {
            "locationTime": int(row["locationTime"]),
            "input_index": int(row["index"])
        }
    })

simplified_geojson = {
    "type": "FeatureCollection",
    "features": simplified_features
}

with open("gpsdata.geojson", "w") as f:
    json.dump(simplified_geojson, f, indent=2)

# --- Save to CSV ---
simplified_df.to_csv("gpsdata.csv", index=False)

print("✅ Saved: 'gpsdata.geojson' and 'gpsdata.csv'")
