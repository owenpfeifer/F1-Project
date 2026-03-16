import streamlit as st
import fastf1
from fastf1.plotting import *
import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Compare Drivers", page_icon="⚔️", layout='wide')

st.title("⚔️ Compare Driver Telemetry")
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True)

if not os.path.exists('f1_cache'):
    os.makedirs('f1_cache')
fastf1.Cache.enable_cache('f1_cache')

setup_mpl(misc_mpl_mods=False)

# 1. Helper Functions
@st.cache_data
def get_race_schedule(year):
    schedule = fastf1.get_event_schedule(year)
    return schedule[schedule['EventFormat'] != 'testing']['EventName'].tolist()

@st.cache_data
def get_drivers(year, race, session_type):
    session = fastf1.get_session(year, race, session_type)
    session.load(telemetry=False, weather=False, messages=False)
    return session.results['Abbreviation'].tolist()

# 2. Four Columns for our Dropdowns
col1, col2, col3, col4 = st.columns(4)

with col1:
    selected_year = st.selectbox("Select Year", [2024, 2025, 2026])

with col2:
    races = get_race_schedule(selected_year)
    selected_race = st.selectbox("Select Race", races)
        
with col3:
    drivers = get_drivers(selected_year, selected_race, 'R')
    driver_1 = st.selectbox('Select Driver 1', drivers, index=0) # Defaults to the first driver
    
with col4:
    # We use the same driver list, but default to the second driver in the list
    driver_2 = st.selectbox('Select Driver 2', drivers, index=1)

# 3. The Comparison Logic
if st.button("Compare Drivers"):
    if driver_1 == driver_2:
        st.warning("Please select two different drivers to compare.")
    else:
        with st.spinner(f"Fetching telemetry for {driver_1} and {driver_2}..."):
            
            session = fastf1.get_session(selected_year, selected_race, 'R')
            session.load()
            
            st.subheader(f"Speed Comparison: {driver_1} vs {driver_2} - Fastest Laps")
            
            try:
                # Get fastest laps for BOTH drivers
                lap_1 = session.laps.pick_driver(driver_1).pick_fastest()
                lap_2 = session.laps.pick_driver(driver_2).pick_fastest()
                
                # Get telemetry for BOTH drivers
                tel_1 = lap_1.get_telemetry()
                tel_2 = lap_2.get_telemetry()
                
                # Fetch team colors automatically using FastF1's built-in tools
                color_1 = fastf1.plotting.get_team_color(lap_1['Team'], session=session)
                color_2 = fastf1.plotting.get_team_color(lap_2['Team'], session=session)
                
                if color_1 == color_2:
                    color_2 = 'black'
                
                # Build the graph
                fig, ax = plt.subplots(figsize=(12, 6))
                
                # Plot Driver 1
                ax.plot(tel_1['Distance'], tel_1['Speed'], color=color_1, label=f"{driver_1} ({lap_1['LapTime'].total_seconds():.3f}s)")
                
                # Plot Driver 2
                ax.plot(tel_2['Distance'], tel_2['Speed'], color=color_2, label=f"{driver_2} ({lap_2['LapTime'].total_seconds():.3f}s)")
                
                ax.set_xlabel("Distance (meters)")
                ax.set_ylabel("Speed (km/h)")
                ax.set_title(f"Fastest Lap Speed Comparison - {selected_year} {selected_race}")
                ax.legend()
                
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Could not load telemetry. Ensure both drivers completed a lap in this race. Error: {e}")