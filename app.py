import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import pydeck as pdk

from data_processor import load_and_process_data, filter_data_by_date_range, filter_data_by_location, filter_data_by_parameter
from visualization import create_time_series_chart, create_scatter_plot, create_bar_chart, create_map_visualization
from utils import get_parameter_info, get_color_scale, get_unique_values, calculate_aqi_stats

# Page configuration
st.set_page_config(page_title="Air Quality Dashboard",
                   page_icon="ℹ️",
                   layout="wide",
                   initial_sidebar_state="expanded")


# Load data
@st.cache_data(
    ttl=3600,
    show_spinner="Loading air quality data...")  # Cache data for 1 hour
def load_data():
    try:
        # Load data using the data processor
        return load_and_process_data("attached_assets/Compressed_AQI.csv")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


# Main title and description
st.image("attached_assets/air-pollution.png", width=50)
st.title("Air Quality Dashboard")
st.markdown("""
This dashboard visualizes air quality data from various locations. 
Explore trends, correlations, and geographical distributions of air quality parameters.
""")

# Load data
with st.spinner("Loading data..."):
    df = load_data()

if df is None:
    st.error(
        "Failed to load data. Please check if the data file exists and is valid."
    )
    st.stop()

# Sidebar title and filters
with st.sidebar:
    # Add title with emoji icon for data analysis, centered
    st.markdown("<h1 style='text-align: center;'>ℹ️ Air Quality Analysis</h1>",
                unsafe_allow_html=True)
    st.markdown("---")
    st.header("Filters")

    # Date range selector
    st.subheader("Date Range")
    min_date = pd.to_datetime(df['date']).min().date()
    max_date = pd.to_datetime(df['date']).max().date()

    start_date = st.date_input("Start Date",
                               min_date,
                               min_value=min_date,
                               max_value=max_date)
    end_date = st.date_input("End Date",
                             max_date,
                             min_value=min_date,
                             max_value=max_date)

    if start_date > end_date:
        st.error("End date must be after start date")
        st.stop()

    # Location filter
    st.subheader("Location")
    all_locations = sorted(get_unique_values(df, 'location'))
    selected_locations = st.multiselect("Select locations",
                                        all_locations,
                                        default=all_locations[:5])

    # Parameter filter
    st.subheader("Parameter")
    all_parameters = sorted(get_unique_values(df, 'parameter'))
    selected_parameter = st.selectbox(
        "Select parameter",
        all_parameters,
        index=all_parameters.index('pm25') if 'pm25' in all_parameters else 0)

    # For correlation analysis
    st.subheader("Correlation Analysis")
    if selected_parameter:
        other_parameters = [
            p for p in all_parameters if p != selected_parameter
        ]
        correlation_parameter = st.selectbox(
            "Compare with parameter",
            other_parameters,
            index=0 if other_parameters else None)

# Filter data based on selections
filtered_df = df.copy()
filtered_df = filter_data_by_date_range(filtered_df, start_date, end_date)
filtered_df = filter_data_by_location(filtered_df, selected_locations)
parameter_filtered_df = filter_data_by_parameter(filtered_df,
                                                 selected_parameter)

# Dashboard layout
if parameter_filtered_df.empty:
    st.warning(f"No data available for the selected filters.")
    st.stop()

# Display key statistics
st.subheader("Key Statistics")
stats_cols = st.columns(4)

# Calculate statistics
stats = calculate_aqi_stats(parameter_filtered_df, selected_parameter)

# Display statistics
with stats_cols[0]:
    st.metric("Average Value", f"{stats['mean_value']:.2f} {stats['unit']}")
with stats_cols[1]:
    st.metric("Max Value", f"{stats['max_value']:.2f} {stats['unit']}")
with stats_cols[2]:
    st.metric("Min Value", f"{stats['min_value']:.2f} {stats['unit']}")
with stats_cols[3]:
    st.metric("Locations", f"{stats['location_count']}")

# Display visualizations in tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["Trends", "Comparison", "Correlation", "Map"])

with tab1:
    st.subheader(f"{selected_parameter.upper()} Trends Over Time")
    st.markdown(
        f"Displaying trends for {get_parameter_info(selected_parameter)['description']}"
    )
    time_series_chart = create_time_series_chart(parameter_filtered_df,
                                                 selected_parameter)
    st.plotly_chart(time_series_chart, use_container_width=True)

with tab2:
    st.subheader(f"{selected_parameter.upper()} Comparison by Location")
    bar_chart = create_bar_chart(parameter_filtered_df, selected_parameter)
    st.plotly_chart(bar_chart, use_container_width=True)

with tab3:
    st.subheader("Parameter Correlation Analysis")

    if correlation_parameter:
        # Filter data for both parameters
        correlation_df = filter_data_by_parameter(
            filtered_df, [selected_parameter, correlation_parameter])

        if not correlation_df.empty:
            scatter_plot = create_scatter_plot(correlation_df,
                                               selected_parameter,
                                               correlation_parameter)
            st.plotly_chart(scatter_plot, use_container_width=True)
        else:
            st.warning(
                "Insufficient data for correlation analysis with selected parameters."
            )
    else:
        st.info("Please select a second parameter for correlation analysis.")

with tab4:
    st.subheader("Geographical Distribution")
    # Prepare data for map
    geo_df = parameter_filtered_df.copy()

    # Group by location and calculate average values for the map
    map_df = geo_df.groupby(['location', 'lat',
                             'lon'])['value'].mean().reset_index()

    # Create map visualization
    map_visualization = create_map_visualization(map_df, selected_parameter)
    st.pydeck_chart(map_visualization)

# Footer
st.markdown("---")
