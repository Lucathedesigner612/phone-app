import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="GPS Tracker Pro", layout="wide", page_icon="📡")

# --- 2. DATABASE (Simulated) ---
# Note: In a professional version, we would use 'st.connection' to a SQL database
if "db" not in st.session_state:
    st.session_state.db = []

# --- 3. THE TRACKING ENGINE (JavaScript) ---
# This script runs on the phone browser to grab GPS coordinates
tracker_html = """
<div style="background: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #6772E5;">
    <h3 style="color: #1f1f1f; font-family: sans-serif;">System Status: Active</h3>
    <p id="status" style="color: #666;">Waiting for Authorization...</p>
    <button onclick="startTracking()" style="background: #6772E5; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; width: 100%;">
        🛰️ ENABLE LIVE TRACKING
    </button>
</div>

<script>
    function startTracking() {
        document.getElementById('status').innerHTML = "Requesting GPS Access...";
        if (navigator.geolocation) {
            navigator.geolocation.watchPosition(sendPosition, handleError, {
                enableHighAccuracy: true,
                maximumAge: 0
            });
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    }

    function sendPosition(position) {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const timestamp = new Date().toLocaleTimeString();
        
        document.getElementById('status').innerHTML = "📡 Signal Locked: " + lat.toFixed(4) + ", " + lon.toFixed(4);
        
        // Push data to Streamlit
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: {lat: lat, lon: lon, time: timestamp}
        }, '*');
    }

    function handleError(error) {
        document.getElementById('status').innerHTML = "❌ Error: " + error.message;
    }
</script>
"""

# --- 4. WEBSITE TABS ---
tab1, tab2 = st.tabs(["📍 Live Map", "📱 Device Setup"])

with tab2:
    st.header("Setup a Device")
    st.info("Open this page on the phone you want to track and click the button below.")
    
    # This captures the data from the JavaScript button
    location_data = components.html(tracker_html, height=250)
    
    # If data comes in from the phone, save it to the history
    if location_data:
        # Check if the last point is the same to avoid duplicates
        if not st.session_state.db or st.session_state.db[-1]['time'] != location_data['time']:
            st.session_state.db.append(location_data)

with tab1:
    st.header("Global Satellite View")
    
    if not st.session_state.db:
        st.warning("No active signals. Please enable tracking on a device in the 'Device Setup' tab.")
        # Default view (Malta)
        m = folium.Map(location=[35.8989, 14.5146], zoom_start=11)
    else:
        # Get the latest position
        latest = st.session_state.db[-1]
        st.metric("Latest Signal", f"{latest['lat']:.4f}, {latest['lon']:.4f}", f"Updated: {latest['time']}")
        
        # Create Map
        m = folium.Map(location=[latest['lat'], latest['lon']], zoom_start=16, tiles="Stamen Terrain")
        
        # Draw a line of the path taken
        path = [[point['lat'], point['lon']] for point in st.session_state.db]
        folium.PolyLine(path, color="blue", weight=2.5, opacity=0.8).add_to(m)
        
        # Marker for current position
        folium.Marker(
            [latest['lat'], latest['lon']],
            popup="Target Device",
            icon=folium.Icon(color="red", icon="screenshot", prefix="fa")
        ).add_to(m)

    st_folium(m, width="100%", height=500)

# --- 5. DATA LOG ---
with st.expander("📄 Raw Signal Logs"):
    if st.session_state.db:
        st.table(pd.DataFrame(st.session_state.db).tail(10))
    else:
        st.write("No data logged yet.")
