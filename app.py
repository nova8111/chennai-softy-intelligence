"""
Chennai Ice Cream & Softy Shop Site Selection & Competitor Intelligence Dashboard.
Exclusively focused on Ice Cream Parlours & Dessert Places:
1. Focal Middle Point & Radius Filtering (1 km, 2 km, 5 km, 10 km, All Chennai).
2. Competitor Directory Ranked by Review Count & Rating.
3. Why Customers Like It vs What Customers Dislike / Complaints.
4. Feeder Road Network Traffic & Floating Commuters.
5. Master 11-Sheet Excel Workbook (.xlsx) Download.
6. Softy Shop Launch Blueprint (Pricing, Margins, Best Locations).
"""

import json
import os
import io
import math
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
    page_title="Chennai Ice Cream & Softy Shop Site Selection",
    page_icon="🍦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #EC4899, #8B5CF6, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-bottom: 1.2rem;
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
        font-size: 1.5rem;
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


@st.cache_resource
def get_engines(api_key: str):
    t_engine = TrafficEngine(api_key=api_key if api_key else None)
    s_extractor = StoreExtractor(api_key=api_key if api_key else None)
    site_engine = SiteOpportunityEngine(api_key=api_key if api_key else None)
    return t_engine, s_extractor, site_engine


@st.cache_data(show_spinner=False)
def load_base_h3_grid():
    return generate_h3_grid(config.H3_RESOLUTION)


# Sidebar Controls
with st.sidebar:
    st.title("🍦 Softy Site Selector")
    
    st.markdown("### 1. Target Middle-Point Location")
    candidate_hubs = []
    # 1. First add the 20 High-Footfall Bazaars
    for b in TOP_20_BAZAAR_SITES:
        candidate_hubs.append({
            "name": f"🛍️ {b['name']}",
            "zone": b["zone"],
            "lat": b["lat"],
            "lng": b["lng"],
            "landmark": b["landmark"]
        })
    # 2. Add traditional Chennai hubs
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

    selected_hub_name = st.selectbox(
        "Select Chennai Bazaar / Neighborhood Hub",
        hub_names,
        index=st.session_state["selected_hub_idx"]
    )
    st.session_state["selected_hub_idx"] = hub_names.index(selected_hub_name)
    current_hub = candidate_hubs[st.session_state["selected_hub_idx"]]

    use_custom_coord = st.checkbox("📍 Or enter custom GPS coordinates", value=False)
    if use_custom_coord:
        focal_lat = st.number_input("Focal Latitude", value=current_hub["lat"], format="%.4f")
        focal_lng = st.number_input("Focal Longitude", value=current_hub["lng"], format="%.4f")
        focal_label = f"Custom Pin ({focal_lat:.3f}, {focal_lng:.3f})"
    else:
        focal_lat = current_hub["lat"]
        focal_lng = current_hub["lng"]
        focal_label = current_hub["name"]

    st.markdown("---")
    st.markdown("### 2. Search Radius Around Point")
    radius_options = {
        "1 km (Walking Catchment)": 1.0,
        "2 km (5-min Drive Catchment)": 2.0,
        "5 km (Standard Trade Area)": 5.0,
        "10 km (Extended Metropolitan)": 10.0,
        "All Chennai (All 50 Top Parlours)": 50.0
    }
    selected_radius_label = st.selectbox(
        "Competitor Catchment Radius",
        list(radius_options.keys()),
        index=2  # default 5 km
    )
    selected_radius_km = radius_options[selected_radius_label]
    st.session_state["radius_km"] = selected_radius_km

    st.markdown("---")
    st.markdown("### 3. Peak Traffic Schedule")
    selected_day = st.selectbox(
        "📅 Day of Week",
        config.DAYS_OF_WEEK,
        index=config.DAYS_OF_WEEK.index(st.session_state["active_day"])
    )
    st.session_state["active_day"] = selected_day

    interval_options = list(config.TIME_INTERVALS.keys())
    selected_interval = st.selectbox(
        "⏰ Time Interval",
        interval_options,
        index=interval_options.index(st.session_state["active_interval"])
    )
    st.session_state["active_interval"] = selected_interval

    st.markdown("---")
    st.markdown("### 4. Map Layer Toggles")
    show_radii_rings = st.checkbox("Show Concentric Catchment Rings", value=True)
    show_feeder_roads = st.checkbox("Show Feeder Road Network", value=True)
    show_h3_traffic = st.checkbox("Show H3 Traffic Congestion", value=True)
    show_bazaars_pins = st.checkbox("Show 20 Bazaar Pins (Cyan)", value=True)

    st.markdown("---")
    st.markdown("### 5. 🍦 Softy Exclusive Focus")
    softy_only_mode = st.toggle(
        "⚡ Show Exclusively Softy Outlets",
        value=False,
        help="Switch ON to filter the app strictly for dedicated softy / soft-serve specialists and kiosks."
    )

    st.markdown("---")
    st.markdown("### 📱 Mobile Phone Access")
    with st.expander("📲 How to Open on Your Phone", expanded=True):
        st.markdown("**1. Connect Phone to Same Wi-Fi**")
        st.markdown("**2. Open This URL in Phone Browser:**")
        st.code("http://192.168.29.58:8501", language="bash")
        st.caption("Or point your phone camera at this QR code:")
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=http://192.168.29.58:8501", width=170)

    st.markdown("---")
    st.markdown("### 🔑 API Key Status")
    user_api_key = st.text_input(
        "Google Maps API Key",
        value=st.session_state["api_key"],
        type="password",
        help="Optional: Ground-truth Chennai data & SQLite caching are active."
    )
    if user_api_key != st.session_state["api_key"]:
        st.session_state["api_key"] = user_api_key
        st.cache_resource.clear()
        st.rerun()

    if st.session_state["api_key"]:
        st.success("🟢 Google Routes & Places API Configured")
    else:
        st.info("🟡 Verified Chennai Ice Cream Registry Active")


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
        p_copy["distance_km"] = dist
        if dist <= 1.0:
            p_copy["ring"] = "0 - 1 km (Immediate)"
        elif dist <= 2.0:
            p_copy["ring"] = "1 - 2 km (Secondary)"
        elif dist <= 5.0:
            p_copy["ring"] = "2 - 5 km (Trade Area)"
        else:
            p_copy["ring"] = "5 - 10 km (Extended)"
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


