#imports
import streamlit as st
from streamlit_folium import st_folium
from data import load_synoptic_data, plot_variable, make_site_map, get_current_stats
from config import VARIABLE_LABELS, SITE_COLORS
from datetime import datetime 
from RadiativeForcing import df_11am, plot_albedo

#set webpage title 
st.set_page_config(page_title="Wasatch Snow Study Plot Dashboard", layout="wide")

#CSS website styling   
primaryColor="#6BA7CC"
st.markdown("""
    <style>
    /* Main app background */
    .stApp {
        background-color: #f5faff;
    }

    /* Sidebar (control panel) */
    section[data-testid="stSidebar"] {
        background-color: #d6ecff;
    }

    /* Main body text */
    .stApp,
    .stApp p,
    .stApp label,
    .stApp span {
        font-family: 'Segoe UI', sans-serif;
        text-align: center;
    }

    /* Wider main page content */
    section[data-testid="stAppViewContainer"] .block-container {
        max-width: 1400px;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Subheaders and section titles */
    .stApp [data-testid="stHeading"] h2,
    .stApp [data-testid="stHeading"] h3 {
        color: #032B56 !important;
        background-color: #d6ecff;
        padding: 10px 24px;
        border-radius: 10px;
        display: block;
        width: 100%;
        box-sizing: border-box;
        margin-bottom: 10px;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 600;
        text-align: center;
    }
    .stApp [data-testid="stHeading"] h2 a,
    .stApp [data-testid="stHeading"] h3 a,
    .stApp [data-testid="stHeading"] a {
        display: none !important;
        color: inherit !important;
        text-decoration: none !important;
        pointer-events: none !important;
        cursor: default !important;
    }
    /* Metric values */
    [data-testid="stMetric"] {
        text-align: left;
    }
    [data-testid="stMetricValue"] {
        color: #00224B;
    }

    [data-testid="stMetricLabel"] {
        color: #032B56;
    }

    </style>
""", unsafe_allow_html=True)


# App title and description 
st.markdown(
    '<h1 style="color: #0b3a66; background-color: #d6ecff; padding: 12px 24px; border-radius: 10px; display: block; width: 100%; box-sizing: border-box; margin-bottom: 12px; font-family: \'Segoe UI\', sans-serif; font-weight: 700; text-align: center;">Wasatch Snow Study Plot Dashboard<br><span style="color: #707271; font-size: 0.8em; font-weight: 600;">SnowHydro Lab - University of Utah</span></h1>',
    unsafe_allow_html=True,
)
st.text("This dashboard provides historic and real-time data from snow study plots across the Wasatch Mountains, Utah. Data is raw and real-time without " \
"any processing or quality control. Use the controls in the sidebar to select variables, sites, and period of interest.")

# Load data
df = load_synoptic_data()

##SIDEBAR CONTROLS FOR VARIABLE, SITE, AND TIMES##

# Sidebar controls for variables
st.sidebar.header("Variable Selection") #header

#variable selection dropdown list with lables from config.py
variable = st.sidebar.selectbox(
    "Variable",
    list(VARIABLE_LABELS.keys()),
    index=2,  # Default to snow_depth
    format_func=lambda x: VARIABLE_LABELS[x]
)

#Sidebar controls for site selection
st.sidebar.header("Site Selection")

all_sites = df["stid"].unique().to_list() #add list of each site to dropdown list

#add two modes for one site or multiple site selections, will have different dropdown options
mode = st.sidebar.radio(
    "Mode Selection",
    ["One site", "Multiple sites"],
    key="display_mode"
)
if mode == "One site":
    sites = [st.sidebar.selectbox("Site Selection", all_sites, key="one_site")]
else:
    sites = st.sidebar.multiselect(
        "Site Selection",
        all_sites,
        default=all_sites,  # all selected by default
        key="Multiple_sites"
    ) 

#Sidebar controls for time selection
st.sidebar.header("Time Selection")
#start date selector
start_date = st.sidebar.date_input(
    "Start Date",
    value=datetime(2025, 10, 1),
    key="start_date"
)
#end date selector 
end_date = st.sidebar.date_input(
    "End Date",
    value=datetime.utcnow().date(),
    key="end_date"
)

## MAIN WEBSITE CONTENT ##

col1, col2 = st.columns(2) # two columns one for the map, other for current conditions 
#add Folium map ot col1
with col1:
    site_map = make_site_map(df, variable)
    st_folium(site_map, width='100%', height=400) #set size
#add current conditions to col2
with col2:
    stats_df = get_current_stats(df, variable) #pull from config.py
    html = f'''
<div style="background-color: #FFFFFF; padding: 20px; border-radius: 0.1px; width: 100%; box-sizing: border-box;">
<h3 style='color:#032B56; margin-bottom: 0.8rem; font-family: "Segoe UI", sans-serif; font-weight: 600; text-align: left; font-size: 2.2em;'>Current Conditions - {VARIABLE_LABELS[variable]}</h3>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
'''
    for i, row in enumerate(stats_df.iter_rows(named=True)):
        if i < 4:
            html += f'''
<div style="text-align: left;">
<div style="font-weight: 600; color: #032B56; font-size: 1.2em;">{row["stid"]}</div>
<div style="font-size: 2em; color: #00224B;">{row['value']:.2f}</div>
</div>
'''
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

##MAIN PLOT##

fig = plot_variable(df, variable, sites, start_date, end_date) #figure with controls 
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'responsive': True}, key ="main_plot")

#RADIATIVE FORCING SECTION##
st.subheader("Broadband Albedo at All Sites") 
st.write(
    "Albedo measures the reflectivity of snow, calculated as the ratio of outgoing shortwave radiation to incoming shortwave radiation. "
    "This plot shows daily broadband albedo at 11am, when there is sufficient incoming solar radiation for the calculation. "
    "Snow albedo ranges between 0.4 and 0.9, with fresh snow typically around 0.8-0.9. "
    "This data can be used as a check for when sites are snow free, albedo values will be <0.3. "
    "Measurements of albedo provide insight into snowpack energy balance and melt processes."
)

fig_albedo = plot_albedo(df_11am) #figure with controls 
st.plotly_chart(fig_albedo, use_container_width=True, config={'displayModeBar': True, 'responsive': False}, key ="albedo_plot")


##FOOTER##
#Make a footer to credit Synoptic 
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #e6f2ff;
        color: navy;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        z-index: 9999;
    }

    /* Prevent content from being hidden behind footer */
    .main {
        padding-bottom: 60px;
    }
    </style>

    <div class="footer"> 
        Josae Samp - University of Utah - 2026 | Data and weather observations aggregated by 
        <a href="https://synopticdata.com/" target="_blank" style="color: navy; text-decoration: underline;">
            Synoptic Data
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
