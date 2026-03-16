import streamlit as st
import fastf1
from fastf1.plotting import *
import plotly.express
import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="F1 Analysis Dashboard",page_icon=":racing_car:",layout='wide')

st.title(" :racing_car: F1 Analysis Dashboard")
st.markdown('<style>div.block-container{padding-top:3rem;}</style>',unsafe_allow_html=True)

if not os.path.exists('f1_cache'):
    os.makedirs('f1_cache')
fastf1.Cache.enable_cache('f1_cache')

fastf1.plotting.setup_mpl(misc_mpl_mods=False)

col1, col2, col3 = st.columns(3)
    
@st.cache_data
def get_race_schedule(year):
    schedule = fastf1.get_event_schedule(year)
    
    return schedule[schedule['EventFormat'] != 'testing']['EventName'].tolist()

@st.cache_data
def get_drivers(year,race,session_type):
    session = fastf1.get_session(year,race,session_type)
    
    session.load(telemetry=False, weather=False, messages=False)
    
    drivers = session.results['Abbreviation'].tolist()
    
    return drivers

with col1:
    selected_year = st.selectbox("Select Year", [2024, 2025, 2026])

with col2:
    races = get_race_schedule(selected_year)
    selected_race = st.selectbox("Select Race", races)
        
with col3:
    drivers = get_drivers(selected_year,selected_race,'R')
    selected_driver = st.selectbox('Select Driver',drivers)
    
if st.button("Load Race Data"):
    with st.spinner(f"Fetching data for the {selected_year} {selected_race}..."):
        
        session = fastf1.get_session(selected_year,selected_race,'R')
        session.load()
        
        st.subheader(f"Speed Telemetry: {selected_driver} - Fastest Lap")
        
        try:
            driver_lap = session.laps.pick_driver(selected_driver).pick_fastest()
            telemetry = driver_lap.get_telemetry()
            
            color_1 = fastf1.plotting.get_team_color(driver_lap['Team'], session=session)
            
            fig, ax = plt.subplots(figsize=(10,5))
            ax.plot(telemetry['Distance'], telemetry['Speed'], color=color_1, label=selected_driver)
            
            ax.set_xlabel("Distance (meters)")
            ax.set_ylabel("Speed (km/h)")
            ax.set_title(f"{selected_driver} Speed vs Distance - {selected_year} {selected_race}")
            ax.legend()
            
            # Send the Matplotlib chart to Streamlit
            st.pyplot(fig)
            
            # Also show the raw race results in a table underneath
            st.subheader("Race Results")
            st.dataframe(session.results[['Position', 'BroadcastName', 'TeamName', 'Points', 'Time']])
            
        except Exception as e:
            st.error(f"Could not load telemetry for {selected_driver}. They may not have completed a lap or participated in this race.")

