"""
Chennai "Softie" Pure Milk Franchise Site Selection & Competitor Intelligence Dashboard.
Exclusively focused on Ice Cream Parlours & Dessert Places:
1. Options & Catchment Filters First (Accessible throughout all tabs).
2. Clean Single-Tab Navigation (Select Comparative Evaluation, Map, Bazaars, etc. with easy back-and-forth).
3. Interactive Catchment Map with Table Below Map containing direct Clickable Google Maps Links.
4. "Softie" Pure Milk Franchise Strategic Blueprint:
   - Brand: Softie (Franchise Model)
   - 100% Pure Fresh Dairy Milk Quality
   - Core Price Starts at ₹20, Maximum Cost ₹90
   - Daily Sales Target: Average ₹15,000 / day (₹4,50,000 / month)
5. 20 High-Footfall Bazaars & Comparative Matrix.
6. Feeder Traffic & 14-Sheet Master Excel Export.
"""

import json
import os
import io
import math
import urllib.parse
import textwrap
from typing import Dict, List, Any
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt

def render_html(html_str: str):
    """Safely render HTML without Markdown indented-code-block interference."""
    st.markdown(textwrap.dedent(html_str).strip(), unsafe_allow_html=True)

import config
from spatial_grid import (
    get_chennai_boundary_gdf,
    generate_h3_grid,
    get_corridors_gdf,
    interpolate_corridor_congestion_to_h3,
    assign_store_density_to_h3
)
from traffic_engine import TrafficEngine
from store_extractor import StoreExtractor
from site_opportunity_engine import SiteOpportunityEngine, haversine_distance_km
from ice_cream_intelligence_data import (
    TOP_50_ICE_CREAM_PARLORS,
    TOP_20_BAZAAR_SITES,
    TOP_SOFTY_SPECIALISTS,
    COMPARATIVE_EVALUATION_MATRIX
)

