
## This file is updates on the code to use  use real time synoptic data to calculate albedo 
## Import Libraries##  
#housekeeping 
import os
os.environ.setdefault("POLARS_SKIP_CPU_CHECK", "1")
import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import synoptic
from datetime import datetime
from config import SITE_COLORS, VARIABLES, API_TOKEN
from config import SITE_COLORS, STATIONS, API_TOKEN
os.environ.setdefault("SYNOPTIC_TOKEN", API_TOKEN) #very important for synoptic data pull

#define function to download data
@st.cache_data(ttl=10800, show_spinner=False)
def load_synoptic_data_wide():
    start = datetime(2025, 10, 1)
    end = datetime.utcnow()

    ts = synoptic.TimeSeries(
        token=API_TOKEN,
        stid=",".join(STATIONS),
        start=start.strftime("%Y%m%d%H%M"),
        end=end.strftime("%Y%m%d%H%M"),
        vars=",".join(VARIABLES),
        units="metric",
        verbose=False,
    )

    df = ts.df().to_pandas()
    df_wide = df.pivot_table(
    index=["stid", "date_time"],
    columns="variable",
    values="value",
    aggfunc="first"
).reset_index()

    # Rename columns for clarity 
    column_renames = { 
        'date_time': 'Time Stamp',
        'solar_radiation': 'Incoming BB',
        'outgoing_radiation_sw': 'Reflected BB',
    }
    df_wide = df_wide.rename(columns=column_renames)  

    # Convert 'Time Stamp' to datetime and radiation columns to numeric
    df_wide["Time Stamp"] = pd.to_datetime(df_wide["Time Stamp"], errors="coerce", utc=True)
    df_wide["Incoming BB"] = pd.to_numeric(df_wide["Incoming BB"], errors="coerce")
    df_wide["Reflected BB"] = pd.to_numeric(df_wide["Reflected BB"], errors="coerce")

    # Define broadband albedo and enforce realistic values
    df_wide["BB Albedo"] = np.where(
        df_wide["Incoming BB"] > 0,
        df_wide["Reflected BB"] / df_wide["Incoming BB"],
        np.nan
    )
    df_wide.loc[
        (df_wide["BB Albedo"] < 0.1) | (df_wide["BB Albedo"] > 1),
        "BB Albedo"
    ] = np.nan

    return df_wide

@st.cache_data(ttl=10800, show_spinner=False)
def load_albedo_data():
    df_wide = load_synoptic_data_wide()
    df_wide = df_wide.copy()
    df_wide["Time Stamp"] = df_wide["Time Stamp"].dt.tz_convert("America/Denver")
    return df_wide[df_wide["Time Stamp"].dt.hour == 11]

#define function for plotting albedo to be used in app.py
def plot_albedo(df_wide):
    fig = px.line(
        df_wide,
        x="Time Stamp",
        y="BB Albedo",
        color="stid",  # remove if not in df
        color_discrete_map=SITE_COLORS,
        title="11am Snow Albedo"
    )
    fig.update_traces(marker=dict(size=5))
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
        title_text="Albedo (Unitless)"
    )
    return fig






