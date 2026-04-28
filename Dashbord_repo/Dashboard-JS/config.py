## for Synoptic Data pull 

##TOKEN this will be added to the streamlit app secret later, token is stored in secrets.toml 
import streamlit as st
API_TOKEN = st.secrets["API_TOKEN"]
#stations to use, if adding more, check current conditions. Station ID from Synoptic
STATIONS = ["UUSBP", "UUWPP", "ATH20", "UUSSD"]

#variables to use, check synoptic for documentation of variable names. These are all current variables from snow study plots
VARIABLES = [
    "air_temp",
    "relative_humidity",
    "snow_depth",
    "volt",
    "outgoing_radiation_sw", 
    "solar_radiation",
    "photosynthetically_active_radiation",
    "incoming_radiation_lw",
    "outgoing_radiation_lw",
]  

#labels for display 
VARIABLE_LABELS = { 
    "air_temp": "Air Temperature (°C)",
    "relative_humidity": "Relative Humidity (%)",
    "snow_depth": "Snow Depth (cm)",
    "volt": "Voltage (V)",
    "outgoing_radiation_sw": "Outgoing Shortwave Radiation (W/m²)",
    "solar_radiation": "Incoming Shortwave Radiation (W/m²)",
    "photosynthetically_active_radiation": "Photosynthetically Active Radiation (µmol/m²/s)",
    "incoming_radiation_lw": "Incoming Longwave Radiation (W/m²)",
    "outgoing_radiation_lw": "Outgoing Longwave Radiation (W/m²)",
}

## Site metadata, get from Synpotic  
SITE_INFO = {
    "UUSBP": {"Snowbasin Snow Study Plot": "UUSBP", "lat": 41.19574, "lon": -111.87014, "elevation": 8308},
    "UUWPP": {"Wasatch Peaks Ranch Snow Study Plot": "UUWPP", "lat": 41.08693, "lon": -111.83258, "elevation": 7780},
    "ATH20": {"Atwater Snow Study Plot": "ATH20", "lat": 40.59148, "lon": -111.63778, "elevation": 8765},
    "UUSSD": {"Sundance Resort Snow Study Plot": "UUSSD", "lat": 40.38076, "lon": -111.59421, "elevation": 7165},
} 

## set colors for plot
SITE_COLORS = {
    "UUSBP": "#4B4997",
    "UUWPP": "#B0C2D7",
    "ATH20": "#4385C5",
    "UUSSD": "#295485",
}

## Variable-specific color schemes (low to high)
VARIABLE_COLOR_SCHEMES = {
    "snow_depth": {"low": (173, 216, 230), "high": (25, 25, 112)},  # light blue to dark blue
    "air_temp": {"low": (70, 130, 180), "high": (205, 92, 92)},  # steel blue to indian red
    "relative_humidity": {"low": (144, 238, 144), "high": (34, 139, 34)},  # light green to forest green
    "solar_radiation": {"low": (255, 250, 205), "high": (204, 102, 0)},  # light yellow to dark orange
    "incoming_radiation_lw": {"low": (255, 250, 205), "high": (204, 102, 0)},  # light yellow to dark orange
    "outgoing_radiation_lw": {"low": (255, 250, 205), "high": (204, 102, 0)},  # light yellow to dark orange
    "outgoing_radiation_sw": {"low": (255, 250, 205), "high": (204, 102, 0)},  # light yellow to dark orange
    "photosynthetically_active_radiation": {"low": (255, 250, 205), "high": (204, 102, 0)},  # light yellow to dark orange
    "volt": {"low": (173, 216, 230), "high": (25, 25, 112)},  # light blue to dark blue (default)
}