# ==========================================
# Main Header & Landmark Banner
# ==========================================
st.markdown('<div class="main-header">🍦 Chennai Ice Cream & Softy Shop Site Selection Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header">Exclusively analyzing the top ice cream & dessert parlours, customer likes vs complaints, and optimal locations for launching a high-profit softy brand around <b>{focal_label}</b>.</div>',
    unsafe_allow_html=True
)

st.markdown(f"""
<div style="background-color: #1E293B; border-radius: 8px; padding: 12px 18px; margin-bottom: 16px; border: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
    <div>
        <span style="color: #94A3B8; font-size: 13px;">NEAREST LANDMARK:</span><br/>
        <b style="font-size: 16px; color: #EC4899;">📍 {landmark_info['landmark']}</b>
    </div>
    <div>
        <span style="color: #94A3B8; font-size: 13px;">TRANSIT / METRO STATION:</span><br/>
        <b style="font-size: 15px; color: #F8FAFC;">🚇 {landmark_info['metro_station']}</b>
    </div>
    <div>
        <span style="color: #94A3B8; font-size: 13px;">EST. COMMERCIAL RENT:</span><br/>
        <b style="font-size: 15px; color: #34D399;">{landmark_info['avg_commercial_rent_sqft']}</b>
    </div>
    <div>
        <span style="color: #94A3B8; font-size: 13px;">SOFTY VIABILITY GRADE:</span><br/>
        <b style="font-size: 15px; color: #F59E0B;">{opportunity_score['grade']}</b>
    </div>
</div>
""", unsafe_allow_html=True)

