# 🚦 Chennai Urban Analytics: Peak Traffic Corridors & Retail Footfall Engine

An end-to-end geospatial intelligence pipeline and interactive 3D web dashboard for Chennai, Tamil Nadu, India.

---

## 🌟 Core Modules

### 1. Spatial Boundary & Uber H3 Hexagonal Grid
- **Urban Extent:** Bound by Ennore Port (~13.21° N) to Sholinganallur (~12.90° N), Poonamallee (~13.05° N) to the Bay of Bengal Coastline (~80.32° E).
- **H3 Grid System:** Partitioned into **663 hexagonal cells** at **Resolution 8** (edge length ~460m, area ~0.737 km² per cell).
- **Spatial Interpolation:** Road corridor congestion values and traffic delays are continuously propagated to the H3 grid cells via inverse distance weighting to create an urban congestion intensity surface.

### 2. Module A: Arterial Road Traffic & 7-Day Peak Schedule Engine
- **7 Monitored Arterial Corridors:**
  1. **GST Road** (Kathipara Junction to Tambaram belt via Airport, Chromepet)
  2. **Anna Salai / Mount Road** (Chennai Central to Guindy / Kathipara)
  3. **OMR / Rajiv Gandhi Salai** (Madhya Kailash to Sholinganallur IT hub)
  4. **Inner Ring Road / JN Road** (Koyambedu CMBT to Kathipara via Vadapalani)
  5. **Poonamallee High Road** (Chennai Central to Poonamallee via Kilpauk, Maduravoyal)
  6. **ECR** (Thiruvanmiyur to Sholinganallur coastal link)
  7. **Ennore Expressway** (Royapuram Port to Ennore Thermal Station)
- **4 Daily Time Intervals:**
  - Morning Peak (`08:30 - 10:30`)
  - Afternoon Off-Peak (`13:00 - 15:00`)
  - Evening Peak (`17:30 - 20:30`)
  - Late Night Baseline Free-Flow (`01:00 - 03:00`)
- **Metric:** `Congestion Factor (CF) = duration_in_traffic / free_flow_duration`.
- Dynamic ranking of the top 5 most congested corridors for every day of the week.

### 3. Module B: High-Footfall & Top-Rated Retail Destination Finder
- **Commercial Clusters:** T. Nagar, Velachery, Anna Nagar, Mylapore, OMR tech corridors, Purasawalkam, Porur, George Town.
- **Store Categories:** `shopping_mall`, `department_store`, `clothing_store`, `electronics_store`, `supermarket`.
- **Composite Footfall Proxy Score (FPS):**
  $$\text{FPS} = \text{user\_ratings\_total} \times \log_{10}(\text{rating} + 1)$$
- **Weekly Visitation Curves & Dwell Times:** Hourly visitor percentage profiles (09:00 - 22:00) modeling weekend shopping rushes (peaking Sat/Sun 18:00 - 21:30) and typical dwell times (45 - 180 mins).
- **Access Road Traffic Coupling:** Associates each commercial store with its immediate arterial access road to display real-time access delays and congestion factors.

### 4. Module C: Interactive Streamlit Dashboard (`app.py`)
- **3D PyDeck Congestion Surface:** Color-coded H3 hexagons (Green = Free Flow, Amber = Moderate, Red = Severe Gridlock) with 3D elevation extrusion based on congestion intensity.
- **Top Store Pins:** Cyan pins with interactive tooltips and an in-depth store profile drawer showing visitor volume curves and access road delays.
- **Summary KPI Cards:** Real-time worst congested road, average corridor speed during peak hours, top footfall destination, and total monitored H3 cells.
- **7-Day Heatmap Matrix:** Complete corridor vs day-of-week matrix.
- **2D Folium GIS Map:** Interactive vector lines and markers with detailed popups.

### 5. Cost & API Efficiency: SQLite Caching
- Deterministic SHA-256 cache keys derived from `(origin, destination, corridor_id, day_of_week, time_slot)` in `urban_analytics_cache.db`.
- **Zero redundant billable calls:** Once cached, queries are served instantly locally with zero API cost.
- **Autonomous Fallback:** Operates seamlessly even without an API key using the calibrated Chennai urban mobility simulation engine.

---

## 🚀 Quickstart & Usage

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Configure Google Maps Platform API Key (Optional)
Copy `.env.example` to `.env` or enter your API key directly in the dashboard sidebar:
```bash
cp .env.example .env
```
Add your key:
```ini
GOOGLE_MAPS_API_KEY=your_actual_key_here
```

### 3. Launch Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📁 Repository Structure

```
├── config.py                 # City boundaries, corridor definitions, time schedules, and API settings
├── spatial_grid.py           # GeoPandas polygon, Uber H3 Res 8 grid generation, spatial joins
├── traffic_engine.py         # Google Routes API client, SQLite caching, delay and CF calculations
├── store_extractor.py        # Places API querying, FPS scoring, weekly visitation curves, access delays
├── app.py                    # Streamlit web interface with PyDeck 3D & Folium maps
├── requirements.txt          # Pinned dependency requirements
├── .env.example              # Example environment configuration
└── urban_analytics_cache.db  # SQLite persistent cache database
```