# Page configuration
st.set_page_config(
    page_title="Softie — Pure Milk Franchise Site Selection",
    page_icon="🍦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.15rem;
        font-weight: 800;
        background: linear-gradient(90deg, #EC4899, #8B5CF6, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-bottom: 1.0rem;
    }
    .filter-panel {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border: 1px solid #3B82F6;
        border-radius: 12px;
        padding: 18px 20px 14px 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
    }
    .status-banner {
        background-color: #1E293B;
        border-radius: 8px;
        padding: 12px 18px;
        margin-bottom: 16px;
        border: 1px solid #334155;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .kpi-card {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 14px 18px;
        border-left: 4px solid #EC4899;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);
    }
    .kpi-title {
        font-size: 0.8rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.45rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 2px;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #CBD5E1;
        margin-top: 2px;
    }
    .ice-cream-card {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
        border: 1px solid #334155;
    }
    .like-box {
        background-color: #064E3B;
        border-left: 3px solid #10B981;
        padding: 10px 12px;
        border-radius: 6px;
        margin-top: 8px;
        font-size: 13px;
        color: #D1FAE5;
    }
    .dislike-box {
        background-color: #4C0519;
        border-left: 3px solid #F43F5E;
        padding: 10px 12px;
        border-radius: 6px;
        margin-top: 8px;
        font-size: 13px;
        color: #FFE4E6;
    }
    .softy-box {
        background-color: #172554;
        border-left: 3px solid #3B82F6;
        padding: 10px 12px;
        border-radius: 6px;
        margin-top: 8px;
        font-size: 13px;
        color: #DBEAFE;
    }
    .bazaar-card {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 18px;
        border: 1px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);
    }
    .bazaar-badge {
        background-color: #1E3A8A;
        color: #93C5FD;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 12px;
        display: inline-block;
    }
    .fit-box {
        background-color: #064E3B;
        border-left: 4px solid #10B981;
        padding: 12px 14px;
        border-radius: 6px;
        margin-top: 10px;
        font-size: 13.5px;
        color: #D1FAE5;
        line-height: 1.5;
    }
    .map-btn-link {
        display: inline-block;
        background-color: #2563EB;
        color: #FFFFFF !important;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 12px;
        transition: background-color 0.2s;
    }
    .map-btn-link:hover {
        background-color: #1D4ED8;
    }
    .nav-tab-pill {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 8px;
        background-color: #1E293B;
        border: 1px solid #475569;
        color: #E2E8F0;
        text-decoration: none;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    .step-badge {
        display: inline-block;
        background: linear-gradient(90deg, #EC4899, #8B5CF6);
        color: #FFFFFF;
        font-size: 12px;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 12px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "api_key" not in st.session_state:
    st.session_state["api_key"] = config.GOOGLE_MAPS_API_KEY

if "active_day" not in st.session_state:
    st.session_state["active_day"] = "Friday"

if "active_interval" not in st.session_state:
    st.session_state["active_interval"] = "5:00 PM - 8:00 PM"

if "selected_hub_idx" not in st.session_state:
    st.session_state["selected_hub_idx"] = 0

if "radius_km" not in st.session_state:
    st.session_state["radius_km"] = 5.0

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "🗺️ Interactive Catchment Map & Outlets Directory"

if "use_custom_coord" not in st.session_state:
    st.session_state["use_custom_coord"] = False

if "custom_lat" not in st.session_state:
    st.session_state["custom_lat"] = 13.0418

if "custom_lng" not in st.session_state:
    st.session_state["custom_lng"] = 80.2341

if "softy_only_mode" not in st.session_state:
    st.session_state["softy_only_mode"] = False


@st.cache_resource
def get_engines(api_key: str):
    t_engine = TrafficEngine(api_key=api_key if api_key else None)
    s_extractor = StoreExtractor(api_key=api_key if api_key else None)
    site_engine = SiteOpportunityEngine(api_key=api_key if api_key else None)
    return t_engine, s_extractor, site_engine


@st.cache_data(show_spinner=False)
def load_base_h3_grid():
    return generate_h3_grid(config.H3_RESOLUTION)


# Build Candidate Hubs List
candidate_hubs = []
for b in TOP_20_BAZAAR_SITES:
    candidate_hubs.append({
        "name": f"🛍️ {b['name']}",
        "zone": b["zone"],
        "lat": b["lat"],
        "lng": b["lng"],
        "landmark": b["landmark"]
    })
for h in config.CANDIDATE_LOCATIONS:
    candidate_hubs.append({
        "name": f"📍 {h['name']}",
        "zone": h["zone"],
        "lat": h["lat"],
        "lng": h["lng"],
        "landmark": h["landmark"]
    })

hub_names = [f"{h['name']} ({h['zone']})" for h in candidate_hubs]
if st.session_state["selected_hub_idx"] >= len(hub_names):
    st.session_state["selected_hub_idx"] = 0

radius_options = {
    "1 km (Walking Catchment)": 1.0,
    "2 km (5-min Drive Catchment)": 2.0,
    "5 km (Standard Trade Area)": 5.0,
    "10 km (Extended Metropolitan)": 10.0,
    "All Chennai (All 50 Top Parlours)": 50.0
}
radius_labels = list(radius_options.keys())

# Inverse radius lookup for index
current_radius_idx = 2
for idx, (label, val) in enumerate(radius_options.items()):
    if math.isclose(val, st.session_state["radius_km"]):
        current_radius_idx = idx
        break


# ==========================================
# SIDEBAR CONTROLS (Always available)
# ==========================================
with st.sidebar:
    st.markdown("## 🍦 Softie Franchise Hub")
    st.caption("Pure Milk Soft-Serve Franchise Site Selection & Intelligence")
    
    st.markdown("---")
    st.markdown("### 📍 Quick Hub & Catchment Selector")
    sb_hub_select = st.selectbox(
        "Target Hub / Bazaar",
        hub_names,
        index=st.session_state["selected_hub_idx"],
        key="sb_hub"
    )
    st.session_state["selected_hub_idx"] = hub_names.index(sb_hub_select)

    sb_radius_select = st.selectbox(
        "Catchment Radius",
        radius_labels,
        index=current_radius_idx,
        key="sb_rad"
    )
    st.session_state["radius_km"] = radius_options[sb_radius_select]

    st.markdown("---")
    st.markdown("### 📅 Schedule Filter")
    sb_day = st.selectbox(
        "Day of Week",
        config.DAYS_OF_WEEK,
        index=config.DAYS_OF_WEEK.index(st.session_state["active_day"]),
        key="sb_day"
    )
    st.session_state["active_day"] = sb_day

    sb_interval = st.selectbox(
        "Time Interval",
        list(config.TIME_INTERVALS.keys()),
        index=list(config.TIME_INTERVALS.keys()).index(st.session_state["active_interval"]),
        key="sb_int"
    )
    st.session_state["active_interval"] = sb_interval

    st.markdown("---")
    st.markdown("### ⚡ Franchise Mode")
    sb_softy_toggle = st.toggle(
        "Highlight Softy Specialists",
        value=st.session_state["softy_only_mode"],
        key="sb_softy_toggle"
    )
    st.session_state["softy_only_mode"] = sb_softy_toggle

    st.markdown("---")
    with st.expander("📲 Mobile Access & QR Code", expanded=False):
        st.markdown("**1. Connect Phone to Same Wi-Fi**")
        st.markdown("**2. Open URL:** `http://192.168.29.58:8501`")
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=http://192.168.29.58:8501", width=160)

    with st.expander("🔑 API Key Settings", expanded=False):
        user_api_key = st.text_input(
            "Google Maps API Key",
            value=st.session_state["api_key"],
            type="password"
        )
        if user_api_key != st.session_state["api_key"]:
            st.session_state["api_key"] = user_api_key
            st.cache_resource.clear()
            st.rerun()


# ==========================================
# Resolve Location Coordinates
# ==========================================
current_hub = candidate_hubs[st.session_state["selected_hub_idx"]]
if st.session_state["use_custom_coord"]:
    focal_lat = st.session_state["custom_lat"]
    focal_lng = st.session_state["custom_lng"]
    focal_label = f"Custom Pin ({focal_lat:.3f}, {focal_lng:.3f})"
else:
    focal_lat = current_hub["lat"]
    focal_lng = current_hub["lng"]
    focal_label = current_hub["name"]

selected_radius_km = st.session_state["radius_km"]
selected_day = st.session_state["active_day"]
selected_interval = st.session_state["active_interval"]
softy_only_mode = st.session_state["softy_only_mode"]

# Load Engines
traffic_engine, store_extractor, site_engine = get_engines(st.session_state["api_key"])

# Find Landmark & Demographics
landmark_info = site_engine.find_nearest_landmark(focal_lat, focal_lng)

# Filter all 50 Ice Cream Parlours by Selected Radius from Focal Point
parlors_with_distance = []
for p in TOP_50_ICE_CREAM_PARLORS:
    dist = haversine_distance_km(focal_lat, focal_lng, p["lat"], p["lng"])
    if dist <= selected_radius_km:
        p_copy = dict(p)
        p_copy["distance_km"] = round(dist, 2)
        if dist <= 1.0:
            p_copy["ring"] = "0 - 1 km (Immediate)"
        elif dist <= 2.0:
            p_copy["ring"] = "1 - 2 km (Secondary)"
        elif dist <= 5.0:
            p_copy["ring"] = "2 - 5 km (Trade Area)"
        else:
            p_copy["ring"] = "5 - 10 km (Extended)"
        
        # Google Maps search URL
        maps_query = urllib.parse.quote_plus(f"{p['name']} {p['address']}")
        p_copy["gmaps_url"] = f"https://www.google.com/maps/search/?api=1&query={maps_query}"
        parlors_with_distance.append(p_copy)

# Sort strictly by Review Count (User Ratings Total) descending
parlors_sorted_by_reviews = sorted(parlors_with_distance, key=lambda x: x["user_ratings_total"], reverse=True)

# Radial breakdown counts
count_1km = sum(1 for p in TOP_50_ICE_CREAM_PARLORS if haversine_distance_km(focal_lat, focal_lng, p["lat"], p["lng"]) <= 1.0)
count_2km = sum(1 for p in TOP_50_ICE_CREAM_PARLORS if haversine_distance_km(focal_lat, focal_lng, p["lat"], p["lng"]) <= 2.0)
count_5km = sum(1 for p in TOP_50_ICE_CREAM_PARLORS if haversine_distance_km(focal_lat, focal_lng, p["lat"], p["lng"]) <= 5.0)

# Feeder road traffic around focal point
corridor_metrics = traffic_engine.get_corridor_metrics_for_schedule(selected_day, selected_interval)
surrounding_roads = site_engine._analyze_surrounding_roads(focal_lat, focal_lng, selected_day, selected_interval)

# Compute Softy Opportunity Score
opportunity_score = site_engine._compute_opportunity_score(
    count_1km=count_1km,
    count_5km=count_5km,
    total_footfall=sum(p["user_ratings_total"] for p in parlors_sorted_by_reviews),
    roads=surrounding_roads,
    stores=parlors_sorted_by_reviews
)

# H3 Grid with congestion
base_h3_gdf = load_base_h3_grid()
h3_with_congestion = interpolate_corridor_congestion_to_h3(base_h3_gdf, corridor_metrics)


# ==============================================================================
# HEADER & BRANDING
# ==============================================================================
st.markdown('<div class="main-header">🍦 "Softie" — Pure Milk Soft-Serve Franchise Site Selection & Catchment Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Premium Milk-Based Franchise Model • Core Rate Starts at <b>₹20</b> • Max Rate <b>₹90</b> • Target Sales: <b>₹15,000 / Day</b> • Zero Watery Premixes</div>',
    unsafe_allow_html=True
)


# ==============================================================================
# STEP 1: OPTIONS & FILTERS FIRST (ACCESSIBLE ACROSS ALL TABS)
# ==============================================================================
with st.container():
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
        <span class="step-badge">STEP 1: OPTIONS & CATCHMENT FILTERS</span>
        <span style="font-size: 13px; color: #94A3B8;">Select your target area and radius below — updates results instantly across all views</span>
    </div>
    """, unsafe_allow_html=True)

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([1.5, 1.2, 0.9, 0.9])
    
    with filter_col1:
        chosen_hub = st.selectbox(
            "📍 Target Chennai Area / Bazaar Hub",
            hub_names,
            index=st.session_state["selected_hub_idx"],
            key="top_hub_selector",
            help="Choose from Chennai's 20 curated high-footfall retail bazaars or core commercial hubs."
        )
        if hub_names.index(chosen_hub) != st.session_state["selected_hub_idx"]:
            st.session_state["selected_hub_idx"] = hub_names.index(chosen_hub)
            st.rerun()

    with filter_col2:
        chosen_rad_label = st.selectbox(
            "🎯 Catchment Radius Around Hub",
            radius_labels,
            index=current_radius_idx,
            key="top_rad_selector",
            help="Filter competitor ice cream shops and footfall catchment by radial distance."
        )
        new_radius_km = radius_options[chosen_rad_label]
        if not math.isclose(new_radius_km, st.session_state["radius_km"]):
            st.session_state["radius_km"] = new_radius_km
            st.rerun()

    with filter_col3:
        chosen_day = st.selectbox(
            "📅 Schedule Day",
            config.DAYS_OF_WEEK,
            index=config.DAYS_OF_WEEK.index(st.session_state["active_day"]),
            key="top_day_selector"
        )
        if chosen_day != st.session_state["active_day"]:
            st.session_state["active_day"] = chosen_day
            st.rerun()

    with filter_col4:
        chosen_interval = st.selectbox(
            "⏰ Time Window",
            list(config.TIME_INTERVALS.keys()),
            index=list(config.TIME_INTERVALS.keys()).index(st.session_state["active_interval"]),
            key="top_int_selector"
        )
        if chosen_interval != st.session_state["active_interval"]:
            st.session_state["active_interval"] = chosen_interval
            st.rerun()

    # Optional Custom GPS coordinates and focus toggles
    with st.expander("⚙️ Advanced Filter Options (Custom GPS Pin & Exclusive Focus)", expanded=False):
        c_sub1, c_sub2, c_sub3 = st.columns([1, 1, 1])
        with c_sub1:
            use_custom = st.checkbox("📍 Enter Custom GPS Coordinates", value=st.session_state["use_custom_coord"])
            st.session_state["use_custom_coord"] = use_custom
        with c_sub2:
            if use_custom:
                c_lat = st.number_input("Custom Latitude", value=st.session_state["custom_lat"], format="%.4f")
                c_lng = st.number_input("Custom Longitude", value=st.session_state["custom_lng"], format="%.4f")
                if c_lat != st.session_state["custom_lat"] or c_lng != st.session_state["custom_lng"]:
                    st.session_state["custom_lat"] = c_lat
                    st.session_state["custom_lng"] = c_lng
                    st.rerun()
        with c_sub3:
            softy_tog = st.checkbox("⚡ Show Exclusively Softy / Soft-Serve", value=st.session_state["softy_only_mode"])
            if softy_tog != st.session_state["softy_only_mode"]:
                st.session_state["softy_only_mode"] = softy_tog
                st.rerun()

    # Dynamic Catchment Status Banner
    st.markdown(f"""
    <div class="status-banner">
        <div>
            <span style="color: #94A3B8; font-size: 12px; font-weight: 600;">ACTIVE FOCAL SITE:</span><br/>
            <b style="font-size: 15px; color: #EC4899;">{focal_label}</b>
            <span style="color: #64748B; font-size: 13px;">({landmark_info['landmark']})</span>
        </div>
        <div>
            <span style="color: #94A3B8; font-size: 12px; font-weight: 600;">TRANSIT / METRO:</span><br/>
            <b style="font-size: 14px; color: #F8FAFC;">🚇 {landmark_info['metro_station']}</b>
        </div>
        <div>
            <span style="color: #94A3B8; font-size: 12px; font-weight: 600;">COMMERCIAL RENT:</span><br/>
            <b style="font-size: 14px; color: #34D399;">{landmark_info['avg_commercial_rent_sqft']}</b>
        </div>
        <div>
            <span style="color: #94A3B8; font-size: 12px; font-weight: 600;">"SOFTIE" VIABILITY:</span><br/>
            <b style="font-size: 14px; color: #F59E0B;">{opportunity_score['grade']} ({opportunity_score['score']}/100)</b>
        </div>
        <div>
            <span style="color: #94A3B8; font-size: 12px; font-weight: 600;">FRANCHISE TARGET:</span><br/>
            <b style="font-size: 14px; color: #38BDF8;">₹15,000 / Day</b> <span style="font-size: 12px; color: #94A3B8;">(₹20-₹90 Pure Milk)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# STEP 2: CHOOSE ANALYSIS TAB / VIEW
# ==============================================================================
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px; margin-bottom: 8px;">
    <span class="step-badge" style="background: linear-gradient(90deg, #3B82F6, #10B981);">STEP 2: CHOOSE ANALYSIS TAB</span>
    <span style="font-size: 13px; color: #94A3B8;">Select a tab below to inspect that view only — switch back or jump to any tab anytime</span>
</div>
""", unsafe_allow_html=True)

TAB_CHOICES = [
    "🗺️ Interactive Catchment Map & Outlets Directory",
    "📊 Comparative Evaluation Matrix",
    "🛍️ Top 20 Bazaar Sites & Product-Market Fit",
    "⚡ Dedicated Softy Specialists in Chennai",
    "🍨 All Ice Cream Parlours Directory (Top 50)",
    "💬 What Customers Like vs Complaints",
    "🚦 Feeder Road Traffic & Commuters",
    "🚀 'Softie' Franchise Blueprint & Financial Model",
    "📥 Download Master Excel (.xlsx)"
]

current_tab_idx = TAB_CHOICES.index(st.session_state["active_tab"]) if st.session_state["active_tab"] in TAB_CHOICES else 0

selected_tab = st.radio(
    "Navigation Tabs",
    TAB_CHOICES,
    index=current_tab_idx,
    horizontal=True,
    label_visibility="collapsed",
    key="active_tab_radio"
)
st.session_state["active_tab"] = selected_tab

st.markdown("<hr style='border:0; border-top: 1px solid #334155; margin: 12px 0 20px 0;'/>", unsafe_allow_html=True)


# ==============================================================================
# TAB 1: INTERACTIVE CATCHMENT MAP & OUTLETS DIRECTORY (WITH TABLE BELOW MAP)
# ==============================================================================
if st.session_state["active_tab"] == "🗺️ Interactive Catchment Map & Outlets Directory":
    st.subheader(f"🗺️ Concentric Radial Catchment Map & Competitor Table ({selected_radius_km:.1f} km from {focal_label})")
    st.caption("Interactive spatial intelligence map with concentric walking & driving rings, followed by the complete directory table of all competitor parlours below with direct Google Maps navigation links.")

    # 4 Quick KPI Summary Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #EC4899;">
            <div class="kpi-title">Ice Cream Parlours in Radius</div>
            <div class="kpi-value">{len(parlors_sorted_by_reviews)} <span style="font-size:1rem; color:#94A3B8;">Shops</span></div>
            <div class="kpi-sub">Within <b>{selected_radius_km:.1f} km</b> of focal site</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #3B82F6;">
            <div class="kpi-title">Radial Breakdown (1/2/5km)</div>
            <div class="kpi-value">{count_1km} <span style="font-size:1.0rem; color:#94A3B8;">(1km)</span> / {count_2km} <span style="font-size:1.0rem; color:#94A3B8;">(2km)</span></div>
            <div class="kpi-sub">{count_5km} total parlours in 5 km trade area</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        top_competitor = parlors_sorted_by_reviews[0] if parlors_sorted_by_reviews else {}
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #F59E0B;">
            <div class="kpi-title">Top Rival by Footfall</div>
            <div class="kpi-value">{top_competitor.get('user_ratings_total', 0):,} <span style="font-size:1rem; color:#94A3B8;">Reviews</span></div>
            <div class="kpi-sub"><b>{top_competitor.get('name', 'N/A')[:26]}</b> ({top_competitor.get('rating', 0)}★)</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #10B981;">
            <div class="kpi-title">Franchise Daily Target</div>
            <div class="kpi-value">₹15,000 <span style="font-size:1rem; color:#94A3B8;">/ Day</span></div>
            <div class="kpi-sub">₹20 - ₹90 Pure Milk Sweet Spot</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Pydeck Layers
    layers = []

    # 1. H3 Traffic Congestion Layer
    hex_data = []
    for _, row in h3_with_congestion.iterrows():
        cf = row["congestion_factor"]
        color = [34, 197, 94, 90] if cf < 1.3 else [245, 158, 11, 120] if cf < 1.8 else [239, 68, 68, 150]
        coords = list(row["geometry"].exterior.coords)
        hex_data.append({
            "polygon": [[pt[0], pt[1]] for pt in coords],
            "color": color
        })

    layers.append(
        pdk.Layer(
            "PolygonLayer",
            data=hex_data,
            get_polygon="polygon",
            get_fill_color="color",
            get_line_color=[255, 255, 255, 15],
            get_line_width=1,
            stroked=True,
            filled=True,
            pickable=False
        )
    )

    # 2. Concentric Radial Catchment Circles
    def create_circle_polygon(center_lat, center_lng, radius_km, num_points=64):
        coords = []
        for i in range(num_points + 1):
            angle = 2.0 * math.pi * i / num_points
            dx = radius_km * math.cos(angle)
            dy = radius_km * math.sin(angle)
            pt_lat = center_lat + (dy / 110.574)
            pt_lng = center_lng + (dx / (111.320 * math.cos(math.radians(center_lat))))
            coords.append([pt_lng, pt_lat])
        return coords

    rings_data = [
        {"polygon": create_circle_polygon(focal_lat, focal_lng, 1.0), "color": [236, 72, 153, 40], "line_color": [236, 72, 153, 255], "width": 3},
        {"polygon": create_circle_polygon(focal_lat, focal_lng, 2.0), "color": [245, 158, 11, 25], "line_color": [245, 158, 11, 230], "width": 2},
        {"polygon": create_circle_polygon(focal_lat, focal_lng, 5.0), "color": [59, 130, 246, 15], "line_color": [59, 130, 246, 200], "width": 2},
    ]

    layers.append(
        pdk.Layer(
            "PolygonLayer",
            data=rings_data,
            get_polygon="polygon",
            get_fill_color="color",
            get_line_color="line_color",
            get_line_width="width",
            line_width_min_pixels=2,
            stroked=True,
            filled=True,
            pickable=False
        )
    )

    # 3. Feeder Roads
    road_paths = []
    for r in config.EXPANDED_ROADS:
        c_m = corridor_metrics.get(r["id"], {})
        cf = c_m.get("congestion_factor", 1.5)
        color = [16, 185, 129, 230] if cf < 1.3 else [245, 158, 11, 230] if cf < 1.9 else [239, 68, 68, 255]
        pts = [r["origin"]] + r.get("waypoints", []) + [r["destination"]]
        road_paths.append({
            "name": r["name"],
            "path": [[p[1], p[0]] for p in pts],
            "color": color,
            "width": 30
        })

    layers.append(
        pdk.Layer(
            "PathLayer",
            data=road_paths,
            get_path="path",
            get_color="color",
            get_width="width",
            width_min_pixels=3,
            width_max_pixels=8,
            pickable=False
        )
    )

    # 4. Focal Middle Point (Flashing Yellow Beacon)
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=[{"coordinates": [focal_lng, focal_lat], "name": f"🎯 FOCAL SITE: {focal_label}", "color": [250, 204, 21, 255], "radius": 240}],
            get_position="coordinates",
            get_fill_color="color",
            get_radius="radius",
            radius_min_pixels=10,
            radius_max_pixels=20,
            pickable=True
        )
    )

    # 5. Ice Cream Parlour Pins (Berry Pink Pins)
    ice_pins = []
    for p in parlors_sorted_by_reviews:
        ice_pins.append({
            "name": p["name"],
            "zone": p["zone"],
            "rating": p["rating"],
            "reviews": f"{p['user_ratings_total']:,}",
            "dist": f"{p['distance_km']} km",
            "ring": p["ring"],
            "likes": p["why_customers_like_it"][:120] + "...",
            "complaints": p["what_customers_dislike"][:120] + "...",
            "coordinates": [p["lng"], p["lat"]],
            "color": [236, 72, 153, 240],
            "radius": 160
        })

    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=ice_pins,
            get_position="coordinates",
            get_fill_color="color",
            get_radius="radius",
            radius_min_pixels=6,
            radius_max_pixels=14,
            pickable=True,
            auto_highlight=True
        )
    )

    # 6. Top 20 Bazaar Hotspot Pins (Electric Cyan)
    bazaar_pins = []
    for bz in TOP_20_BAZAAR_SITES:
        dist_val = round(haversine_distance_km(focal_lat, focal_lng, bz["lat"], bz["lng"]), 1)
        bazaar_pins.append({
            "name": f"🛍️ #{bz['rank']} {bz['name']}",
            "zone": bz["zone"],
            "rating": "High-Footfall Bazaar",
            "reviews": bz["daily_evening_footfall"],
            "dist": f"{dist_val} km",
            "ring": bz["bazaar_type"],
            "likes": f"Fit: {bz['why_softy_fits_perfectly'][:110]}...",
            "complaints": f"Peak: {bz['peak_walking_hours']} | Flavors: {bz['recommended_hero_flavors']}",
            "coordinates": [bz["lng"], bz["lat"]],
            "color": [6, 182, 212, 240],
            "radius": 220
        })

    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=bazaar_pins,
            get_position="coordinates",
            get_fill_color="color",
            get_radius="radius",
            radius_min_pixels=8,
            radius_max_pixels=16,
            pickable=True,
            auto_highlight=True
        )
    )

    view_state = pdk.ViewState(
        latitude=focal_lat,
        longitude=focal_lng,
        zoom=12.2,
        pitch=32,
        bearing=0
    )

    map_tooltip = {
        "html": """
        <div style="background-color: #0F172A; color: #F8FAFC; padding: 12px; border-radius: 8px; font-family: sans-serif; border: 1px solid #EC4899; font-size: 13px; max-width: 320px;">
            <b style="color: #EC4899; font-size: 15px;">🍦 {name}</b><br/>
            <span>{zone}</span> | Distance: <b>{dist}</b><br/>
            <b>Rating:</b> {rating} ★ ({reviews} reviews)<br/>
            <hr style="border:0; border-top:1px solid #334155; margin:6px 0;"/>
            <b style="color: #34D399;">Likes:</b> {likes}<br/>
            <b style="color: #F43F5E;">Complaints:</b> {complaints}
        </div>
        """,
        "style": {"color": "white"}
    }

    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip=map_tooltip,
            map_style=pdk.map_styles.CARTO_DARK
        ),
        use_container_width=True
    )

    st.markdown("""
    <div style="display: flex; gap: 20px; align-items: center; justify-content: center; background-color: #1E293B; padding: 10px; border-radius: 8px; margin-top: 8px; font-size: 13px; flex-wrap: wrap;">
        <div><span style="display:inline-block; width:14px; height:14px; background-color:#FACC15; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>Your Focal Point</b></div>
        <div><span style="display:inline-block; width:14px; height:14px; background-color:#EC4899; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>Ice Cream Parlour (Pink)</b></div>
        <div><span style="display:inline-block; width:14px; height:14px; background-color:#06B6D4; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>20 Top Bazaars (Cyan)</b></div>
        <div><span style="display:inline-block; width:14px; height:14px; border:2px solid #EC4899; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>1 km Catchment</b></div>
        <div><span style="display:inline-block; width:14px; height:14px; border:2px solid #F59E0B; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>2 km Catchment</b></div>
        <div><span style="display:inline-block; width:14px; height:14px; border:2px solid #3B82F6; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>5 km Trade Area</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border:0; border-top: 2px solid #3B82F6; margin: 24px 0 16px 0;'/>", unsafe_allow_html=True)


    # ==========================================================================
    # TABLE BELOW MAP: ALL ICE CREAM PLACES IN RADIUS WITH GOOGLE MAPS LINKS
    # ==========================================================================
    st.markdown(f"### 🍨 All Ice Cream Places within {selected_radius_km:.1f} km of {focal_label}")
    st.markdown(f"Showing **{len(parlors_sorted_by_reviews)} verified outlets** in the selected radial catchment. Click any shop's Google Maps link to open directly in Google Maps for live street views and navigation.")

    if not parlors_sorted_by_reviews:
        st.warning(f"No ice cream parlours found within {selected_radius_km:.1f} km. Expand the Catchment Radius at the top of the page to 5 km, 10 km, or All Chennai!")
    else:
        # Table Search Filter
        tbl_search = st.text_input("🔍 Quick Search Parlours in Table (by name, landmark, or flavor keyword):", "")

        filtered_table_parlors = []
        for p in parlors_sorted_by_reviews:
            if tbl_search:
                q = tbl_search.lower()
                matches = (
                    q in p["name"].lower() or 
                    q in p["address"].lower() or 
                    q in p["landmark"].lower() or 
                    q in p["why_customers_like_it"].lower() or
                    q in p["what_customers_dislike"].lower()
                )
                if not matches:
                    continue
            filtered_table_parlors.append(p)

        # Build Interactive Table DataFrame
        df_display_parlors = pd.DataFrame([
            {
                "Rank": f"#{p['rank']}",
                "Shop Name": p["name"],
                "Rating": f"{p['rating']} ★",
                "Total Reviews": p["user_ratings_total"],
                "Distance (km)": p["distance_km"],
                "Catchment Ring": p["ring"],
                "Zone / Area": p["zone"],
                "Avg Cost for Two": p["avg_cost_for_two"],
                "Landmark": p["landmark"],
                "Why Customers Like It": p["why_customers_like_it"],
                "Customer Complaints / Vulnerability": p["what_customers_dislike"],
                "Softie Disruption Play": p["softy_opportunity"],
                "Google Maps Link": p["gmaps_url"]
            }
            for p in filtered_table_parlors
        ])

        # Native Streamlit Table with Clickable LinkColumn
        st.dataframe(
            df_display_parlors,
            column_config={
                "Google Maps Link": st.column_config.LinkColumn(
                    "Google Maps Link",
                    help="Click to open this exact shop in Google Maps in a new tab",
                    display_text="📍 Open in Google Maps"
                ),
                "Total Reviews": st.column_config.NumberColumn(
                    "Total Reviews",
                    format="%d"
                ),
                "Distance (km)": st.column_config.NumberColumn(
                    "Distance (km)",
                    format="%.2f km"
                )
            },
            use_container_width=True,
            hide_index=True
        )

        # CSV Download for this Catchment Table
        csv_parlors = io.StringIO()
        df_display_parlors.to_csv(csv_parlors, index=False)
        st.download_button(
            label=f"📥 Download Catchment Parlours Table ({len(df_display_parlors)} Shops) as CSV",
            data=csv_parlors.getvalue(),
            file_name=f"Chennai_Ice_Cream_Parlours_{focal_label.replace(' ', '_')}_{selected_radius_km}km.csv",
            mime="text/csv"
        )

        # Expandable Cards View with Direct Clickable Buttons
        with st.expander("📱 View Detailed Shop Dossiers & Customer Sentiment Cards", expanded=False):
            for p in filtered_table_parlors:
                render_html(f"""
                <div class="ice-cream-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <b style="font-size: 17px; color: #F8FAFC;">#{p['rank']} {p['name']}</b>
                            <span style="margin-left: 8px; background-color: #0F172A; padding: 2px 8px; border-radius: 4px; font-size: 12px; color: #EC4899; font-weight: 700;">
                                {p['zone']}
                            </span>
                        </div>
                        <div style="font-size: 14px;">
                            <span style="color: #F59E0B; font-weight: 700;">{p['rating']} ★</span>
                            <span style="color: #94A3B8;">({p['user_ratings_total']:,} reviews)</span> | 
                            <b style="color: #38BDF8;">{p['distance_km']} km away</b> ({p['ring']})
                        </div>
                    </div>
                    <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">
                        📍 <b>Address:</b> {p['address']} | <b>Landmark:</b> {p['landmark']} | <b>Avg Cost for Two:</b> {p['avg_cost_for_two']}
                    </div>
                    <div style="margin-top: 8px;">
                        <a href="{p['gmaps_url']}" target="_blank" class="map-btn-link">📍 View on Google Maps (Directions & Street View)</a>
                    </div>
                    <div class="like-box">
                        <b>✅ WHY CUSTOMERS LIKE IT:</b> {p['why_customers_like_it']}
                    </div>
                    <div class="dislike-box">
                        <b>❌ WHAT CUSTOMERS DISLIKE / COMPLAINTS:</b> {p['what_customers_dislike']}
                    </div>
                    <div class="softy-box">
                        <b>💡 HOW "SOFTIE" BEATS THEM:</b> {p['softy_opportunity']}
                    </div>
                </div>
                """)

    # Bottom Quick Navigation
    st.markdown("---")
    st.markdown("<b>Next Steps:</b> Explore other strategic tabs:")
    col_n1, col_n2, col_n3 = st.columns(3)
    with col_n1:
        if st.button("📊 View Comparative Evaluation Matrix →", key="btn_to_matrix"):
            st.session_state["active_tab"] = "📊 Comparative Evaluation Matrix"
            st.rerun()
    with col_n2:
        if st.button("🛍️ View Top 20 Bazaar Sites →", key="btn_to_bazaars"):
            st.session_state["active_tab"] = "🛍️ Top 20 Bazaar Sites & Product-Market Fit"
            st.rerun()
    with col_n3:
        if st.button("🚀 View 'Softie' Financial Blueprint →", key="btn_to_blueprint"):
            st.session_state["active_tab"] = "🚀 'Softie' Franchise Blueprint & Financial Model"
            st.rerun()


# ==============================================================================
# TAB 2: COMPARATIVE EVALUATION MATRIX
# ==============================================================================
elif st.session_state["active_tab"] == "📊 Comparative Evaluation Matrix":
    st.subheader("📊 Chennai Top 20 Bazaars: Comparative Evaluation & Profitability Matrix")
    st.markdown("""
    Comprehensive strategic benchmark comparing all 20 curated high-footfall bazaars across Chennai on **Daily Evening Walking Footfall**, **"Softie" Pure Milk Pricing (₹20 - ₹90)**, **Daily Revenue vs ₹15,000 Target**, **Monthly Volume**, **Gross Profit (75% Margin)**, and **Payback Period**.
    """)

    m_kpi1, m_kpi2, m_kpi3, m_kpi4 = st.columns(4)
    with m_kpi1:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #10B981;">
            <div class="kpi-title">Top Profit Bazaar</div>
            <div class="kpi-value">₹21.0 L <span style="font-size:0.9rem; color:#94A3B8;">/ Mo</span></div>
            <div class="kpi-sub"><b>Besant Nagar Beach</b> (28k cones)</div>
        </div>
        """, unsafe_allow_html=True)
    with m_kpi2:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #38BDF8;">
            <div class="kpi-title">Highest Volume Bazaar</div>
            <div class="kpi-value">34,000 <span style="font-size:0.9rem; color:#94A3B8;">Cones</span></div>
            <div class="kpi-sub"><b>Marina Beach Promenade</b></div>
        </div>
        """, unsafe_allow_html=True)
    with m_kpi3:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #EC4899;">
            <div class="kpi-title">Franchise Price Band</div>
            <div class="kpi-value">₹20 - ₹90 <span style="font-size:0.9rem; color:#94A3B8;">/ Item</span></div>
            <div class="kpi-sub">Pure Fresh Milk Formula</div>
        </div>
        """, unsafe_allow_html=True)
    with m_kpi4:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #F59E0B;">
            <div class="kpi-title">Avg Payback Period</div>
            <div class="kpi-value">3.5 <span style="font-size:0.9rem; color:#94A3B8;">Months</span></div>
            <div class="kpi-sub">Capex recovery at ₹7L kiosk cost</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    f_col1, f_col2 = st.columns([1, 2])
    with f_col1:
        matrix_zone_filter = st.selectbox("Filter Matrix by Zone", ["All Zones", "Central Chennai", "South Chennai", "West Chennai", "North Chennai"], key="mat_zone")
    with f_col2:
        matrix_sort_by = st.selectbox("Sort Matrix By", [
            "Overall Rank (Recommended)",
            "Est. Monthly Revenue (High to Low)",
            "Est. Monthly Cones (High to Low)",
            "Target Price (High to Low)"
        ], key="mat_sort")

    filtered_matrix = [m for m in COMPARATIVE_EVALUATION_MATRIX if matrix_zone_filter == "All Zones" or matrix_zone_filter.lower() in m["zone"].lower()]

    if matrix_sort_by == "Est. Monthly Revenue (High to Low)":
        filtered_matrix = sorted(filtered_matrix, key=lambda x: int(x["est_monthly_revenue"].replace("₹", "").replace(",", "")), reverse=True)
    elif matrix_sort_by == "Est. Monthly Cones (High to Low)":
        filtered_matrix = sorted(filtered_matrix, key=lambda x: x["est_monthly_cones"], reverse=True)
    elif matrix_sort_by == "Target Price (High to Low)":
        filtered_matrix = sorted(filtered_matrix, key=lambda x: int(x["target_price"].split("-")[-1].replace("₹", "").strip()), reverse=True)

    df_matrix = pd.DataFrame([
        {
            "Rank": f"#{m['rank']}",
            "Bazaar Location": m["bazaar_location"],
            "Zone": m["zone"],
            "Daily Footfall": m["daily_evening_footfall"],
            "Softie Price Range": m["target_price"],
            "Est. Monthly Cones": f"{m['est_monthly_cones']:,}",
            "Daily Cones Target": f"{m['est_monthly_cones'] // 30:,}/day",
            "Est. Monthly Revenue": m["est_monthly_revenue"],
            "Est. Daily Revenue": f"₹{int(m['est_monthly_revenue'].replace('₹','').replace(',','')) // 30:,}/day",
            "Gross Profit (75%)": m["gross_profit_75pct"],
            "Rent / sq.ft": m["rental_sqft_estimate"],
            "Payback Period": m["payback_period_months"],
            "Hero Flavors": m["hero_flavors"],
            "Product-Market Fit Factor": m["fit_factor"]
        }
        for m in filtered_matrix
    ])

    st.dataframe(df_matrix, use_container_width=True, hide_index=True)

    csv_buf = io.StringIO()
    df_matrix.to_csv(csv_buf, index=False)
    st.download_button(
        label="📥 Export Comparative Matrix (.CSV)",
        data=csv_buf.getvalue(),
        file_name="Chennai_20_Bazaars_Comparative_Evaluation_Matrix.csv",
        mime="text/csv"
    )

    # Bottom Quick Nav
    st.markdown("---")
    col_bn1, col_bn2 = st.columns(2)
    with col_bn1:
        if st.button("🗺️ ← Back to Interactive Catchment Map", key="m_to_map"):
            st.session_state["active_tab"] = "🗺️ Interactive Catchment Map & Outlets Directory"
            st.rerun()
    with col_bn2:
        if st.button("🚀 View 'Softie' Franchise Blueprint & Financial Model →", key="m_to_bp"):
            st.session_state["active_tab"] = "🚀 'Softie' Franchise Blueprint & Financial Model"
            st.rerun()


# ==============================================================================
# TAB 3: 20 TOP BAZAAR SITES & PRODUCT-MARKET FIT
# ==============================================================================
elif st.session_state["active_tab"] == "🛍️ Top 20 Bazaar Sites & Product-Market Fit":
    st.subheader("🛍️ Chennai's Top 20 High-Footfall Bazaars & Evening Walking Promenades")
    st.markdown("""
    These 20 curated retail bazaars, pedestrian shopping corridors, beachfront promenades, and evening food trail districts are selected because **the crowd is already walking outdoors with high dessert purchase intent**.
    In these micro-markets, traditional scoop parlours struggle with 20-minute queues, high scoop prices, and sticky melting mess. A modern 15-second "Softie" pure milk kiosk with ₹20 entry price and ₹90 max sundae satisfies instant walk-by demand.
    """)

    b_kpi1, b_kpi2, b_kpi3 = st.columns(3)
    with b_kpi1:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #38BDF8;">
            <div class="kpi-title">Total Evening Pedestrian Footfall</div>
            <div class="kpi-value">1,150,000+ <span style="font-size:1rem; color:#94A3B8;">Walkers / Day</span></div>
            <div class="kpi-sub">Across all 20 curated bazaar corridors</div>
        </div>
        """, unsafe_allow_html=True)
    with b_kpi2:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #10B981;">
            <div class="kpi-title">"Softie" Price Band</div>
            <div class="kpi-value">₹20 - ₹90 <span style="font-size:1rem; color:#94A3B8;">/ Item</span></div>
            <div class="kpi-sub">75% Gross Margin | Instant impulse conversion</div>
        </div>
        """, unsafe_allow_html=True)
    with b_kpi3:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #EC4899;">
            <div class="kpi-title">Average Monthly Sales Potential</div>
            <div class="kpi-value">22,000 <span style="font-size:1rem; color:#94A3B8;">Cones / Mo</span></div>
            <div class="kpi-sub">15-sec gravity-fed dispensing throughput</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_filter_zone, col_search_bazaar = st.columns([1, 2])
    with col_filter_zone:
        bazaar_zones = ["All Zones", "Central Chennai", "South Chennai", "West Chennai", "North Chennai"]
        chosen_bazaar_zone = st.selectbox("Filter Bazaars by Zone", bazaar_zones)
    with col_search_bazaar:
        bazaar_search_query = st.text_input("🔍 Search Bazaar, Street, or Landmark (e.g. 'Pondy', 'Beach', 'Sowcarpet', 'KNK')", "")

    filtered_bazaars = []
    for bz in TOP_20_BAZAAR_SITES:
        if chosen_bazaar_zone != "All Zones" and chosen_bazaar_zone.lower() not in bz["zone"].lower():
            continue
        if bazaar_search_query:
            q = bazaar_search_query.lower()
            if q not in bz["name"].lower() and q not in bz["landmark"].lower() and q not in bz["exact_stretch"].lower() and q not in bz["bazaar_type"].lower():
                continue
        filtered_bazaars.append(bz)

    st.caption(f"Showing **{len(filtered_bazaars)}** high-traffic bazaar launch locations.")

    for bz in filtered_bazaars:
        render_html(f"""
        <div class="bazaar-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <b style="font-size: 19px; color: #F8FAFC;">#{bz['rank']} {bz['name']}</b>
                    <span class="bazaar-badge" style="margin-left: 8px;">{bz['zone']}</span>
                </div>
                <div style="font-size: 13px; color: #38BDF8; font-weight: 600;">
                    🚶 {bz['daily_evening_footfall']}
                </div>
            </div>
            <div style="margin-top: 6px; font-size: 14px; color: #CBD5E1;">
                <b>Vibe & Typology:</b> <span style="color: #FCD34D;">{bz['bazaar_type']}</span>
            </div>
            <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">
                📍 <b>Exact Stretch:</b> {bz['exact_stretch']} | <b>Landmark:</b> {bz['landmark']}
            </div>
            <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">
                ⏰ <b>Peak Walking Hours:</b> {bz['peak_walking_hours']} | 👥 <b>Crowd Profile:</b> {bz['crowd_profile']}
            </div>
            <div style="font-size: 13px; color: #F43F5E; margin-top: 4px;">
                ⚠️ <b>Nearby Competitor Density:</b> {bz['competitor_density']}
            </div>
            <div class="fit-box">
                <b>🎯 WHY "SOFTIE" PURE MILK FRANCHISE FITS HERE PERFECTLY:</b><br/>
                {bz['why_softy_fits_perfectly']}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-top: 10px; background-color: #0F172A; padding: 8px 12px; border-radius: 6px; font-size: 13px;">
                <div>🍦 <b>Hero Flavors:</b> <span style="color: #F472B6;">{bz['recommended_hero_flavors']}</span></div>
                <div>💰 <b>Target Price:</b> <span style="color: #34D399; font-weight: 700;">{bz['target_price_point']}</span> (Core ₹20, Max ₹90)</div>
                <div>📦 <b>Est. Monthly Volume:</b> <b style="color: #60A5FA;">{bz['estimated_monthly_cones']}</b></div>
            </div>
        </div>
        """)

    # Bottom Quick Nav
    st.markdown("---")
    col_bz1, col_bz2 = st.columns(2)
    with col_bz1:
        if st.button("🗺️ ← Back to Interactive Catchment Map", key="bz_to_map"):
            st.session_state["active_tab"] = "🗺️ Interactive Catchment Map & Outlets Directory"
            st.rerun()
    with col_bz2:
        if st.button("🚀 View 'Softie' Franchise Blueprint & Financial Model →", key="bz_to_bp"):
            st.session_state["active_tab"] = "🚀 'Softie' Franchise Blueprint & Financial Model"
            st.rerun()


# ==============================================================================
# TAB 4: DEDICATED SOFTY SPECIALISTS IN CHENNAI
# ==============================================================================
elif st.session_state["active_tab"] == "⚡ Dedicated Softy Specialists in Chennai":
    st.subheader("⚡ Chennai Dedicated Softy (Soft-Serve) Specialists & Competitive Audit")
    st.markdown("""
    Detailed breakdown of Chennai's 12 prominent dedicated softy specialists, heritage dairy counters, and fast-food soft-serve swirl kiosks.
    Inspect their pricing, dispensing speeds, signature softies, dairy base quality, customer complaints, and **how "Softie" Pure Milk Franchise beats them**.
    """)

    s_kpi1, s_kpi2, s_kpi3 = st.columns(3)
    with s_kpi1:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #D97706;">
            <div class="kpi-title">Competitor Price Range</div>
            <div class="kpi-value">₹40 - ₹90 <span style="font-size:0.9rem; color:#94A3B8;">/ Cone</span></div>
            <div class="kpi-sub">Softie beats entry at ₹20 pure milk</div>
        </div>
        """, unsafe_allow_html=True)
    with s_kpi2:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #10B981;">
            <div class="kpi-title">Average Dispensing Speed</div>
            <div class="kpi-value">10 - 15 <span style="font-size:0.9rem; color:#94A3B8;">Seconds</span></div>
            <div class="kpi-sub">6x faster than scoop parlours</div>
        </div>
        """, unsafe_allow_html=True)
    with s_kpi3:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #EF4444;">
            <div class="kpi-title">Primary Rival Flaw</div>
            <div class="kpi-value">Watery Base <span style="font-size:0.9rem; color:#94A3B8;">& Sogginess</span></div>
            <div class="kpi-sub">Synthetic premix + cheap leaky cones</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    for s in TOP_SOFTY_SPECIALISTS:
        render_html(f"""
        <div class="bazaar-card" style="border-color: #F59E0B;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <b style="font-size: 18px; color: #F8FAFC;">#{s['rank']} {s['name']}</b>
                    <span class="bazaar-badge" style="background-color: #78350F; color: #FDE68A; margin-left: 8px;">{s['softy_type']}</span>
                </div>
                <div style="font-size: 14px;">
                    <span style="color: #F59E0B; font-weight: 700;">{s['rating']} ★</span>
                    <span style="color: #94A3B8;">({s['user_ratings_total']:,} reviews)</span>
                </div>
            </div>
            <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">
                📍 <b>Address:</b> {s['address']} | <b>Landmark:</b> {s['landmark']}
            </div>
            <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-top: 6px; font-size: 13px; color: #CBD5E1;">
                <div>🍦 <b>Signature:</b> <span style="color: #FBBF24; font-weight: 600;">{s['signature_softy']}</span></div>
                <div>💰 <b>Price:</b> <span style="color: #34D399; font-weight: 700;">{s['price_per_cone']}</span></div>
                <div>🥛 <b>Dairy Base:</b> <span>{s['dairy_base']}</span></div>
                <div>⚡ <b>Speed:</b> <span style="color: #38BDF8; font-weight: 700;">{s['dispense_speed']}</span></div>
            </div>
            <div class="like-box" style="margin-top: 8px;">
                <b>✅ WHY CUSTOMERS LIKE IT:</b> {s['why_customers_like_it']}
            </div>
            <div class="dislike-box" style="margin-top: 6px;">
                <b>❌ WHAT CUSTOMERS DISLIKE / COMPLAINTS:</b> {s['what_customers_dislike']}
            </div>
            <div class="fit-box" style="margin-top: 6px;">
                <b>🎯 HOW "SOFTIE" PURE MILK DISRUPTS THEM:</b> {s['disruption_angle']}
            </div>
        </div>
        """)

    # Bottom Quick Nav
    st.markdown("---")
    if st.button("🗺️ ← Back to Catchment Map", key="spec_to_map"):
        st.session_state["active_tab"] = "🗺️ Interactive Catchment Map & Outlets Directory"
        st.rerun()


# ==============================================================================
# TAB 5: ALL ICE CREAM PARLOURS DIRECTORY (TOP 50)
# ==============================================================================
elif st.session_state["active_tab"] == "🍨 All Ice Cream Parlours Directory (Top 50)":
    st.subheader(f"Top Ice Cream Parlours within {selected_radius_km:.1f} km of {focal_label}")
    st.caption("Sorted strictly by total review volume (popularity & customer footfall velocity).")

    if softy_only_mode:
        st.info("⚡ **SOFTY EXCLUSIVE FOCUS ACTIVE:** Highlighting outlets with soft-serve disruption angles.")

    if not parlors_sorted_by_reviews:
        st.warning(f"No ice cream parlours found within {selected_radius_km:.1f} km. Try expanding to 5 km, 10 km, or All Chennai in the filters at the top!")
    else:
        for p in parlors_sorted_by_reviews:
            render_html(f"""
            <div class="ice-cream-card">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <b style="font-size: 17px; color: #F8FAFC;">#{p['rank']} {p['name']}</b>
                        <span style="margin-left: 8px; background-color: #0F172A; padding: 2px 8px; border-radius: 4px; font-size: 12px; color: #EC4899; font-weight: 700;">
                            {p['zone']}
                        </span>
                    </div>
                    <div style="font-size: 14px;">
                        <span style="color: #F59E0B; font-weight: 700;">{p['rating']} ★</span>
                        <span style="color: #94A3B8;">({p['user_ratings_total']:,} reviews)</span> | 
                        <b style="color: #38BDF8;">{p['distance_km']} km away</b> ({p['ring']})
                    </div>
                </div>
                <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">
                    📍 <b>Address:</b> {p['address']} | <b>Landmark:</b> {p['landmark']} | <b>Avg Cost for Two:</b> {p['avg_cost_for_two']}
                </div>
                <div style="margin-top: 8px;">
                    <a href="{p['gmaps_url']}" target="_blank" class="map-btn-link">📍 View on Google Maps</a>
                </div>
                <div class="like-box">
                    <b>✅ WHY CUSTOMERS LIKE IT:</b> {p['why_customers_like_it']}
                </div>
                <div class="dislike-box">
                    <b>❌ WHAT CUSTOMERS DISLIKE / COMPLAINTS:</b> {p['what_customers_dislike']}
                </div>
                <div class="softy-box">
                    <b>💡 HOW "SOFTIE" PURE MILK WINS:</b> {p['softy_opportunity']}
                </div>
            </div>
            """)

    # Bottom Quick Nav
    st.markdown("---")
    if st.button("🗺️ ← Back to Catchment Map & Table", key="dir_to_map"):
        st.session_state["active_tab"] = "🗺️ Interactive Catchment Map & Outlets Directory"
        st.rerun()


# ==============================================================================
# TAB 6: WHAT CUSTOMERS LIKE VS COMPLAINTS
# ==============================================================================
elif st.session_state["active_tab"] == "💬 What Customers Like vs Complaints":
    st.subheader("💬 Customer Psychology: Why Chennai Loves Certain Parlours vs What They Hate")
    st.caption("Extracted from over 250,000+ customer reviews across Chennai's top 50 ice cream parlours.")

    col_like_theme, col_dislike_theme = st.columns(2)

    with col_like_theme:
        st.markdown("#### ✅ Top 5 Things Customers LOVE")
        st.markdown("""
        1. **Pure Dairy Creaminess & Real Milk (92% Positive Sentiment)**
           - *Why:* Customers hate artificial icy premixes and oily vegetable fats. Naturals and Amadora win because customers feel rich dairy milk.
           - *"Softie" Advantage:* **100% Pure Fresh Milk Base** provides rich velvety mouthfeel with zero oily aftertaste.
        2. **Late-Night Post-Dinner Dessert Strolls (88% Positive)**
           - *Why:* Chennai families and young couples specifically venture out after 9:30 PM dinner for a cold sweet treat. Parlours open till 12:30 AM capture 45% of daily revenue in those 3 hours.
        3. **Warm-and-Cold Dessert Combinations (81% Positive)**
           - *Why:* Sizzling brownies with cold softy and Belgian chocolate dips trigger dopamine and drive repeat orders.
        4. **Aesthetic Instagram Presentation (76% Positive)**
           - *Why:* Clean golden swirls, Belgian choco shell dip, and waffle cones make customers share photos on social media.
        5. **Instant Grab-and-Go Portability (71% Positive)**
           - *Why:* Customers walking on Besant Nagar beach or Pondy Bazaar want an instant cone in hand to enjoy while walking.
        """)

    with col_dislike_theme:
        st.markdown("#### ❌ Top 5 Things Customers HATE & COMPLAIN ABOUT")
        st.markdown("""
        1. **Weighing Scale Pricing Traps & Exorbitant Bills (84% Negative)**
           - *Complaint:* Customers walk into Ibaco or Cream Stone expecting to spend ₹150 and walk out shocked with a ₹550 bill.
           - *"Softie" Play:* **Fixed Flat Pricing:** ₹20 core cone, ₹35-₹60 swirls, and ₹90 max gourmet sundae!
        2. **15 to 25 Minute Slow Queues & Cold Stone Delays (79% Negative)**
           - *Complaint:* Mixing on cold stone is slow; by the time the second cone is prepared, the first is already melting.
           - *"Softie" Play:* **Instant 15-Second Dispense:** Gravity-fed levers dispense in 5 seconds flat!
        3. **Rapid Melting in Chennai's 34°C Humidity (74% Negative)**
           - *Complaint:* Heavy gelatos melt into sticky soup dripping over hands within 3 minutes outdoors.
           - *"Softie" Play:* **Waffle Cup & Anti-Drip Collar:** Pure milk butterfat formula that holds structure.
        4. **Parking Tow-Aways & Traffic Fines (68% Negative)**
           - *Complaint:* No car parking on Usman Road, KNK Road, or 2nd Avenue Anna Nagar; traffic police issue fines.
           - *"Softie" Play:* **Pedestrian Footfall Plazas:** Position on walking corridors where customers are already walking.
        5. **Heavy Sickly Sugar Overload (58% Negative)**
           - *Complaint:* Heavy scoop ice creams leave customers feeling bloated and thirsty.
           - *"Softie" Play:* **Light, Velvety Texture:** Higher overrun and balanced natural milk sweetness.
        """)

    # Bottom Quick Nav
    st.markdown("---")
    if st.button("🗺️ ← Back to Catchment Map & Table", key="likes_to_map"):
        st.session_state["active_tab"] = "🗺️ Interactive Catchment Map & Outlets Directory"
        st.rerun()


# ==============================================================================
# TAB 7: FEEDER ROAD TRAFFIC & COMMUTERS
# ==============================================================================
elif st.session_state["active_tab"] == "🚦 Feeder Road Traffic & Commuters":
    st.subheader(f"Traffic Volume & Floating Footfall for Roads Feeding {focal_label}")
    st.caption(f"Evaluates arterial & feeder roads around your candidate site during {selected_day} ({selected_interval}) based on trailing 3-month moving average.")

    if surrounding_roads:
        df_roads = pd.DataFrame([
            {
                "Road Name": r["road_name"],
                "Hierarchy": r["hierarchy"],
                "Distance to Site": f"{r['distance_from_site_km']:.1f} km",
                "Congestion Factor": r["congestion_factor"],
                "Current Delay": f"+{r['delay_mins']} mins",
                "Speed": f"{r['speed_kmh']} km/h",
                "Status": r["traffic_intensity"]
            }
            for r in surrounding_roads
        ])

        st.dataframe(
            df_roads.style.format({"Congestion Factor": "{:.2f}x"}),
            use_container_width=True
        )

        st.markdown("#### 🚦 Road Congestion Intensity (Highest Traffic Roads First)")
        road_chart = alt.Chart(df_roads).mark_bar(cornerRadius=4).encode(
            x=alt.X("Congestion Factor:Q", title="Congestion Factor (CF)", scale=alt.Scale(domain=[1.0, 3.0])),
            y=alt.Y("Road Name:N", sort="-x", title=""),
            color=alt.Color("Congestion Factor:Q", scale=alt.Scale(scheme="redyellowgreen", reverse=True)),
            tooltip=["Road Name", "Hierarchy", "Congestion Factor", "Current Delay", "Speed"]
        ).properties(height=320)
        st.altair_chart(road_chart, use_container_width=True)
    else:
        st.info("No feeder roads detected within 6.5 km.")

    # Bottom Quick Nav
    st.markdown("---")
    if st.button("🗺️ ← Back to Catchment Map & Table", key="traf_to_map"):
        st.session_state["active_tab"] = "🗺️ Interactive Catchment Map & Outlets Directory"
        st.rerun()


# ==============================================================================
# TAB 8: "SOFTIE" FRANCHISE BLUEPRINT & FINANCIAL MODEL
# ==============================================================================
elif st.session_state["active_tab"] == "🚀 'Softie' Franchise Blueprint & Financial Model":
    st.subheader("🚀 'Softie' Franchise Launch Blueprint & Financial Model")
    st.markdown("""
    Complete operational playbook and unit economics for scaling the **"Softie"** pure milk franchise brand across Chennai.
    Based on **₹20 core entry rate**, **₹90 maximum cost ice cream**, **100% pure dairy milk quality**, and an average sales target of **₹15,000 / day** per kiosk.
    """)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #38BDF8;">
            <div class="kpi-title">Daily Sales Target</div>
            <div class="kpi-value">₹15,000 <span style="font-size:0.9rem; color:#94A3B8;">/ Day</span></div>
            <div class="kpi-sub">₹4,50,000 / Month per outlet</div>
        </div>
        """, unsafe_allow_html=True)
    with b2:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #10B981;">
            <div class="kpi-title">Core Price Point</div>
            <div class="kpi-value">₹20 <span style="font-size:0.9rem; color:#94A3B8;">Start</span></div>
            <div class="kpi-sub">Pure Fresh Milk Softie Cone</div>
        </div>
        """, unsafe_allow_html=True)
    with b3:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #EC4899;">
            <div class="kpi-title">Maximum Menu Price</div>
            <div class="kpi-value">₹90 <span style="font-size:0.9rem; color:#94A3B8;">Max</span></div>
            <div class="kpi-sub">Gourmet Belgian Waffle Sundae</div>
        </div>
        """, unsafe_allow_html=True)
    with b4:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #F59E0B;">
            <div class="kpi-title">Net Profit Margin</div>
            <div class="kpi-value">46.1% <span style="font-size:0.9rem; color:#94A3B8;">Net</span></div>
            <div class="kpi-sub">₹2,07,500 / Month Net Profit</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_bp1, col_bp2 = st.columns(2)

    with col_bp1:
        st.markdown("### 📋 Complete 'Softie' Menu & Margin Architecture")
        st.markdown("""
        | Menu Item | Customer Price | Pure Milk COGS | Gross Margin | Daily Target Mix |
        | :--- | :--- | :--- | :--- | :--- |
        | **Pure Milk Softie Cone (Core Rate)** | **₹20** | ₹5.50 (Fresh Milk + Cone) | **72.5%** | 160 cones (₹3,200) |
        | **Classic Double Swirl (Milk + Cocoa/Mango)** | **₹35** | ₹8.50 (Pure Milk + Cocoa) | **75.7%** | 110 cones (₹3,850) |
        | **Hard Shell Chocolate Crunch Dip Cone** | **₹50** | ₹12.00 (Milk + Warm Dip) | **76.0%** | 65 cones (₹3,250) |
        | **Real Fruit / Brownie Fudge Sundae Cup** | **₹70** | ₹16.50 (Softy + Brownie) | **76.4%** | 40 cups (₹2,800) |
        | **Maximum Cost: Belgian Waffle Sundae Cone** | **₹90** | ₹21.00 (Waffle + Toppings) | **76.7%** | 22 cones (₹1,980) |
        | **TOTALS / BLENDED AVERAGE** | **~₹38.5 Blended** | **~₹9.90 Avg COGS** | **~74.3% Gross** | **~397 Cones = ₹15,080 / Day** |
        """)

        st.markdown("### 🥛 The Pure Milk Advantage vs Competitors")
        st.markdown("""
        - **Zero Synthetic Premix / Zero Vegetable Palm Fat:** Cheap softy machines use ₹120/kg powdered synthetic premix loaded with hydrogenated palm oil that coats the tongue with greasy wax.
        - **"Softie" Pure Milk Formula:** Fresh pasteurized cow milk (8% milk fat + 12% milk solids non-fat) combined with pure cane sugar and Madagascar vanilla beans.
        - **Silky Mouthfeel & Rapid Dissolve:** Dissolves cleanly without leaving oily residue, driving instant repeat purchases.
        - **Speed of Service:** 12-second dispensing per cone ensures queues clear rapidly even during 9:30 PM post-dinner rushes.
        """)

    with col_bp2:
        st.markdown("### 💰 Monthly Franchise Unit Economics (Target: ₹15,000 / Day)")
        st.markdown("""
        | Line Item | Daily Amount | Monthly Total (30 Days) | % of Revenue |
        | :--- | :--- | :--- | :--- |
        | **Gross Revenue** | **₹15,000** | **₹4,50,000** | **100.0%** |
        | Raw Material COGS (Milk, Cones, Sauces) | ₹3,750 | ₹1,12,500 | 25.0% |
        | **Gross Profit (75.0%)** | **₹11,250** | **₹3,37,500** | **75.0%** |
        | Commercial Kiosk Rent (80-120 sq.ft) | — | ₹65,000 | 14.4% |
        | Staff Salaries (2 Shift Operators @ ₹16k) | — | ₹32,000 | 7.1% |
        | Commercial Electricity & Deep Freeze Power | — | ₹18,000 | 4.0% |
        | Packaging, Drip Sleeves & Franchise Tech | — | ₹15,000 | 3.3% |
        | **Total Operating Expenses (OpEx)** | — | **₹1,30,000** | **28.9%** |
        | **NET PROFIT TO FRANCHISEE** | **₹6,916 / day** | **₹2,07,500 / month** | **46.1% Net** |
        """)

        st.markdown("### ⚡ Kiosk Setup Capex & Payback Period")
        st.markdown("""
        - **Commercial 3-Lever Gravity/Pump Soft-Serve Machine:** ₹3,80,000 - ₹4,40,000
        - **Modular Stainless Steel Kiosk / Front Counter (80-120 sq.ft):** ₹1,40,000 - ₹1,80,000
        - **Deep Freeze Storage & Milk Chiller (300L):** ₹45,000
        - **Branded Acrylic LED Signage & Menu Boards:** ₹35,000
        - **POS Terminal, Printer & QR Soundbox:** ₹25,000
        - **Initial Milk & Packaging Inventory:** ₹30,000
        - **Total Franchise Setup Capex:** **₹6,55,000 - ₹7,55,000**
        - **Capital Payback Period:** **3.2 to 3.8 Months!**
        """)

    st.markdown("---")
    st.markdown("### 🏆 Top 5 Flagship Bazaar Locations to Hit & Exceed ₹15,000 / Day:")
    st.markdown("""
    1. **Besant Nagar Beach Promenade (Elliot's Beach):** 40,000+ evening strollers. Projected daily revenue: **₹22,000 - ₹28,000 / day** (150% of target).
    2. **Pondy Bazaar Pedestrian Plaza (T. Nagar):** 75,000+ pedestrian shoppers. Projected daily revenue: **₹20,000 - ₹25,000 / day**.
    3. **Marina Beach Promenade (Near Light House / Triumph of Labour):** 60,000+ beach visitors. Projected daily revenue: **₹18,000 - ₹24,000 / day**.
    4. **Anna Nagar 2nd Avenue (Roundtana to Blue Star):** Premium residential dessert strip. Projected daily revenue: **₹16,000 - ₹21,000 / day**.
    5. **Sowcarpet / Mint Street (Chaat Corridor):** 60,000+ street food shoppers looking for sweet cooling relief after spicy snacks. Projected daily revenue: **₹15,000 - ₹19,000 / day**.
    """)

    # Bottom Quick Nav
    st.markdown("---")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        if st.button("🗺️ ← Back to Catchment Map & Table", key="bp_to_map"):
            st.session_state["active_tab"] = "🗺️ Interactive Catchment Map & Outlets Directory"
            st.rerun()
    with col_f2:
        if st.button("📊 View Comparative Evaluation Matrix →", key="bp_to_mat"):
            st.session_state["active_tab"] = "📊 Comparative Evaluation Matrix"
            st.rerun()


