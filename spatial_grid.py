"""
Spatial Grid Module for Chennai Urban Analytics.
Defines the spatial polygon using GeoPandas covering Chennai's core urban footprint,
and partitions it into an Uber H3 Hexagonal Grid (Resolution 8: edge length ~460m).
"""

import json
from typing import Dict, List, Tuple, Any, Optional
import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
import h3

import config


def get_chennai_boundary_gdf() -> gpd.GeoDataFrame:
    """
    Creates and returns a GeoDataFrame with Chennai's core urban footprint polygon.
    Polygon coordinates are (lat, lng), converted to Shapely (lng, lat) for GIS standards.
    """
    coords_lng_lat = [(lng, lat) for lat, lng in config.CHENNAI_POLYGON_COORDS]
    polygon = Polygon(coords_lng_lat)
    
    gdf = gpd.GeoDataFrame(
        [{"name": "Chennai Urban Extent", "geometry": polygon}],
        geometry="geometry",
        crs="EPSG:4326"
    )
    return gdf


def generate_h3_grid(resolution: int = config.H3_RESOLUTION) -> gpd.GeoDataFrame:
    """
    Partitions the Chennai boundary polygon into Uber H3 Hexagonal Grid cells.
    Uses H3 Resolution 8 (~460m edge length, ~0.737 km2 area).
    Returns a GeoDataFrame containing cell_id, lat, lng, and hexagon polygon geometry.
    """
    # H3 v4 accepts LatLngPoly with list of (lat, lng) tuples
    lat_lng_poly = h3.LatLngPoly(config.CHENNAI_POLYGON_COORDS)
    h3_cells = h3.polygon_to_cells(lat_lng_poly, resolution)

    hex_records = []
    for cell in h3_cells:
        lat, lng = h3.cell_to_latlng(cell)
        boundary_lat_lng = h3.cell_to_boundary(cell)
        # Convert boundary to (lng, lat) for Shapely Polygon
        boundary_lng_lat = [(pt_lng, pt_lat) for pt_lat, pt_lng in boundary_lat_lng]
        geom = Polygon(boundary_lng_lat)

        hex_records.append({
            "cell_id": str(cell),
            "lat": lat,
            "lng": lng,
            "geometry": geom,
            "congestion_factor": 1.0,
            "store_count": 0,
            "total_footfall_proxy": 0.0,
            "nearest_corridor": "",
            "zone": "Core Urban"
        })

    gdf_hex = gpd.GeoDataFrame(hex_records, geometry="geometry", crs="EPSG:4326")
    return gdf_hex


def get_corridors_gdf(corridors: Optional[List[Dict[str, Any]]] = None) -> gpd.GeoDataFrame:
    """
    Constructs a GeoDataFrame containing LineString geometries for all arterial road corridors.
    """
    if corridors is None:
        corridors = config.ARTERIAL_CORRIDORS

    corridor_records = []
    for c in corridors:
        # Construct points list: origin -> waypoints -> destination
        pts = [c["origin"]] + c.get("waypoints", []) + [c["destination"]]
        line_coords = [(lng, lat) for lat, lng in pts]
        line_geom = LineString(line_coords)

        corridor_records.append({
            "id": c["id"],
            "name": c["name"],
            "zone": c["zone"],
            "length_km": c["length_km"],
            "free_flow_mins": c["free_flow_mins"],
            "speed_limit_kmh": c["speed_limit_kmh"],
            "origin_name": c["origin_name"],
            "destination_name": c["destination_name"],
            "geometry": line_geom,
        })

    gdf = gpd.GeoDataFrame(corridor_records, geometry="geometry", crs="EPSG:4326")
    return gdf


