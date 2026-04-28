##this is data file for app.py to create a Streamlit dashboard. -Josae Samp

#import packages
import os
os.environ.setdefault("POLARS_SKIP_CPU_CHECK", "1")
import polars as pl
import plotly.express as px
from datetime import datetime, timezone
from config import STATIONS, VARIABLES, API_TOKEN, SITE_COLORS, VARIABLE_LABELS, VARIABLE_COLOR_SCHEMES
os.environ.setdefault("SYNOPTIC_TOKEN", API_TOKEN) #very important for synoptic data pull
import synoptic 
import folium
from config import SITE_INFO

##MAIN DATA PLOT##

def load_synoptic_data():
    start = datetime(2025, 10, 1) #aribtrary start date
    end = datetime.utcnow() #end current time

    ts = synoptic.TimeSeries( #pull synoptic time series data 
        token=API_TOKEN, #use token (redunancy incase not set in enviroment)
        stid=",".join(STATIONS), #join all stations from config.py
        start=start.strftime("%Y%m%d%H%M"), #start date structure 
        end=end.strftime("%Y%m%d%H%M"), #end state strucutre 
        vars=",".join(VARIABLES), #all variables from config.py
        units="metric", #metric units
        verbose=False,
    )

    return ts.df() #return as data frame

#create function to plot variable with controls for site, variable, and time range to be used in app.py
def plot_variable(df, variable, sites, start_date, end_date): 
    df = df.filter(pl.col("variable") == variable) #filter by variable
    df = df.filter(pl.col("stid").is_in(sites)) #filter by site selection 
    df = df.filter(pl.col("value").is_not_null()) #filter to avoid errors in plotting if null values 

    # Convert snow depth from mm to cm
    if variable == "snow_depth":
        df = df.with_columns(pl.col("value") / 10)

    # Filter by date range
    start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_dt = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
    df = df.filter(pl.col("date_time").is_between(start_dt, end_dt)) #filtered data frame within time range

    #reducacny check for empty data frame after filtering, if empty return a blank figure with message instead of error
    pdf = df.to_pandas() #convert to pandas for plotly
    if pdf.empty:
        fig = px.line(
            title=f"No data available for {VARIABLE_LABELS[variable]}"
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(
                    text="No valid observations are available for the selected variable/site combination.",
                    x=0.5,
                    y=0.5,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=14)
                )
            ]
        )
        return fig
#FIGURE CREATION USING selected variable, sites, and time range.
    fig = px.line( #line
        pdf, #df 
        x="date_time", #x is date time
        y="value", # y is the selected varibale value
        color="stid", #color by site
        color_discrete_map=SITE_COLORS,
        markers=True,
        title=f"{VARIABLE_LABELS[variable]}" #title
    )

    fig.update_traces(marker=dict(size=3))

    # Remove gridlines and style axis lines
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor="lightgrey",
        linewidth=1,
        ticks="outside",
        tickcolor="lightgrey",
        title_text="Date and Time"
    )
    fig.update_yaxes(
        showgrid=False,
        showline=True,
        linecolor="lightgrey",
        linewidth=1,
        ticks="outside",
        tickcolor="lightgrey",
        title_text=f"{VARIABLE_LABELS[variable]}"
    )

    return fig 


##MAP##  

#define function to make map in app.py with current conditions for coloring and popups with site metadata from config.py
def make_site_map(df, variable):
    # Get current stats for coloring
    stats_df = get_current_stats(df, variable) 
    # Get min and max values for normalization for coloring on map for visualization of current condiitons
    values = stats_df['value'].to_list()
    values = [v for v in values if v is not None]
    if values:
        min_val = min(values)
        max_val = max(values)
    else:
        min_val = max_val = 0
    #center map on the average of all sites lat and long 
    center_lat = sum(site["lat"] for site in SITE_INFO.values()) / len(SITE_INFO)
    center_lon = sum(site["lon"] for site in SITE_INFO.values()) / len(SITE_INFO)

    #create map, location (defined above), zoom level, add scale control, tiles set below 
    m = folium.Map(location=[center_lat, center_lon], zoom_start=8, control_scale=True, tiles=None)
    #set tiles 
    #topographic as default
    topo = folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Topo",
        overlay=False,
        control=True,
        show=True
    )
    topo.add_to(m) #add to map 

    #add satellite as option
    satellite = folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite",
        overlay=False,
        control=True,
        show=False
    ) 
    satellite.add_to(m) #add to map

    #information for popups and markers 
    for site_name, site in SITE_INFO.items():
        # Get info for popups, site name, lat, long, and elevation 
        display_name = [k for k in site.keys() if k not in ["lat", "lon", "elevation"]][0]
        elevation = site["elevation"]
        
        # Get current value for this site
        site_stats = stats_df.filter(pl.col('stid') == site_name)#filter by site name
        if site_stats.is_empty() or site_stats['value'][0] is None: #IF NULL or 0 set color to gray
            color = 'gray'
            fill_color = 'gray'
        else: #if else add color by current conditions 
            val = site_stats['value'][0]
            # Normalize value to 0-1 for coloring 
            if max_val == min_val:
                norm = 0.5
            else:
                norm = (val - min_val) / (max_val - min_val)
            
            # Get color scheme for variable, default to blue
            color_scheme = VARIABLE_COLOR_SCHEMES.get(variable, {"low": (173, 216, 230), "high": (25, 25, 112)})
            low_rgb = color_scheme["low"]
            high_rgb = color_scheme["high"]
            
            # Interpolate between low and high colors
            r = int(low_rgb[0] + (high_rgb[0] - low_rgb[0]) * norm)
            g = int(low_rgb[1] + (high_rgb[1] - low_rgb[1]) * norm)
            b = int(low_rgb[2] + (high_rgb[2] - low_rgb[2]) * norm)
            color = f'#{r:02x}{g:02x}{b:02x}'
            fill_color = color
        #create popup text for site metadata 
        popup_text = f"{display_name}<br>Latitude: {site['lat']}<br>Longitude: {site['lon']}<br>Elevation: {elevation} ft"
        #create marker with colors as defined above based on current conditions 
        folium.CircleMarker(
            location=[site["lat"], site["lon"]],
            radius=10, #size
            color=color, #color as defined above 
            fill=True,
            fill_color=fill_color,
            fill_opacity=0.9, #a bit transparent 
            popup=popup_text, #add popup text 
            tooltip=display_name, #show site name on hover
        ).add_to(m) #add to map 

    folium.LayerControl().add_to(m) #all the controls to the map 
    return m #return the map to be used in app.py

##current stats for display 
def get_current_stats(df, variable): #define the function 
    sub = (
        df.filter(pl.col("variable") == variable) #control for variable will select was is displayed for current conditions
          .filter(pl.col("value").is_not_null()) #will break and will display error if null
          .sort("date_time")
    )

    latest = sub.group_by("stid", maintain_order=True).tail(1) #keep latest observation for each site, maintain order

    # Convert snow depth from mm to cm
    if variable == "snow_depth":
        latest = latest.with_columns(pl.col("value") / 10)

    return latest.select(["stid", "date_time", "value"]) #return site name, date and time, and value of selected variable
