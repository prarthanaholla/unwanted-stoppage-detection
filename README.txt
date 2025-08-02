1.Requirement:
install Docker 

2.Directory Structure:
.
├── conf/
│   └── valhalla.json              # Configuration file for Valhalla settings
├── custom_data/
│   ├── valhalla_tiles/            # Pre-built Valhalla map tiles
│   └── bangalore_full.osm.pbf     # OSM PBF map data for Bangalore
├── edp_filtering.py               # Python script for filtering raw GPS data(Advanced Douglas-Peucker filtering)
├── map_matching.py                # Python script for map matching GPS traces with Valhalla
├── routedistance_calculation.py   # Python script for calculating  route distance between GPS points
└── stoppage_detection.py          # Python script for stoppage detection


The valhalla.json file is the configuration file for the Valhalla routing engine, where you define settings for routing (e.g., car, bike), map matching, and tile storage. It allows you to customize how Valhalla processes GPS data and handles routing requests.

3.valhalla setup:
step 1: cmd /c valhalla_docker_setup.bat.
        (The .bat file automates the process of setting up and running a Valhalla Docker container, building map tiles from a specified OSM PBF file, and starting the Valhalla service for map-matching and routing.)

4.
step 1.In another terminal run edp_filtering.py to filter out raw gps points.
step 2:Run map_matching.py file for map matching the points.
step 3:After running the map_matching.py , run routedistance_calculation.py file for calculating the route distance between points.
step 4:Run stoppage_detection.py to get stoppage points.