def interpolate_corridor_congestion_to_h3(
    gdf_hex: gpd.GeoDataFrame,
    corridor_metrics: Dict[str, Dict[str, Any]],
    decay_distance_deg: float = 0.035  # ~3.8 km influence radius
) -> gpd.GeoDataFrame:
    """
    Spatially interpolates road corridor congestion onto H3 hexagonal grid cells
    using inverse distance weighting to simulate urban traffic spillover.
    """
    gdf_result = gdf_hex.copy()
    gdf_corridors = get_corridors_gdf()

    # Pre-extract corridor geometries and their current congestion factor
    corridor_data = []
    for _, row in gdf_corridors.iterrows():
        c_id = row["id"]
        c_metrics = corridor_metrics.get(c_id, {})
        cf = c_metrics.get("congestion_factor", 1.0)
        corridor_data.append({
            "id": c_id,
            "name": row["name"],
            "geom": row["geometry"],
            "congestion_factor": cf,
            "speed_kmh": c_metrics.get("current_speed_kmh", 45.0)
        })

    congestion_factors = []
    nearest_corridors = []
    speeds = []

    for _, hex_row in gdf_result.iterrows():
        pt = Point(hex_row["lng"], hex_row["lat"])
        best_dist = float("inf")
        best_c = None
        weighted_cf_sum = 0.0
        weight_sum = 0.0

        for c in corridor_data:
            dist = pt.distance(c["geom"])
            if dist < best_dist:
                best_dist = dist
                best_c = c

            if dist < decay_distance_deg:
                w = 1.0 / ((dist + 0.005) ** 1.8)
                weighted_cf_sum += c["congestion_factor"] * w
                weight_sum += w

        if weight_sum > 0:
            interpolated_cf = weighted_cf_sum / weight_sum
            # Diminish slightly as distance increases from any road
            decay = max(0.0, 1.0 - (best_dist / (decay_distance_deg * 2.0)))
            cell_cf = 1.0 + (interpolated_cf - 1.0) * decay
        else:
            cell_cf = 1.0

        nearest_name = best_c["name"] if best_c else "Urban Grid"
        nearest_speed = best_c["speed_kmh"] if best_c else 50.0

        congestion_factors.append(round(cell_cf, 3))
        nearest_corridors.append(nearest_name)
        speeds.append(round(nearest_speed / max(1.0, cell_cf), 1))

    gdf_result["congestion_factor"] = congestion_factors
    gdf_result["nearest_corridor"] = nearest_corridors
    gdf_result["estimated_speed_kmh"] = speeds
    
    # Classify traffic intensity status
    # Green = Free flow (< 1.25), Amber = Moderate (1.25 - 1.8), Deep Red = Severe (> 1.8)
    def classify_status(cf: float) -> str:
        if cf < 1.25:
            return "Free Flow"
        elif cf < 1.80:
            return "Moderate Congestion"
        elif cf < 2.30:
            return "Heavy Congestion"
        else:
            return "Severe Gridlock"

    gdf_result["traffic_status"] = gdf_result["congestion_factor"].apply(classify_status)

    return gdf_result


def assign_store_density_to_h3(
    gdf_hex: gpd.GeoDataFrame,
    stores: List[Dict[str, Any]]
) -> gpd.GeoDataFrame:
    """
    Aggregates retail store counts and total Footfall Proxy Score (FPS) into each H3 cell.
    """
    gdf_result = gdf_hex.copy()

    store_points = []
    for s in stores:
        lat = s.get("lat") or s.get("geometry", {}).get("location", {}).get("lat")
        lng = s.get("lng") or s.get("geometry", {}).get("location", {}).get("lng")
        if lat and lng:
            fps = s.get("footfall_proxy_score", 0.0)
            store_points.append({"lat": lat, "lng": lng, "fps": fps, "name": s.get("name", "")})

    # Initialize counters
    cell_store_counts = {cell: 0 for cell in gdf_result["cell_id"]}
    cell_store_fps = {cell: 0.0 for cell in gdf_result["cell_id"]}

    for sp in store_points:
        try:
            cell = h3.latlng_to_cell(sp["lat"], sp["lng"], config.H3_RESOLUTION)
            cell_str = str(cell)
            if cell_str in cell_store_counts:
                cell_store_counts[cell_str] += 1
                cell_store_fps[cell_str] += sp["fps"]
        except Exception:
            continue

    gdf_result["store_count"] = gdf_result["cell_id"].map(cell_store_counts).fillna(0).astype(int)
    gdf_result["total_footfall_proxy"] = gdf_result["cell_id"].map(cell_store_fps).fillna(0.0).round(1)

    return gdf_result


if __name__ == "__main__":
    print("Testing Chennai Spatial Grid Generation...")
    gdf_bounds = get_chennai_boundary_gdf()
    print("Boundary Polygon Area (deg²):", gdf_bounds.area.iloc[0])
    
    gdf_grid = generate_h3_grid(config.H3_RESOLUTION)
    print(f"Generated {len(gdf_grid)} H3 Resolution {config.H3_RESOLUTION} Hexagonal Cells.")
    
    gdf_roads = get_corridors_gdf()
    print(f"Constructed {len(gdf_roads)} Arterial Road Corridors.")
    print("Sample H3 cell:", gdf_grid.iloc[0]["cell_id"], "Lat/Lng:", gdf_grid.iloc[0]["lat"], gdf_grid.iloc[0]["lng"])