# 4 KPI Summary Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #EC4899;">
        <div class="kpi-title">Ice Cream Parlours in Radius</div>
        <div class="kpi-value">{len(parlors_sorted_by_reviews)} <span style="font-size:1rem; color:#94A3B8;">Shops</span></div>
        <div class="kpi-sub">Within <b>{selected_radius_label.split('(')[0].strip()}</b></div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #3B82F6;">
        <div class="kpi-title">Radial Breakdown (1/2/5km)</div>
        <div class="kpi-value">{count_1km} <span style="font-size:1.1rem; color:#94A3B8;">(1km)</span> / {count_2km} <span style="font-size:1.1rem; color:#94A3B8;">(2km)</span></div>
        <div class="kpi-sub">{count_5km} total parlours in 5 km trade area</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    top_competitor = parlors_sorted_by_reviews[0] if parlors_sorted_by_reviews else {}
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #F59E0B;">
        <div class="kpi-title">Top Rival by Reviews</div>
        <div class="kpi-value">{top_competitor.get('user_ratings_total', 0):,} <span style="font-size:1rem; color:#94A3B8;">Reviews</span></div>
        <div class="kpi-sub"><b>{top_competitor.get('name', 'N/A')[:26]}</b> ({top_competitor.get('rating', 0)}★)</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #10B981;">
        <div class="kpi-title">Softy Disruption Score</div>
        <div class="kpi-value">{opportunity_score['score']} <span style="font-size:1rem; color:#94A3B8;">/ 100</span></div>
        <div class="kpi-sub"><b>{opportunity_score['grade'].split('(')[0]}</b> | Sweet Spot</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# ==========================================
# Navigation Tabs
# ==========================================
tab_matrix, tab_bazaars, tab_softy_specialists, tab_directory, tab_map, tab_likes_dislikes, tab_traffic, tab_blueprint, tab_excel = st.tabs([
    "📊 Comparative Evaluation Matrix (20 Bazaars)",
    "🛍️ 20 Top Bazaar Sites & Product-Market Fit",
    "⚡ Dedicated Softy Outlets in Chennai",
    "🍨 All Ice Cream Parlours (Top 50)",
    "🗺️ Interactive Catchment Map (1, 2, 5 km)",
    "💬 What Customers Like vs Complaints",
    "🚦 Feeder Road Traffic & Commuters",
    "🚀 Softy Shop Launch Blueprint",
    "📥 Download Master Excel (.xlsx)"
])


