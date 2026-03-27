import streamlit as st
import phonenumbers
from phonenumbers import geocoder, carrier
from streamlit_folium import st_folium
import folium
import pandas as pd

st.set_page_config(page_title="Luca's Signal Tracker", layout="wide")

# --- DATABASE ---
if "target_coords" not in st.session_state:
    st.session_state.target_coords = None

st.title("📡 Satellite Phone Tracker")

# --- STEP 1: THE LOOKUP ---
with st.sidebar:
    st.header("🔍 Identify Target")
    number_input = st.text_input("Enter Phone Number (with +)", placeholder="+356 99...")
    
    if number_input:
        try:
            parsed_num = phonenumbers.parse(number_input)
            location = geocoder.description_for_number(parsed_num, "en")
            isp = carrier.name_for_number(parsed_num, "en")
            st.success(f"📍 Location: {location}")
            st.info(f"📶 Carrier: {isp}")
            
            st.divider()
            st.subheader("🔗 Send Tracking Link")
            st.write("Send this link to the target. Once they click, the map will update.")
            st.code(f"https://luca-phone-app.streamlit.app/?target={number_input.replace('+', '')}")
        except:
            st.error("Invalid format. Use + and Country Code.")

# --- STEP 2: THE MAP ---
col1, col2 = st.columns([3, 1])

with col1:
    # Default Map Center (Malta)
    m = folium.Map(location=[35.85, 14.45], zoom_start=10)
    
    # Check if a target has shared their location
    query_params = st.query_params
    if "lat" in query_params:
        lat = float(query_params["lat"])
        lon = float(query_params["lon"])
        st.session_state.target_coords = [lat, lon]
        
    if st.session_state.target_coords:
        folium.Marker(
            st.session_state.target_coords, 
            popup="Target Device", 
            icon=folium.Icon(color='red', icon='screenshot')
        ).add_to(m)
        m.location = st.session_state.target_coords
        m.zoom_start = 16

    st_folium(m, width="100%", height=500)

with col2:
    st.subheader("Signal Logs")
    if st.session_state.target_coords:
        st.metric("Status", "🟢 ONLINE")
        st.write(f"Lat: {st.session_state.target_coords[0]}")
        st.write(f"Lon: {st.session_state.target_coords[1]}")
    else:
        st.metric("Status", "🔴 WAITING")
        st.write("No live signal detected yet.")
