# Unwanted Stoppage Detection from GPS Trajectories



This project focuses on detecting **unwanted or abnormal vehicle stoppages** from raw GPS trajectory data.  
In real-world fleet management and logistics systems, GPS data is noisy and unreliable. Simple rule-based approaches using fixed distance or time thresholds often result in **false stoppage detections**.

This project implements a **robust, end-to-end pipeline** that:
- Cleans noisy GPS data while preserving movement behavior
- Aligns GPS points to real road geometry
- Computes realistic route-based distances
- Detects abnormal stoppages using spatio-temporal logic

The system is **self-hosted, open-source, and designed for real-world applicability**.

---

## Problem Statement

Given raw GPS data containing:
- Latitude
- Longitude
- Timestamp
- (Optional) Speed

The goal is to detect **unplanned or abnormal stoppages** by analyzing:
- Spatial movement
- Temporal gaps
- Route-based distance (instead of straight-line distance)

The system must avoid false positives caused by:
- GPS jitter
- Traffic congestion
- Normal slowdowns and turns

---

## Challenges with Raw GPS Data

Raw GPS trajectories suffer from several real-world issues:
- **GPS jitter** even when the vehicle is stationary  
- **Sudden GPS jumps** due to signal loss  
- **Off-road points** in dense urban environments  
- **Unrealistic distance estimation** using straight-line (haversine) distance  

Without proper preprocessing, stoppage detection becomes inaccurate and unreliable.

---

##  System Architecture
Raw GPS Data
↓
EDP-based GPS Filtering
↓
Valhalla Map Matching
↓
Route Distance Calculation
↓
Stoppage Detection


## Methodology
1️. GPS Filtering using EDP (Enhanced Douglas–Peucker)

Traditional Douglas–Peucker simplifies trajectories based only on geometry, which can remove important behavioral points such as stops or speed changes.

This project uses Enhanced Douglas–Peucker (ESTC-EDP), which preserves points based on vehicle behavior, not just shape.

Constraints applied:

•	1.Time constraint → preserves stop points

•	2.Speed constraint → preserves speed changes

•	3.Spatial constraint → avoids over-smoothing

Only points with no meaningful behavioral variation are removed.

Result:

•	1.Reduced noise

•	2.Preserved stoppage-related behavior

•	3.Faster and more reliable downstream processing


2.Map Matching using Valhalla

Even after filtering, GPS points may lie beside roads. To align them correctly, this project uses Valhalla, an open-source routing and map-matching engine.

Why Valhalla:

•	Open-source and free

•	Self-hosted using Docker

•	Production-grade and scalable

How it works (conceptually):

•	Uses a Hidden Markov Model (HMM)

•	GPS points are observations

•	Road segments are hidden states

•	Uses emission probability (GPS-to-road likelihood)

•	Uses transition probability (realistic movement between roads)

•	Applies the Viterbi algorithm to find the most likely road path

Result:

GPS points snapped accurately to real road segments



3.Route Distance Calculation

Straight-line (haversine) distance underestimates real travel distance.

This step computes:

•	Actual road-network distance between consecutive points

•	Uses Valhalla routing instead of aerial distance

•	This enables realistic travel-time estimation.


4.Stoppage Detection Logic

Stoppages are detected using distance–time inconsistency, not fixed thresholds.

Let:

•	x = route distance between points

•	y = actual time difference

•	expected_time = x / average_speed

Rules:

•	Small distance + large time → stoppage

•	Actual time > expected time → stoppage

•	Both conditions do not need to be true together

This avoids false positives caused by traffic or normal movement.




##Project Structure
stoppage-analysis/
│
├── conf/
│   └── valhalla.json
│
├── custom_data/
│   ├── valhalla_tiles/
│   └── bangalore_full.osm.pbf
│
├── edp_filtering.py
├── map_matching.py
├── routedistance_calculation.py
└── stoppage_detection.py


## Setup & Execution
### Prerequisites

- Python 3.9+
- Docker
- Valhalla (Docker-based setup)
- OpenStreetMap (OSM) data in `.osm.pbf` format
- GPS trajectory dataset

#### Dataset Requirements

The GPS dataset should contain vehicle trajectory data with the following fields:
- `latitude`
- `longitude`
- `timestamp`
- `speed` *(optional)*

>  **Note:**  
> The original GPS dataset used during development is **not included in this repository** due to privacy and sensitivity concerns related to real-world location data.

Users should place their GPS dataset locally and update the input path in the scripts as required.

#### OpenStreetMap Data

Download the required regional OSM extract (e.g., from Geofabrik) and place it in:
custom_data/
└── bangalore_full.osm.pbf


OSM data is used by Valhalla for map matching and route distance calculation.

## Steps to run:
1.Start Valhalla
cmd /c valhalla_docker_setup.bat


Keep the Valhalla service running.

2.Run the Pipeline
python edp_filtering.py
python map_matching.py
python routedistance_calculation.py
python stoppage_detection.py

