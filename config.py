"""
Chennai Urban Analytics & Site Opportunity Configuration Module.
Defines geographic boundaries, arterial & secondary road networks,
commercial clusters, candidate site selection hubs, time intervals, and API settings.
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

# Google Maps Platform API Key
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# SQLite Cache Database
CACHE_DB_PATH = os.path.join(os.path.dirname(__file__), "urban_analytics_cache.db")

# Uber H3 Grid Resolution (Res 8 edge length ~460m, area ~0.737 km²)
H3_RESOLUTION = 8

# Chennai Core Urban Footprint Polygon Bounds
CHENNAI_POLYGON_COORDS = [
    (13.2200, 80.3250),  # Ennore Port / North Coast
    (13.1500, 80.3050),  # Tiruvottiyur Coast
    (13.1000, 80.2980),  # Royapuram / Port
    (13.0450, 80.2850),  # Marina Beach / Santhome Coast
    (12.9850, 80.2650),  # Besant Nagar / Thiruvanmiyur Coast
    (12.9250, 80.2550),  # Injambakkam Coast
    (12.8900, 80.2450),  # Akkarai / Sholinganallur East
    (12.8900, 80.2150),  # Sholinganallur South West
    (12.9150, 80.1450),  # Medavakkam / Tambaram East
    (12.9400, 80.1150),  # Tambaram West / Chromepet
    (12.9900, 80.1250),  # Pallavaram / Pammal
    (13.0200, 80.1100),  # Porur West
    (13.0500, 80.0950),  # Poonamallee West
    (13.0900, 80.1250),  # Ambattur / Maduravoyal
    (13.1400, 80.1650),  # Kolathur / Puzhal
    (13.1850, 80.2350),  # Manali / Madhavaram
    (13.2200, 80.3000),  # Minjur / Ennore North West
    (13.2200, 80.3250),  # Close polygon at Ennore
]

# Updated Daily Time Intervals (as requested)
TIME_INTERVALS = {
    "10:00 AM - 2:00 PM": {
        "id": "morning_lunch",
        "label": "Morning / Lunch Window",
        "time_range": "10:00 AM - 2:00 PM",
        "hour_start": 10.0,
        "hour_end": 14.0,
        "is_peak": True,
        "congestion_base_multiplier": 1.65,
    },
    "2:00 PM - 5:00 PM": {
        "id": "afternoon_transition",
        "label": "Afternoon Transition",
        "time_range": "2:00 PM - 5:00 PM",
        "hour_start": 14.0,
        "hour_end": 17.0,
        "is_peak": False,
        "congestion_base_multiplier": 1.25,
    },
    "5:00 PM - 8:00 PM": {
        "id": "evening_peak",
        "label": "Evening Peak",
        "time_range": "5:00 PM - 8:00 PM",
        "hour_start": 17.0,
        "hour_end": 20.0,
        "is_peak": True,
        "congestion_base_multiplier": 2.20,
    },
    "8:00 PM - 12:00 AM": {
        "id": "night_dinner",
        "label": "Night / Dinner Peak",
        "time_range": "8:00 PM - 12:00 AM",
        "hour_start": 20.0,
        "hour_end": 24.0,
        "is_peak": True,
        "congestion_base_multiplier": 1.55,
    },
}

DAYS_OF_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

# EXPANDED ROAD NETWORK (Primary Expressways + Secondary Commercial Arterials + Connectors)
EXPANDED_ROADS: List[Dict[str, Any]] = [
    # 1. Primary Highways
    {
        "id": "road_gst",
        "name": "GST Road (Kathipara - Tambaram belt)",
        "hierarchy": "Primary Expressway",
        "zone": "South-West",
        "origin_name": "Kathipara Junction",
        "origin": (13.0067, 80.2054),
        "destination_name": "Tambaram Sanatorium",
        "destination": (12.9249, 80.1180),
        "waypoints": [
            (12.9815, 80.1764),
            (12.9660, 80.1550),
            (12.9460, 80.1380),
        ],
        "length_km": 15.4,
        "free_flow_mins": 22.0,
        "speed_limit_kmh": 60,
        "base_cf": {"morning_lunch": 1.85, "afternoon_transition": 1.25, "evening_peak": 2.30, "night_dinner": 1.60},
    },
    {
        "id": "road_anna_salai",
        "name": "Anna Salai (Mount Road: Central to Guindy)",
        "hierarchy": "Primary Arterial",
        "zone": "Central",
        "origin_name": "Chennai Central",
        "origin": (13.0827, 80.2707),
        "destination_name": "Guindy / Kathipara",
        "destination": (13.0067, 80.2054),
        "waypoints": [
            (13.0560, 80.2580),
            (13.0360, 80.2450),
            (13.0230, 80.2280),
        ],
        "length_km": 12.8,
        "free_flow_mins": 20.0,
        "speed_limit_kmh": 50,
        "base_cf": {"morning_lunch": 1.95, "afternoon_transition": 1.30, "evening_peak": 2.50, "night_dinner": 1.70},
    },
    {
        "id": "road_omr",
        "name": "OMR / Rajiv Gandhi Salai (Madhya Kailash to Sholinganallur)",
        "hierarchy": "Primary Arterial (IT Corridor)",
        "zone": "South",
        "origin_name": "Madhya Kailash Junction",
        "origin": (13.0063, 80.2443),
        "destination_name": "Sholinganallur Junction",
        "destination": (12.9010, 80.2279),
        "waypoints": [
            (12.9800, 80.2430),
            (12.9550, 80.2410),
            (12.9350, 80.2370),
        ],
        "length_km": 13.5,
        "free_flow_mins": 19.0,
        "speed_limit_kmh": 60,
        "base_cf": {"morning_lunch": 2.20, "afternoon_transition": 1.20, "evening_peak": 2.75, "night_dinner": 1.80},
    },
    {
        "id": "road_irr",
        "name": "Inner Ring Road / JN Road (Koyambedu - Vadapalani - Kathipara)",
        "hierarchy": "Primary Arterial",
        "zone": "Central-West",
        "origin_name": "Koyambedu CMBT",
        "origin": (13.0694, 80.1948),
        "destination_name": "Kathipara Junction",
        "destination": (13.0067, 80.2054),
        "waypoints": [
            (13.0510, 80.2100),
            (13.0330, 80.2120),
            (13.0180, 80.2070),
        ],
        "length_km": 8.7,
        "free_flow_mins": 14.0,
        "speed_limit_kmh": 50,
        "base_cf": {"morning_lunch": 1.90, "afternoon_transition": 1.28, "evening_peak": 2.55, "night_dinner": 1.65},
    },
    {
        "id": "road_ph_road",
        "name": "Poonamallee High Road (Central - Koyambedu - Poonamallee)",
        "hierarchy": "Primary Arterial",
        "zone": "Central-West",
        "origin_name": "Chennai Central",
        "origin": (13.0827, 80.2750),
        "destination_name": "Poonamallee Bus Terminus",
        "destination": (13.0489, 80.0983),
        "waypoints": [
            (13.0780, 80.2430),
            (13.0720, 80.2180),
            (13.0694, 80.1948),
            (13.0580, 80.1580),
        ],
        "length_km": 19.8,
        "free_flow_mins": 32.0,
        "speed_limit_kmh": 50,
        "base_cf": {"morning_lunch": 1.80, "afternoon_transition": 1.25, "evening_peak": 2.35, "night_dinner": 1.55},
    },
    {
        "id": "road_ecr",
        "name": "ECR (Thiruvanmiyur to Sholinganallur link)",
        "hierarchy": "Primary Scenic Arterial",
        "zone": "South-East Coast",
        "origin_name": "Thiruvanmiyur RTO",
        "origin": (12.9830, 80.2594),
        "destination_name": "Akkarai / Sholinganallur Link",
        "destination": (12.9022, 80.2514),
        "waypoints": [
            (12.9620, 80.2580),
            (12.9450, 80.2560),
            (12.9280, 80.2540),
            (12.9150, 80.2520),
        ],
        "length_km": 10.2,
        "free_flow_mins": 15.0,
        "speed_limit_kmh": 60,
        "base_cf": {"morning_lunch": 1.35, "afternoon_transition": 1.15, "evening_peak": 1.95, "night_dinner": 1.85},
    },
    {
        "id": "road_ennore",
        "name": "Ennore Expressway / Manali Oil Refinery Road",
        "hierarchy": "Industrial Arterial",
        "zone": "North",
        "origin_name": "Royapuram Bridge",
        "origin": (13.1147, 80.2986),
        "destination_name": "Ennore Thermal Station",
        "destination": (13.2100, 80.3200),
        "waypoints": [
            (13.1480, 80.3020),
            (13.1670, 80.3060),
            (13.1900, 80.3120),
        ],
        "length_km": 12.6,
        "free_flow_mins": 21.0,
        "speed_limit_kmh": 50,
        "base_cf": {"morning_lunch": 1.65, "afternoon_transition": 1.35, "evening_peak": 1.85, "night_dinner": 1.40},
    },

    # 2. Secondary & High-Density Commercial Arterials
    {
        "id": "road_arcot",
        "name": "Arcot Road (Vadapalani - Porur Spine)",
        "hierarchy": "Secondary Commercial Arterial",
        "zone": "West",
        "origin_name": "Vadapalani Signal",
        "origin": (13.0505, 80.2085),
        "destination_name": "Porur Roundana",
        "destination": (13.0382, 80.1565),
        "waypoints": [
            (13.0450, 80.1850),  # Valasaravakkam
            (13.0410, 80.1680),  # Alwarthirunagar
        ],
        "length_km": 6.2,
        "free_flow_mins": 12.0,
        "speed_limit_kmh": 40,
        "base_cf": {"morning_lunch": 1.85, "afternoon_transition": 1.30, "evening_peak": 2.45, "night_dinner": 1.70},
    },
    {
        "id": "road_usman",
        "name": "Usman Road & Panagal Commercial Spine",
        "hierarchy": "Commercial Retail Core",
        "zone": "Central",
        "origin_name": "South Usman Road Flyover",
        "origin": (13.0350, 80.2310),
        "destination_name": "Panagal Park / North Usman",
        "destination": (13.0470, 80.2370),
        "waypoints": [
            (13.0410, 80.2335),  # Ranganathan St junction
        ],
        "length_km": 1.8,
        "free_flow_mins": 5.0,
        "speed_limit_kmh": 30,
        "base_cf": {"morning_lunch": 2.20, "afternoon_transition": 1.55, "evening_peak": 2.85, "night_dinner": 2.10},
    },
    {
        "id": "road_velachery_main",
        "name": "Velachery Main Road (Guindy to Tambaram link)",
        "hierarchy": "Secondary Arterial",
        "zone": "South",
        "origin_name": "Guindy Race Course",
        "origin": (13.0030, 80.2130),
        "destination_name": "Pallikaranai / Medavakkam",
        "destination": (12.9350, 80.1980),
        "waypoints": [
            (12.9815, 80.2180),  # Velachery Vijayanagar
            (12.9550, 80.2070),  # Pallikaranai Marsh
        ],
        "length_km": 9.8,
        "free_flow_mins": 17.0,
        "speed_limit_kmh": 45,
        "base_cf": {"morning_lunch": 1.90, "afternoon_transition": 1.25, "evening_peak": 2.50, "night_dinner": 1.75},
    },
    {
        "id": "road_100ft_anna_nagar",
        "name": "100 Feet Road (Thirumangalam - Anna Nagar - Kolathur)",
        "hierarchy": "Major Urban Ring Arterial",
        "zone": "West",
        "origin_name": "Koyambedu Roundtana",
        "origin": (13.0720, 80.1980),
        "destination_name": "Retteri Junction / Kolathur",
        "destination": (13.1250, 80.2050),
        "waypoints": [
            (13.0850, 80.1940),  # VR Mall / Thirumangalam
            (13.1020, 80.1980),  # Padi Flyover
        ],
        "length_km": 7.4,
        "free_flow_mins": 13.0,
        "speed_limit_kmh": 50,
        "base_cf": {"morning_lunch": 1.80, "afternoon_transition": 1.25, "evening_peak": 2.35, "night_dinner": 1.60},
    },
    {
        "id": "road_mount_poonamallee",
        "name": "Mount-Poonamallee Road (Kathipara - DLF Cybercity - Porur)",
        "hierarchy": "Tech & Commercial Corridor",
        "zone": "West",
        "origin_name": "Kathipara Junction",
        "origin": (13.0067, 80.2054),
        "destination_name": "Porur Roundana",
        "destination": (13.0382, 80.1565),
        "waypoints": [
            (13.0180, 80.1850),  # Nandambakkam / Trade Centre
            (13.0290, 80.1680),  # DLF IT Park / Ramapuram
        ],
        "length_km": 6.8,
        "free_flow_mins": 11.0,
        "speed_limit_kmh": 50,
        "base_cf": {"morning_lunch": 1.95, "afternoon_transition": 1.28, "evening_peak": 2.60, "night_dinner": 1.65},
    },
    {
        "id": "road_sardar_patel",
        "name": "Sardar Patel Road (Guindy - Raj Bhavan - Adyar)",
        "hierarchy": "Institutional & Commercial Arterial",
        "zone": "South-Central",
        "origin_name": "Guindy Kathipara",
        "origin": (13.0067, 80.2054),
        "destination_name": "Adyar Signal",
        "destination": (13.0055, 80.2570),
        "waypoints": [
            (13.0080, 80.2220),  # Anna University
            (13.0063, 80.2443),  # Madhya Kailash
        ],
        "length_km": 6.1,
        "free_flow_mins": 10.0,
        "speed_limit_kmh": 50,
        "base_cf": {"morning_lunch": 1.80, "afternoon_transition": 1.20, "evening_peak": 2.40, "night_dinner": 1.50},
    },
    {
        "id": "road_lb_road",
        "name": "Lattice Bridge (LB) Road (Adyar to Thiruvanmiyur)",
        "hierarchy": "Retail & Residential Arterial",
        "zone": "South",
        "origin_name": "Adyar Bridge / Signal",
        "origin": (13.0055, 80.2570),
        "destination_name": "Thiruvanmiyur Bus Depot",
        "destination": (12.9830, 80.2594),
        "waypoints": [
            (12.9940, 80.2580),  # Adyar Depot / Post Office
        ],
        "length_km": 3.0,
        "free_flow_mins": 6.0,
        "speed_limit_kmh": 40,
        "base_cf": {"morning_lunch": 1.70, "afternoon_transition": 1.25, "evening_peak": 2.30, "night_dinner": 1.65},
    },
    {
        "id": "road_ttk_road",
        "name": "TTK Road & CP Ramaswamy (Alwarpet Dining Hub)",
        "hierarchy": "Upscale Commercial Street",
        "zone": "Central",
        "origin_name": "Music Academy Signal",
        "origin": (13.0450, 80.2580),
        "destination_name": "Chamiers Road Junction",
        "destination": (13.0280, 80.2520),
        "waypoints": [
            (13.0360, 80.2550),  # Alwarpet Signal
        ],
        "length_km": 2.2,
        "free_flow_mins": 5.0,
        "speed_limit_kmh": 35,
        "base_cf": {"morning_lunch": 1.60, "afternoon_transition": 1.20, "evening_peak": 2.20, "night_dinner": 1.80},
    },
]

# Legacy compatibility pointer
ARTERIAL_CORRIDORS = EXPANDED_ROADS

# CANDIDATE SITE SELECTION HUBS (with specific Landmark & Coordinates)
CANDIDATE_LOCATIONS: List[Dict[str, Any]] = [
    {
        "id": "loc_tnagar",
        "name": "T. Nagar (Thyagaraya Nagar)",
        "zone": "Central",
        "landmark": "Panagal Park & Usman Road Shopping Spine",
        "metro_station": "T. Nagar / Mambalam Railway Station",
        "lat": 13.0418,
        "lng": 80.2341,
        "hub_category": "Premier High-Density Retail & Fashion",
        "density_tier": "Ultra High",
        "avg_commercial_rent_sqft": "₹180 - ₹350 / sq.ft",
        "footfall_category": "Clothing, Jewellery, Dining, Department Stores",
        "recommended_business": ["Boutique Cafe", "Jewellery Showroom", "Quick Service Restaurant", "Ethnic Apparel"],
    },
    {
        "id": "loc_velachery",
        "name": "Velachery Commercial Hub",
        "zone": "South",
        "landmark": "Phoenix Marketcity & Vijayanagar Bus Terminus",
        "metro_station": "Velachery MRTS Station",
        "lat": 12.9815,
        "lng": 80.2180,
        "hub_category": "Youth, Lifestyle & Modern Retail Hub",
        "density_tier": "Very High",
        "avg_commercial_rent_sqft": "₹120 - ₹220 / sq.ft",
        "footfall_category": "Lifestyle Malls, Entertainment, Tech Retails",
        "recommended_business": ["Specialty Coffee Shop", "Casual Dining Bistro", "Athleisure Store", "Gaming Lounge"],
    },
    {
        "id": "loc_annanagar",
        "name": "Anna Nagar (Roundtana & 2nd Avenue)",
        "zone": "West",
        "landmark": "Anna Nagar Tower Park & VR Chennai Mall",
        "metro_station": "Anna Nagar Tower & Thirumangalam Metro",
        "lat": 13.0850,
        "lng": 80.2101,
        "hub_category": "Affluent Residential & Gourmet Dining Hub",
        "density_tier": "High",
        "avg_commercial_rent_sqft": "₹140 - ₹260 / sq.ft",
        "footfall_category": "Premium Dining, Organic Groceries, Fashion Boutiques",
        "recommended_business": ["Artisanal Bakery & Cafe", "Wellness & Fitness Studio", "Fine Dining", "Luxury Salon"],
    },
    {
        "id": "loc_omr_perungudi",
        "name": "OMR Perungudi (Kandanchavadi Tech Hub)",
        "zone": "South",
        "landmark": "SP Infocity, RMZ Millenia & World Trade Center",
        "metro_station": "Perungudi Metro (Upcoming Phase 2)",
        "lat": 12.9640,
        "lng": 80.2415,
        "hub_category": "Tech Workforce & Corporate Retail Corridor",
        "density_tier": "High",
        "avg_commercial_rent_sqft": "₹90 - ₹170 / sq.ft",
        "footfall_category": "Corporate Lunches, Quick Groceries, Tech Gadgets",
        "recommended_business": ["Corporate Meal Box & Cafe", "Gym & Fitness Hub", "Co-working Lounge", "Express Grocery"],
    },
    {
        "id": "loc_omr_sholinganallur",
        "name": "Sholinganallur Junction",
        "zone": "South",
        "landmark": "ELCOT IT SEZ & Wipro Campus Gateway",
        "metro_station": "Sholinganallur Metro Junction",
        "lat": 12.9010,
        "lng": 80.2279,
        "hub_category": "Fast-Growing Tech Belt & High-Rise Living",
        "density_tier": "High",
        "avg_commercial_rent_sqft": "₹80 - ₹150 / sq.ft",
        "footfall_category": "Supermarkets, Family Dining, Evening Leisure",
        "recommended_business": ["Family Restaurant", "Supermarket Superstore", "Children Play Cafe", "Electronics Store"],
    },
    {
        "id": "loc_adyar",
        "name": "Adyar & Besant Nagar",
        "zone": "South",
        "landmark": "Adyar Signal, MG Road & Elliot's Beach",
        "metro_station": "Adyar Depot Metro (Phase 2)",
        "lat": 13.0055,
        "lng": 80.2570,
        "hub_category": "High-Income Heritage & Beachside Leisure",
        "density_tier": "Very High",
        "avg_commercial_rent_sqft": "₹150 - ₹280 / sq.ft",
        "footfall_category": "Beachfront Dining, Artisanal Foods, Organic Supermarkets",
        "recommended_business": ["Rooftop Sea-View Cafe", "Organic Health Store", "Continental Eatery", "Pet Cafe"],
    },
    {
        "id": "loc_alwarpet",
        "name": "Alwarpet & Mylapore",
        "zone": "Central",
        "landmark": "Luz Corner & Kapaleeshwarar Temple",
        "metro_station": "Mandaveli / Thirumayilai MRTS",
        "lat": 13.0339,
        "lng": 80.2677,
        "hub_category": "Cultural Heritage, Silk Sarees & Gourmet Dining",
        "density_tier": "High",
        "avg_commercial_rent_sqft": "₹130 - ₹240 / sq.ft",
        "footfall_category": "Traditional Filter Coffee, South Indian Dining, Books",
        "recommended_business": ["Heritage Vegetarian Dining", "Art Gallery & Cafe", "Silk & Handicrafts", "Boutique Clinic"],
    },
    {
        "id": "loc_vadapalani",
        "name": "Vapalani & Arcot Road",
        "zone": "West",
        "landmark": "Vadapalani Murugan Temple & Nexus Vijaya Mall",
        "metro_station": "Vadapalani Metro Station",
        "lat": 13.0505,
        "lng": 80.2085,
        "hub_category": "Cinema, Entertainment & High Transit Commuters",
        "density_tier": "Very High",
        "avg_commercial_rent_sqft": "₹110 - ₹200 / sq.ft",
        "footfall_category": "Malls, Cinema Crowds, Quick Retail",
        "recommended_business": ["Dessert & Ice Cream Parlour", "Youth Fast Food", "Apparel Outlet", "Opticals & Accessories"],
    },
    {
        "id": "loc_porur",
        "name": "Porur Junction & Mount-Poonamallee",
        "zone": "West",
        "landmark": "Porur Roundana & DLF Cybercity Tech Park",
        "metro_station": "Porur Junction Metro (Phase 2)",
        "lat": 13.0382,
        "lng": 80.1565,
        "hub_category": "West Chennai IT Gateway & Mixed Suburban",
        "density_tier": "High",
        "avg_commercial_rent_sqft": "₹85 - ₹160 / sq.ft",
        "footfall_category": "Department Stores, Electronics, Family Dining",
        "recommended_business": ["Electronics Superstore", "Multi-Cuisine Restaurant", "Large Supermarket", "Drive-thru Quick Eats"],
    },
    {
        "id": "loc_purasawalkam",
        "name": "Purasawalkam High Road",
        "zone": "North-Central",
        "landmark": "Kellys Corner, Motcham Cinema & Saravana Stores",
        "metro_station": "Kilpauk Medical College Metro",
        "lat": 13.0903,
        "lng": 80.2565,
        "hub_category": "Traditional North Chennai Textile & Gold Spine",
        "density_tier": "Very High",
        "avg_commercial_rent_sqft": "₹120 - ₹230 / sq.ft",
        "footfall_category": "Textiles, Kitchen Appliances, Gold Jewellery",
        "recommended_business": ["Jewellery & Watches", "Bridal Wear Studio", "Sweet & Savory Chaat Hub", "Footwear Megastore"],
    },
    {
        "id": "loc_georgetown",
        "name": "George Town / Parrys Corner",
        "zone": "North",
        "landmark": "Madras High Court & Broadway Bus Terminus",
        "metro_station": "High Court Metro Station",
        "lat": 13.0880,
        "lng": 80.2885,
        "hub_category": "Wholesale Trade, Hardware, Textiles & Stationery",
        "density_tier": "Ultra High",
        "avg_commercial_rent_sqft": "₹140 - ₹300 / sq.ft",
        "footfall_category": "Wholesale B2B, Stationery, Heavy Footfall",
        "recommended_business": ["B2B Wholesale Depot", "Logistics & Express Packaging", "Quick Street Food / Snacks", "Hardware Flagship"],
    },
    {
        "id": "loc_tambaram",
        "name": "Tambaram Commercial Spine",
        "zone": "South-West",
        "landmark": "Tambaram Railway Terminal & GST Road Market",
        "metro_station": "Tambaram Railway Junction",
        "lat": 12.9249,
        "lng": 80.1180,
        "hub_category": "Southern Transit Gateway & Satellite Commerce",
        "density_tier": "Very High",
        "avg_commercial_rent_sqft": "₹90 - ₹175 / sq.ft",
        "footfall_category": "Transit Shoppers, Daily Groceries, Clothing",
        "recommended_business": ["Transit Convenience Store", "Budget Fashion Store", "Snacks & Refreshment Point", "Mobile & Tech Service"],
    },
]

# Commercial Clusters for Places API
COMMERCIAL_CLUSTERS = [
    {
        "name": "T. Nagar (Thyagaraya Nagar)",
        "zone": "Central",
        "center": (13.0418, 80.2341),
        "radius_m": 1600,
        "primary_access_corridor": "road_anna_salai",
    },
    {
        "name": "Velachery Commercial Hub",
        "zone": "South",
        "center": (12.9815, 80.2180),
        "radius_m": 2000,
        "primary_access_corridor": "road_gst",
    },
    {
        "name": "Anna Nagar Hub",
        "zone": "West",
        "center": (13.0850, 80.2101),
        "radius_m": 1800,
        "primary_access_corridor": "road_irr",
    },
    {
        "name": "Mylapore & Alwarpet",
        "zone": "Central",
        "center": (13.0339, 80.2677),
        "radius_m": 1500,
        "primary_access_corridor": "road_anna_salai",
    },
    {
        "name": "OMR Tech Corridor (Perungudi & Thoraipakkam)",
        "zone": "South",
        "center": (12.9550, 80.2410),
        "radius_m": 2500,
        "primary_access_corridor": "road_omr",
    },
    {
        "name": "Purasawalkam High Road",
        "zone": "North-Central",
        "center": (13.0903, 80.2565),
        "radius_m": 1400,
        "primary_access_corridor": "road_ph_road",
    },
    {
        "name": "Poonamallee / Porur Junction",
        "zone": "West",
        "center": (13.0382, 80.1565),
        "radius_m": 2200,
        "primary_access_corridor": "road_arcot",
    },
    {
        "name": "George Town / Parrys Corner",
        "zone": "North",
        "center": (13.0880, 80.2885),
        "radius_m": 1500,
        "primary_access_corridor": "road_ennore",
    },
]

# Targeted Store / Business Categories
STORE_CATEGORIES = [
    "shopping_mall",
    "department_store",
    "clothing_store",
    "electronics_store",
    "supermarket",
    "restaurant",
    "cafe",
]