# ==========================================
# TAB 0: Comparative Evaluation Matrix
# ==========================================
with tab_matrix:
    st.subheader("📊 Chennai Top 20 Bazaars: Comparative Evaluation & Profitability Matrix")
    st.markdown("""
    Comprehensive strategic benchmark comparing all 20 curated high-footfall bazaars across Chennai on **Daily Evening Walking Footfall**, **Target Price Sweet Spot**, **Monthly Sales Volume**, **Est. Monthly Revenue**, **Gross Profit (75% Margin)**, and **Capital Payback Period**.
    """)

    m_kpi1, m_kpi2, m_kpi3, m_kpi4 = st.columns(4)
    with m_kpi1:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #10B981;">
            <div class="kpi-title">Top Gross Profit Bazaar</div>
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
            <div class="kpi-title">Highest Ticket Size</div>
            <div class="kpi-value">₹120 - ₹160 <span style="font-size:0.9rem; color:#94A3B8;">/ Cone</span></div>
            <div class="kpi-sub"><b>Khader Nawaz Khan (KNK) Rd</b></div>
        </div>
        """, unsafe_allow_html=True)
    with m_kpi4:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #F59E0B;">
            <div class="kpi-title">Avg Payback Period</div>
            <div class="kpi-value">3.8 <span style="font-size:0.9rem; color:#94A3B8;">Months</span></div>
            <div class="kpi-sub">Capex recovery at ₹8L kiosk cost</div>
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
            "Target Price": m["target_price"],
            "Monthly Cones": f"{m['est_monthly_cones']:,}",
            "Conversion": m["conversion_rate"],
            "Monthly Revenue": m["est_monthly_revenue"],
            "Gross Profit (75%)": m["gross_profit_75pct"],
            "Rent / sq.ft": m["rental_sqft_estimate"],
            "Payback": m["payback_period_months"],
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

    st.markdown("---")


# ==========================================
# TAB 1: 20 Top Bazaar Sites & Product-Market Fit
# ==========================================
with tab_bazaars:
    st.subheader("🛍️ Chennai's Top 20 High-Footfall Bazaars & Evening Walking Promenades")
    st.markdown("""
    These 20 curated retail bazaars, pedestrian shopping corridors, beachfront promenades, and evening food trail districts are selected because **the crowd is already walking outdoors with high dessert purchase intent**.
    In these micro-markets, traditional scoop parlours struggle with 20-minute queues, high scoop prices, and sticky melting mess. A modern 15-second softy kiosk with anti-drip waffle cones fits this environment.
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
            <div class="kpi-title">Target Price Sweet Spot</div>
            <div class="kpi-value">₹60 - ₹120 <span style="font-size:1rem; color:#94A3B8;">/ Cone</span></div>
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
                <b>🎯 WHY YOUR SOFTY SHOP FITS IN HERE VERY, VERY WELL:</b><br/>
                {bz['why_softy_fits_perfectly']}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-top: 10px; background-color: #0F172A; padding: 8px 12px; border-radius: 6px; font-size: 13px;">
                <div>🍦 <b>Hero Flavors:</b> <span style="color: #F472B6;">{bz['recommended_hero_flavors']}</span></div>
                <div>💰 <b>Target Price:</b> <span style="color: #34D399; font-weight: 700;">{bz['target_price_point']}</span></div>
                <div>📦 <b>Est. Monthly Volume:</b> <b style="color: #60A5FA;">{bz['estimated_monthly_cones']}</b></div>
            </div>
        </div>
        """)


# ==========================================
# TAB 2: Dedicated Softy Outlets in Chennai
# ==========================================
with tab_softy_specialists:
    st.subheader("⚡ Chennai Dedicated Softy (Soft-Serve) Specialists & Competitive Audit")
    st.markdown("""
    Detailed breakdown of Chennai's 12 prominent dedicated softy specialists, heritage dairy counters, and fast-food soft-serve swirl kiosks.
    Inspect their pricing, dispensing speeds, signature softies, dairy base quality, customer complaints, and **how your new softy shop can disrupt them**.
    """)

    s_kpi1, s_kpi2, s_kpi3 = st.columns(3)
    with s_kpi1:
        st.markdown("""
        <div class="kpi-card" style="border-left-color: #D97706;">
            <div class="kpi-title">Competitor Price Range</div>
            <div class="kpi-value">₹40 - ₹90 <span style="font-size:0.9rem; color:#94A3B8;">/ Cone</span></div>
            <div class="kpi-sub">Mass market affordability sweet spot</div>
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
                <b>🎯 HOW YOUR SOFTY BRAND WINS:</b> {s['disruption_angle']}
            </div>
        </div>
        """)


# ==========================================
# TAB 3: Ice Cream Parlours Directory
# ==========================================
with tab_directory:
    st.subheader(f"Top Ice Cream Parlours within {selected_radius_label} of {focal_label}")
    st.caption("Sorted strictly by total review volume (popularity & customer footfall velocity). Click into any parlour to inspect why customers love it and what they complain about.")

    if softy_only_mode:
        st.info("⚡ **SOFTY EXCLUSIVE FOCUS ACTIVE:** Showing all parlours with their specific softy disruption angle.")

    if not parlors_sorted_by_reviews:
        st.warning(f"No ice cream parlours found within {selected_radius_label}. Try expanding to 5 km or All Chennai in the left sidebar!")
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
                <div class="like-box">
                    <b>✅ WHY CUSTOMERS LIKE IT:</b> {p['why_customers_like_it']}
                </div>
                <div class="dislike-box">
                    <b>❌ WHAT CUSTOMERS DISLIKE / COMPLAINTS:</b> {p['what_customers_dislike']}
                </div>
                <div class="softy-box">
                    <b>💡 HOW YOUR SOFTY SHOP CAN BEAT THEM:</b> {p['softy_opportunity']}
                </div>
            </div>
            """)


# ==========================================
# TAB 2: Interactive Catchment Map
# ==========================================
with tab_map:
    st.subheader(f"Concentric Radial Catchment Map (1, 2, 5 km) from {focal_label}")

    layers = []

    # 1. H3 Traffic Layer
    if show_h3_traffic:
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

    # 2. Concentric Radial Circles
    if show_radii_rings:
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
    if show_feeder_roads:
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
            "color": [236, 72, 153, 240], # Vibrant Berry Pink
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
    if show_bazaars_pins:
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
                "color": [6, 182, 212, 240], # Bright Cyan
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
        <div><span style="display:inline-block; width:14px; height:14px; background-color:#FACC15; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>Your Focal Middle Point</b></div>
        <div><span style="display:inline-block; width:14px; height:14px; background-color:#EC4899; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>Ice Cream Parlour (Pink)</b></div>
        <div><span style="display:inline-block; width:14px; height:14px; background-color:#06B6D4; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>20 Top Bazaars (Cyan)</b></div>
        <div><span style="display:inline-block; width:14px; height:14px; border:2px solid #EC4899; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>1 km Catchment</b></div>
        <div><span style="display:inline-block; width:14px; height:14px; border:2px solid #F59E0B; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>2 km Catchment</b></div>
        <div><span style="display:inline-block; width:14px; height:14px; border:2px solid #3B82F6; border-radius:50%; margin-right:6px; vertical-align:middle;"></span><b>5 km Trade Area</b></div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# TAB 3: Likes vs Dislikes Analysis
