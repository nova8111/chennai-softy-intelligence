"""
Traffic Metric Engine for Chennai Arterial Corridors.
Integrates with Google Routes API / Distance Matrix API with SQLite persistent caching,
computes Congestion Factor (CF = duration_in_traffic / free_flow_duration),
and simulates traffic performance across 7 days x 4 time intervals.
"""

import os
import json
import sqlite3
import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Any, Optional
import requests

import config

CACHE_DB_PATH = config.CACHE_DB_PATH


class TrafficEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.GOOGLE_MAPS_API_KEY
        self._corridor_lookup = {c["id"]: c for c in config.ARTERIAL_CORRIDORS}
        self._init_sqlite_cache()

    def _init_sqlite_cache(self) -> None:
        """Initializes SQLite database tables for caching Google API responses and metrics."""
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_traffic_cache (
                    cache_key TEXT PRIMARY KEY,
                    corridor_id TEXT,
                    day_of_week TEXT,
                    time_interval TEXT,
                    origin TEXT,
                    destination TEXT,
                    distance_km REAL,
                    free_flow_duration_min REAL,
                    duration_in_traffic_min REAL,
                    congestion_factor REAL,
                    speed_kmh REAL,
                    source TEXT,
                    response_json TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_traffic_lookup 
                ON api_traffic_cache(corridor_id, day_of_week, time_interval)
            """)
            conn.commit()

    def _generate_cache_key(
        self,
        corridor_id: str,
        day_of_week: str,
        time_interval: str,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> str:
        """Generates deterministic SHA-256 hash key based on coordinates, day, and time slots."""
        raw_key = f"{corridor_id}:{day_of_week}:{time_interval}:{origin[0]:.4f},{origin[1]:.4f}:{destination[0]:.4f},{destination[1]:.4f}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached traffic result from SQLite."""
        try:
            with sqlite3.connect(CACHE_DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM api_traffic_cache WHERE cache_key = ?", (cache_key,))
                row = cursor.fetchone()
                if row:
                    c_info = self._corridor_lookup.get(row["corridor_id"], {})
                    free_flow = float(row["free_flow_duration_min"])
                    in_traffic = float(row["duration_in_traffic_min"])
                    return {
                        "corridor_id": row["corridor_id"],
                        "corridor_name": c_info.get("name", row["corridor_id"]),
                        "zone": c_info.get("zone", "Core Urban"),
                        "day_of_week": row["day_of_week"],
                        "time_interval": row["time_interval"],
                        "origin": c_info.get("origin", (0.0, 0.0)),
                        "destination": c_info.get("destination", (0.0, 0.0)),
                        "distance_km": float(row["distance_km"]),
                        "free_flow_duration_min": free_flow,
                        "duration_in_traffic_min": in_traffic,
                        "delay_mins": round(max(0.0, in_traffic - free_flow), 1),
                        "congestion_factor": float(row["congestion_factor"]),
                        "speed_kmh": float(row["speed_kmh"]),
                        "source": row["source"],
                        "cached": True,
                    }
        except Exception as e:
            print(f"[Cache Warning] Failed to read from cache: {e}")
        return None

    def _save_to_cache(self, cache_key: str, data: Dict[str, Any], raw_response: Dict[str, Any]) -> None:
        """Saves traffic computation result into SQLite cache."""
        try:
            with sqlite3.connect(CACHE_DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO api_traffic_cache (
                        cache_key, corridor_id, day_of_week, time_interval,
                        origin, destination, distance_km, free_flow_duration_min,
                        duration_in_traffic_min, congestion_factor, speed_kmh,
                        source, response_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cache_key,
                    data["corridor_id"],
                    data["day_of_week"],
                    data["time_interval"],
                    f"{data['origin'][0]},{data['origin'][1]}",
                    f"{data['destination'][0]},{data['destination'][1]}",
                    data["distance_km"],
                    data["free_flow_duration_min"],
                    data["duration_in_traffic_min"],
                    data["congestion_factor"],
                    data["speed_kmh"],
                    data.get("source", "SIMULATION"),
                    json.dumps(raw_response)
                ))
                conn.commit()
        except Exception as e:
            print(f"[Cache Warning] Failed to write to cache: {e}")

    def call_google_routes_api(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        waypoints: Optional[List[Tuple[float, float]]] = None,
        departure_dt: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calls modern Google Routes API (routes.googleapis.com/directions/v2:computeRoutes)
        with traffic awareness and route duration calculations.
        """
        if not self.api_key:
            return None

        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.staticDuration,routes.description,routes.polyline.encodedPolyline"
        }

        body: Dict[str, Any] = {
            "origin": {"location": {"latLng": {"latitude": origin[0], "longitude": origin[1]}}},
            "destination": {"location": {"latLng": {"latitude": destination[0], "longitude": destination[1]}}},
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
        }

        if waypoints:
            body["intermediates"] = [
                {"location": {"latLng": {"latitude": wp[0], "longitude": wp[1]}}}
                for wp in waypoints
            ]

        if departure_dt:
            body["departureTime"] = departure_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            response = requests.post(url, headers=headers, json=body, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "routes" in data and len(data["routes"]) > 0:
                    route = data["routes"][0]
                    # Parse durations: e.g. "1240s"
                    def parse_sec(dur_str: str) -> float:
                        if isinstance(dur_str, str) and dur_str.endswith("s"):
                            return float(dur_str[:-1])
                        return float(dur_str or 0)

                    duration_in_traffic_sec = parse_sec(route.get("duration", "0s"))
                    static_duration_sec = parse_sec(route.get("staticDuration", "0s")) or duration_in_traffic_sec
                    distance_meters = float(route.get("distanceMeters", 0))

                    return {
                        "distance_km": round(distance_meters / 1000.0, 2),
                        "duration_in_traffic_min": round(duration_in_traffic_sec / 60.0, 2),
                        "free_flow_duration_min": round(static_duration_sec / 60.0, 2),
                        "polyline": route.get("polyline", {}).get("encodedPolyline", ""),
                        "raw": data
                    }
            else:
                print(f"[Google Routes API HTTP {response.status_code}] {response.text[:200]}")
        except Exception as e:
            print(f"[Google Routes API Exception] {e}")

        return None

    def compute_corridor_metric(
        self,
        corridor: Dict[str, Any],
        day_of_week: str,
        time_interval_key: str
    ) -> Dict[str, Any]:
        """
        Computes traffic metrics for a single corridor at a specific day and time interval.
        Leverages SQLite caching first, then Google Routes API, with calibrated fallback simulation.
        """
        corridor_id = corridor["id"]
        origin = corridor["origin"]
        destination = corridor["destination"]
        waypoints = corridor.get("waypoints", [])

        time_info = config.TIME_INTERVALS.get(time_interval_key, {})
        time_id = time_info.get("id", "evening_peak")

        cache_key = self._generate_cache_key(corridor_id, day_of_week, time_id, origin, destination)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        # Calculate departure timestamp for future simulation if calling live API
        # e.g., Next occurrence of day_of_week at start of interval
        days_map = {d: i for i, d in enumerate(config.DAYS_OF_WEEK)}
        now = datetime.now(timezone.utc)
        current_day_idx = now.weekday()  # Mon=0, Sun=6
        target_day_idx = days_map.get(day_of_week, 0)
        days_ahead = (target_day_idx - current_day_idx) % 7
        if days_ahead == 0 and now.hour > time_info.get("hour_start", 18):
            days_ahead = 7
        
        target_date = now + timedelta(days=days_ahead)
        start_hour = int(time_info.get("hour_start", 18))
        target_dt = target_date.replace(hour=start_hour, minute=30, second=0, microsecond=0)

        # Attempt Google Routes API
        api_result = None
        if self.api_key:
            api_result = self.call_google_routes_api(origin, destination, waypoints, target_dt)

        if api_result and api_result.get("free_flow_duration_min", 0) > 0:
            free_flow = api_result["free_flow_duration_min"]
            in_traffic = api_result["duration_in_traffic_min"]
            cf = round(max(1.0, in_traffic / free_flow), 3)
            dist_km = api_result["distance_km"]
            speed_kmh = round(dist_km / (in_traffic / 60.0), 1) if in_traffic > 0 else 45.0
            source = "GOOGLE_ROUTES_API"
            raw_payload = api_result["raw"]
        else:
            # Calibrated urban traffic simulation model for Chennai
            base_free_flow = corridor["free_flow_mins"]
            dist_km = corridor["length_km"]
            
            # Extract day and interval specific corridor weight
            day_weights = corridor.get("congestion_weights", {}).get(day_of_week, {})
            corridor_weight = day_weights.get(time_id)
            if corridor_weight is None:
                corridor_weight = corridor.get("base_cf", {}).get(time_id, 1.5)
            
            # Apply slight realistic variability
            hash_int = int(hashlib.md5(f"{corridor_id}{day_of_week}{time_id}".encode()).hexdigest(), 16)
            jitter = ((hash_int % 15) - 7) / 100.0  # -0.07 to +0.07
            cf = round(max(1.0, corridor_weight + jitter), 3)
            
            in_traffic = round(base_free_flow * cf, 2)
            free_flow = round(base_free_flow, 2)
            speed_kmh = round(dist_km / (in_traffic / 60.0), 1)
            source = "CALIBRATED_CHENNAI_URBAN_MODEL"
            raw_payload = {"simulation": True, "base_multiplier": corridor_weight, "jitter": jitter}

        metric_data = {
            "corridor_id": corridor_id,
            "corridor_name": corridor["name"],
            "zone": corridor["zone"],
            "day_of_week": day_of_week,
            "time_interval": time_interval_key,
            "origin": origin,
            "destination": destination,
            "distance_km": dist_km,
            "free_flow_duration_min": free_flow,
            "duration_in_traffic_min": in_traffic,
            "delay_mins": round(max(0.0, in_traffic - free_flow), 1),
            "congestion_factor": cf,
            "speed_kmh": speed_kmh,
            "source": source,
            "cached": False,
        }

        self._save_to_cache(cache_key, metric_data, raw_payload)
        return metric_data

    def get_corridor_metrics_for_schedule(
        self,
        day_of_week: str,
        time_interval_key: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Computes or retrieves metrics for all 7 arterial corridors for the specified day and interval.
        Returns a dictionary keyed by corridor_id.
        """
        results = {}
        for corridor in config.ARTERIAL_CORRIDORS:
            metric = self.compute_corridor_metric(corridor, day_of_week, time_interval_key)
            results[corridor["id"]] = metric
        return results

    def get_top_congested_corridors(
        self,
        day_of_week: str,
        time_interval_key: str,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Identifies and ranks the top N most congested road corridors for the given day and interval
        sorted descending by Congestion Factor (CF).
        """
        all_metrics = self.get_corridor_metrics_for_schedule(day_of_week, time_interval_key)
        sorted_corridors = sorted(
            all_metrics.values(),
            key=lambda x: x["congestion_factor"],
            reverse=True
        )
        return sorted_corridors[:top_n]

    def get_7day_congestion_matrix(self) -> Dict[str, Any]:
        """
        Pre-computes a full 7-day x 4-interval congestion factor matrix across all corridors.
        Useful for multi-day comparative analysis and heatmaps.
        """
        matrix_records = []
        for day in config.DAYS_OF_WEEK:
            for interval in config.TIME_INTERVALS.keys():
                metrics = self.get_corridor_metrics_for_schedule(day, interval)
                for c_id, m in metrics.items():
                    matrix_records.append({
                        "corridor_id": c_id,
                        "corridor_name": m.get("corridor_name", c_id),
                        "day_of_week": day,
                        "time_interval": interval,
                        "congestion_factor": m["congestion_factor"],
                        "delay_mins": m["delay_mins"],
                        "speed_kmh": m["speed_kmh"],
                    })
        return matrix_records

    def get_summary_kpis(
        self,
        day_of_week: str,
        time_interval_key: str
    ) -> Dict[str, Any]:
        """
        Computes summary KPI indicators for the interactive dashboard:
        - Worst congested corridor today
        - Average corridor speed during peak hours
        - Maximum delay in minutes
        """
        metrics = list(self.get_corridor_metrics_for_schedule(day_of_week, time_interval_key).values())
        if not metrics:
            return {}

        worst_corridor = max(metrics, key=lambda x: x["congestion_factor"])
        avg_speed = round(sum(m["speed_kmh"] for m in metrics) / len(metrics), 1)
        max_delay = max(m["delay_mins"] for m in metrics)

        return {
            "worst_corridor_name": worst_corridor.get("corridor_name", "N/A"),
            "worst_congestion_factor": worst_corridor["congestion_factor"],
            "worst_corridor_delay_mins": worst_corridor["delay_mins"],
            "worst_corridor_speed_kmh": worst_corridor["speed_kmh"],
            "average_speed_kmh": avg_speed,
            "max_delay_mins": max_delay,
            "active_day": day_of_week,
            "active_interval": time_interval_key,
        }


if __name__ == "__main__":
    print("Testing Traffic Engine...")
    engine = TrafficEngine()
    print("Evaluating Monday Evening Peak...")
    mon_evening = engine.get_top_congested_corridors("Monday", "Evening Peak (17:30 - 20:30)")
    for rank, c in enumerate(mon_evening, 1):
        print(f"#{rank} {c.get('corridor_name')} | CF: {c['congestion_factor']} | Delay: {c['delay_mins']}m | Speed: {c['speed_kmh']} km/h")
    
    kpis = engine.get_summary_kpis("Monday", "Evening Peak (17:30 - 20:30)")
    print("\nSummary KPIs:", kpis)
