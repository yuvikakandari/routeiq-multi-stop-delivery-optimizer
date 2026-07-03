# frontend/app.py
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="RouteIQ Core", layout="wide")

# Persistent State Initializations
if "stops" not in st.session_state:
    st.session_state.stops = []
if "routing_results" not in st.session_state:
    st.session_state.routing_results = None

geolocator = Nominatim(user_agent="routeiq_dispatch_engine")

# Inject Custom Olive Green Background and High-Contrast Typography Selection
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #556B2F !important;
            color: #FFFFFF !important;
        }
        [data-testid="stHeader"] {
            background-color: rgba(0,0,0,0) !important;
        }
        .stSelectbox label, .stTextInput label {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        div[data-testid="stMetricValue"] {
            color: #FFFFFF !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #EAEAEA !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("RouteIQ — Multi-Stop Delivery Route Optimizer")
st.write("")

col_control, col_map = st.columns([1, 2])

with col_control:
    st.subheader("Configuration Panel")
    scenario = st.selectbox(
        "Current Congestion Footprint", 
        ['Clear_Night', 'Morning_Rush', 'Evening_Rush', 'Monsoon_Rain']
    )
    
    st.write("")
    st.markdown("### Location Search Integration")
    address_query = st.text_input("Enter Delhi landmark or locality:", placeholder="e.g. Connaught Place, India Gate")
    
    if st.button("Resolve and Add Address Pin", use_container_width=True):
        if address_query:
            try:
                location = geolocator.geocode(f"{address_query}, Delhi, India", timeout=10)
                if location:
                    coords = (location.latitude, location.longitude)
                    if coords not in st.session_state.stops and len(st.session_state.stops) < 6:
                        st.session_state.stops.append(coords)
                        st.session_state.routing_results = None  
                        st.rerun()
                    elif len(st.session_state.stops) >= 6:
                        st.error("Maximum threshold of 6 stops reached.")
                else:
                    st.error("Address coordinates could not be resolved.")
            except Exception:
                st.error("Geocoding service timeout.")

    st.write("")
    if st.button("Clear Dropoff Pin Selection", use_container_width=True):
        st.session_state.stops = []
        st.session_state.routing_results = None
        st.rerun()

    st.write("")
    st.markdown(f"**Registered Stops ({len(st.session_state.stops)} / 6):**")
    for idx, stop in enumerate(st.session_state.stops):
        st.text(f"Stop {idx+1}: Lat {stop[0]:.5f}, Lon {stop[1]:.5f}")

    st.write("")
    optimize_btn = st.button("Run Route Optimization Pipeline", type="primary", use_container_width=True)

# Graph Construction
m = folium.Map(location=[28.6139, 77.2090], zoom_start=13)
folium.Marker([28.6139, 77.2090], popup="Warehouse Central Depot", icon=folium.Icon(color='green', icon='home')).add_to(m)

for idx, stop in enumerate(st.session_state.stops):
    folium.Marker(stop, popup=f"Stop #{idx+1}", icon=folium.Icon(color='blue', icon='info-sign')).add_to(m)

with col_map:
    # Removed fixed width=800, added container scaling
    map_interaction = st_folium(m, height=520, use_container_width=True, key="dispatch_map")
# Mouse Pointer Coordinate Capture
if map_interaction and map_interaction.get("last_clicked"):
    click_coords = (map_interaction["last_clicked"]["lat"], map_interaction["last_clicked"]["lng"])
    if click_coords not in st.session_state.stops and len(st.session_state.stops) < 6 and st.session_state.routing_results is None:
        st.session_state.stops.append(click_coords)
        st.rerun()

if optimize_btn:
    if not (3 <= len(st.session_state.stops) <= 6):
        st.error("Select between 3 and 6 location markers to execute routing algorithms.")
    else:
        with st.spinner("Processing optimization matrices across network graphs..."):
            response = requests.post("http://127.0.0.1:8000/api/optimize", json={"locations": st.session_state.stops, "scenario": scenario})
            if response.status_code == 200:
                st.session_state.routing_results = response.json()
            else:
                st.error("Backend processing exception.")

# Optimization Matrix Breakdown
if st.session_state.routing_results is not None:
    res = st.session_state.routing_results
    b, o = res["baseline"], res["optimized"]
    savings = ((b["eta"] - o["eta"]) / b["eta"]) * 100
    
    st.write("---")
    st.subheader("Optimization Summary Matrix")
    st.write("")
    
    cm1, cm2, cm3 = st.columns(3)
    cm1.metric(label="Distance Baseline", value=f"{b['eta']} mins", delta=f"{b['distance']} km total", delta_color="off")
    cm2.metric(label="RouteIQ ML Optimized", value=f"{o['eta']} mins", delta=f"-{savings:.1f}% Time ({o['distance']} km)", delta_color="inverse")
    cm3.metric(label="Evaluated Traffic Footprint", value=scenario)
    
    st.write("")
    
    m_res = folium.Map(location=[28.6139, 77.2090], zoom_start=13)
    folium.Marker([28.6139, 77.2090], popup="Warehouse Depot Hub", icon=folium.Icon(color='green', icon='home')).add_to(m_res)
    
    for idx, s in enumerate(st.session_state.stops):
        folium.Marker(s, popup=f"Stop #{idx+1}", icon=folium.Icon(color='black', icon='info-sign')).add_to(m_res)
    
    if b["path"]: 
        folium.PolyLine(b["path"], color="red", weight=3, opacity=0.6, tooltip="Shortest-Distance Baseline").add_to(m_res)
    if o["path"]: 
        folium.PolyLine(o["path"], color="blue", weight=5, opacity=0.8, tooltip="RouteIQ ML Optimized Path").add_to(m_res)
    
    st.subheader("Calculated Route Leg Output Paths")
    st.caption("Red Line = Shortest Distance Baseline | Blue Line = RouteIQ Congestion-Aware Track")
    st_folium(m_res, height=500, use_container_width=True, key="results_map")
# Persistent Execution Ledger Table
st.write("---")
st.subheader("Historical Batch Performance Log (SQLite Persistence)")
st.write("")
try:
    history_response = requests.get("http://127.0.0.1:8000/api/history")
    if history_response.status_code == 200:
        history_data = history_response.json()
        if history_data:
            import pandas as pd
            df_logs = pd.DataFrame(history_data, columns=[
                "Timestamp", "Scenario", "Stops Optimized", "Baseline ETA (m)", "RouteIQ ETA (m)", "Efficiency Gain (%)"
            ])
            st.dataframe(df_logs, use_container_width=True)
except Exception:
    st.caption("Could not connect to database history services.")