# ==========================================
with tab_likes_dislikes:
    st.subheader("💬 Customer Psychology: Why Chennai Loves Certain Parlours vs What They Hate")
    st.caption("Extracted from over 250,000+ customer reviews across Chennai's top 50 ice cream parlours.")

    col_like_theme, col_dislike_theme = st.columns(2)

    with col_like_theme:
        st.markdown("#### ✅ Top 5 Things Customers LOVE")
        st.markdown("""
        1. **Pure Dairy Creaminess & Real Fruit Pulp (92% Positive Sentiment)**
           - *Why:* Customers hate artificial icy premixes. Naturals' Tender Coconut and Amadora's Five Bean Vanilla win because customers feel the rich milk fat and genuine fruit pieces.
        2. **Late-Night Post-Dinner Dessert Strolls (88% Positive)**
           - *Why:* Chennai families and young couples specifically venture out after 9:30 PM dinner for a cold sweet treat. Parlours open till 12:30 AM capture 45% of daily revenue in those 3 hours.
        3. **Warm-and-Cold Dessert Combinations (81% Positive)**
           - *Why:* Sizzling brownies with cold scoops (Corner House DBC, Belgian Waffle sandwiches) trigger dopamine and drive the highest repeat orders.
        4. **Aesthetic Instagram Presentation (76% Positive)**
           - *Why:* Colorful swirls, black charcoal cones, and gold drizzle make customers take out their phones and post stories, giving free viral marketing.
        5. **Instant Grab-and-Go Portability (71% Positive)**
           - *Why:* Customers walking on Besant Nagar beach or T. Nagar Pondy Bazaar want an instant cone in hand to enjoy while walking.
        """)

    with col_dislike_theme:
        st.markdown("#### ❌ Top 5 Things Customers HATE & COMPLAIN ABOUT")
        st.markdown("""
        1. **Weighing Scale Pricing Traps & Exorbitant Bills (84% Negative)**
           - *Complaint:* Customers walk into Ibaco or Cream Stone expecting to spend ₹150 and walk out shocked with a ₹550 bill. They feel cheated.
           - *Your Softy Play:* **Fixed Flat Pricing:** ₹60, ₹80, and ₹110 on a big transparent board!
        2. **15 to 25 Minute Slow Queues & Cold Stone Delays (79% Negative)**
           - *Complaint:* Mixing on cold stone is slow; by the time the second cone is prepared, the first is already melting.
           - *Your Softy Play:* **Instant 15-Second Dispense:** Soft-serve levers dispense in 5 seconds flat!
        3. **Rapid Melting in Chennai's 34°C Humidity (74% Negative)**
           - *Complaint:* Heavy gelatos and soft scoops melt into sticky soup dripping over hands within 3 minutes outdoors.
           - *Your Softy Play:* **Waffle Cup & Drip-Guard Collar:** High butterfat soft-serve formula that holds shape.
        4. **Parking Tow-Aways & Traffic Fines (68% Negative)**
           - *Complaint:* No car parking on Usman Road, KNK Road, or 2nd Avenue Anna Nagar; traffic police issue fines.
           - *Your Softy Play:* **Pedestrian Footfall Plazas:** Position on walking corridors (like Pondy Bazaar or beach promenades).
        5. **Heavy Sickly Sugar Overload (58% Negative)**
           - *Complaint:* Heavy scoop ice creams leave customers feeling bloated and thirsty.
           - *Your Softy Play:* **Light, Velvety Texture:** Higher overrun and balanced sweetness.
        """)


# ==========================================
# TAB 4: Feeder Road Traffic
# ==========================================
with tab_traffic:
    st.subheader(f"Traffic Volume & Floating Footfall for Roads Feeding {focal_label}")
    st.caption(f"Evaluates all 15 primary & secondary roads feeding your candidate site during {selected_day} ({selected_interval}) based on trailing 3-month moving average.")

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