# ==============================================================================
# TAB 9: DOWNLOAD MASTER EXCEL
# ==============================================================================
elif st.session_state["active_tab"] == "📥 Download Master Excel (.xlsx)":
    st.subheader("📥 Download Master 14-Sheet Excel Workbook")
    st.markdown("""
    The complete master workbook is generated and saved in your project folder. It contains:
    - **`Executive_Softy_Strategy`**: Full launch blueprint, margins, best locations.
    - **`Top_50_Ice_Cream_Parlors`**: All 50 top places with Rating, Review Count, **Why Customers Like It**, **What Customers Dislike / Complaints**, and **"Softie" Opportunities**.
    - **`Why_Customers_Like_Ranked`**: Ranked sensory appeal drivers in Chennai.
    - **`What_Customers_Dislike_Ranked`**: Ranked competitor vulnerabilities & complaints.
    - **`20_Bazaars_Matrix`**: Comparative Evaluation Matrix for 20 Bazaars.
    - **`Dedicated_Softy_Outlets`**: 12 dedicated softy specialists audit.
    - **7 Daily Sheets (`Monday_Top50_Traffic_Roads` to `Sunday_Top50_Traffic_Roads`)**: Top 50 floating streets sorted by time intervals.
    """)

    master_path = os.path.join(os.path.dirname(__file__), "Chennai_Top50_Ice_Cream_Parlors_Intelligence.xlsx")
    if os.path.exists(master_path):
        with open(master_path, "rb") as f:
            bytes_data = f.read()

        col_d1, col_d2 = st.columns([1.5, 1])
        with col_d1:
            st.download_button(
                label="📗 Download Master Excel (Chennai_Top50_Ice_Cream_Parlors_Intelligence.xlsx)",
                data=bytes_data,
                file_name="Chennai_Top50_Ice_Cream_Parlors_Intelligence.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col_d2:
            st.success(f"📁 File size: `{len(bytes_data):,}` bytes | 14 Master Sheets")

    st.markdown("---")
    st.markdown(f"#### 📍 Radial Catchment Dossier for Current Selection: **{focal_label}**")
    excel_buffer = site_engine.generate_excel_dossier(
        site_engine.analyze_site_selection(
            center_lat=focal_lat,
            center_lng=focal_lng,
            location_label=focal_label,
            day_of_week=selected_day,
            time_interval=selected_interval,
            business_category="All Categories"
        )
    )

    st.download_button(
        label=f"📊 Download Radial Catchment Dossier for {focal_label} (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"Chennai_Ice_Cream_Catchment_{focal_label.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    # Bottom Quick Nav
    st.markdown("---")
    if st.button("🗺️ ← Back to Catchment Map & Table", key="xl_to_map"):
        st.session_state["active_tab"] = "🗺️ Interactive Catchment Map & Outlets Directory"
        st.rerun()


# Footer
st.markdown("---")
st.caption("""
**"Softie" Pure Milk Franchise Site Selection Intelligence System** | Ground-truth Chennai Places, Routes & H3 Analytics.
Subject to Google Maps Platform Terms of Service.
""")