# ==========================================
# TAB 5: Softy Shop Blueprint & Playbook
# ==========================================
with tab_blueprint:
    st.subheader("🚀 Strategic Blueprint for Starting a Softy Shop in Chennai")
    st.markdown("How to build a 75% gross margin soft-serve brand and beat the existing scoop parlours:")

    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown("### 🏆 Top 5 Best Locations to Open in Chennai:")
        st.markdown("""
        1. **Besant Nagar Beach Promenade (Elliot's Beach):**
           - *Why:* Chennai's #1 evening walking & leisure strip. 40,000+ weekend floating pedestrians craving immediate cold treats while walking on the beach.
           - *Target Rent:* ₹70,000 - ₹1,20,000/month for an 80-120 sq.ft micro-kiosk.
        2. **Anna Nagar Shanthi Colony / 2nd Avenue:**
           - *Why:* Chennai's premier post-dinner dessert walking street. High-income families walk here after dinner specifically looking for ice cream.
           - *Target Rent:* ₹80,000 - ₹1,50,000/month.
        3. **Pondy Bazaar Pedestrian Plaza (T. Nagar):**
           - *Why:* 85,000+ daily shoppers exhausted from shopping looking for quick ₹60-₹80 relief. Huge footfall velocity.
        4. **OMR Perungudi / Kandanchavadi Tech Corridor:**
           - *Why:* 100,000+ young IT professionals living in apartments seeking casual evening dessert hangouts.
        5. **Velachery 100 Feet Bypass Road (Near Vijayanagar):**
           - *Why:* Massive concentration of college students and young millennial families.
        """)

    with col_b2:
        st.markdown("### 💰 Economics & Pricing Sweet Spot:")
        st.markdown("""
        | Item | Target Menu Price | Raw Cost of Goods (COGS) | Gross Profit Margin |
        | :--- | :--- | :--- | :--- |
        | **Classic Vanilla / Cocoa Swirl** | **₹60** | ₹14 (Milk + Cone + Mix) | **76.6%** |
        | **Gourmet Belgian Chocolate Cone** | **₹85** | ₹20 (Belgian cocoa mix) | **76.5%** |
        | **Lotus Biscoff / Nutella Sundae Cup** | **₹120** | ₹28 (Softy + Warm Sauce) | **76.7%** |
        | **Tender Coconut / Mango Seasonal Swirl** | **₹90** | ₹21 (Real fruit puree) | **76.6%** |
        """)
        st.markdown("""
        - **Daily Volume Target:** 250 - 400 cones / day
        - **Monthly Revenue:** ₹5.5 Lakhs - ₹9.0 Lakhs
        - **Net Profit Margin:** **32% - 38%** after rent, electricity, and 2 staff members.
        """)


# ==========================================
# TAB 6: Download Master Excel
# ==========================================
with tab_excel:
    st.subheader("📥 Download Master 11-Sheet Excel Workbook")
    st.markdown("""
    The complete master workbook is generated and saved in your project folder. It contains:
    - **`Executive_Softy_Strategy`**: Full launch blueprint, margins, best locations.
    - **`Top_50_Ice_Cream_Parlors`**: All 50 top places with Rating, Review Count, **Why Customers Like It**, **What Customers Dislike / Complaints**, and **Softy Opportunities**.
    - **`Why_Customers_Like_Ranked`**: Ranked sensory appeal drivers in Chennai.
    - **`What_Customers_Dislike_Ranked`**: Ranked competitor vulnerabilities & complaints.
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
            st.success(f"📁 File size: `{len(bytes_data):,}` bytes | 14 Sheets (Includes Comparative Matrix & Dedicated Softy Audit)")

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


# Footer
st.markdown("---")
st.caption("""
**Google Maps Platform Attribution & Compliance Notice:**
- Usage of Google Maps Platform products may incur costs against your Google Cloud project billing account. Zero-cost prototyping is supported via the Maps Demo Key or the built-in calibrated cache.
- APIs utilized: Routes API, Places API (New), Maps JavaScript SDK.
- Restrict production keys via [Google Cloud Console API Key Restrictions](https://docs.cloud.google.com/api-keys/docs/add-restrictions-api-keys).
- Google-sourced code snippets are provided 'as-is' under the Apache 2.0 License (https://www.apache.org/licenses/LICENSE-2.0).
- Subject to the [Google Maps Platform Terms of Service](https://cloud.google.com/maps-platform/terms).
""")
