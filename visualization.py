import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pydeck as pdk

from data_processor import aggregate_data_for_time_series, aggregate_data_for_comparison, prepare_correlation_data
from utils import get_parameter_info, get_color_scale

def create_time_series_chart(df, parameter):
    """
    Create a time series line chart for the selected parameter.
    
    Args:
        df: DataFrame containing filtered air quality data
        parameter: The air quality parameter to visualize
        
    Returns:
        Plotly figure object
    """
    
    ts_data = aggregate_data_for_time_series(df, parameter)
    
    
    param_info = get_parameter_info(parameter, df)
    
    
    template = 'plotly_white'
    
    # Create line chart
    fig = px.line(
        ts_data, 
        x='date', 
        y='value', 
        color='location',
        title=f'{param_info["title"]} Over Time',
        labels={
            'date': 'Date',
            'value': f'{param_info["title"]} ({param_info["unit"]})',
            'location': 'Location'
        },
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template=template
    )
    
    # Customize layout
    fig.update_layout(
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#E9ECEF'
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#E9ECEF'
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor='white'
    )
    
    
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def create_bar_chart(df, parameter):
    """
    Create a bar chart comparing parameter values across locations.
    
    Args:
        df: DataFrame containing filtered air quality data
        parameter: The air quality parameter to visualize
        
    Returns:
        Plotly figure object
    """
   
    comp_data = aggregate_data_for_comparison(df, parameter)
    
    
    param_info = get_parameter_info(parameter, df)
    
    
    comp_data = comp_data.sort_values(by='mean', ascending=False)
    
    
    template = 'plotly_white'
    
    # Create bar chart
    fig = px.bar(
        comp_data,
        x='location',
        y='mean',
        error_y=comp_data['max']-comp_data['mean'],
        error_y_minus=comp_data['mean']-comp_data['min'],
        title=f'Average {param_info["title"]} by Location',
        labels={
            'location': 'Location',
            'mean': f'Average {param_info["title"]} ({param_info["unit"]})'
        },
        color='mean',
        color_continuous_scale=get_color_scale(parameter),
        template=template
    )
    
    # Customize layout
    fig.update_layout(
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            tickangle=45,
            gridcolor='#E9ECEF'
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#E9ECEF'
        ),
        coloraxis_colorbar=dict(
            title=f'{param_info["title"]}',
            title_side='right'
        ),
        margin=dict(l=40, r=40, t=40, b=100),
        plot_bgcolor='white'
    )
    
    return fig

def create_scatter_plot(df, param1, param2):
    """
    Create a scatter plot to analyze correlation between two parameters.
    
    Args:
        df: DataFrame containing filtered air quality data
        param1: First parameter for correlation
        param2: Second parameter for correlation
        
    Returns:
        Plotly figure object
    """
    # Prepare data for correlation analysis
    corr_data = prepare_correlation_data(df, param1, param2)
    
    
    param1_info = get_parameter_info(param1, df)
    param2_info = get_parameter_info(param2, df)
    
    # Create scatter plot
    fig = px.scatter(
        corr_data,
        x=param1,
        y=param2,
        color='location',
        title=f'Correlation between {param1_info["title"]} and {param2_info["title"]}',
        labels={
            param1: f'{param1_info["title"]} ({param1_info["unit"]})',
            param2: f'{param2_info["title"]} ({param2_info["unit"]})',
            'location': 'Location'
        },
        hover_data=['date'],
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template='plotly_white',
        opacity=0.7
    )
    
    # Add trendline
    fig.update_traces(
        marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey')),
    )
    
    # Add a best fit line
    fig.update_layout(
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#E9ECEF'
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='#E9ECEF'
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor='white'
    )
    
    # Add trendline if there are enough points
    if len(corr_data) > 5:
        fig.update_layout(
            shapes=[
                dict(
                    type='line',
                    xref='x', yref='y',
                    x0=corr_data[param1].min(),
                    y0=np.polyval(np.polyfit(corr_data[param1], corr_data[param2], 1), corr_data[param1].min()),
                    x1=corr_data[param1].max(),
                    y1=np.polyval(np.polyfit(corr_data[param1], corr_data[param2], 1), corr_data[param1].max()),
                    line=dict(color='rgba(78, 121, 167, 0.5)', width=2, dash='dash')
                )
            ]
        )
    
    return fig

def create_map_visualization(df, parameter):
    """
    Create a map visualization of the air quality data.
    
    Args:
        df: DataFrame containing air quality data with lat, lon coordinates
        parameter: The parameter being visualized
        
    Returns:
        PyDeck visualization object
    """
    # Get parameter information with dynamic units from the original DataFrame
    param_info = get_parameter_info(parameter, df)
    
    
    min_value = df['value'].min()
    max_value = df['value'].max()
    df['point_size'] = 5000 * ((df['value'] - min_value) / (max_value - min_value) + 0.5)
    
    
    color_scale = get_color_scale(parameter, as_rgb_tuples=True)
    
    
    df['color_r'] = 0
    df['color_g'] = 0
    df['color_b'] = 0
    
    # Normalize values
    normalized_values = (df['value'] - min_value) / (max_value - min_value) if max_value > min_value else np.array([0.5] * len(df))
    
    # Simple linear interpolation
    if 'pm' in parameter or 'co' in parameter or 'no' in parameter or 'so2' in parameter or 'o3' in parameter:
        # For pollutants: green (low) to red (high)
        df['color_r'] = (normalized_values * 255).astype(int)
        df['color_g'] = ((1 - normalized_values) * 255).astype(int)
        df['color_b'] = 50
    else:
        # For other parameters: blue (low) to yellow (high)
        df['color_r'] = (normalized_values * 255).astype(int)
        df['color_g'] = (normalized_values * 255).astype(int)
        df['color_b'] = ((1 - normalized_values) * 255).astype(int)
    
    # Create layers
    layers = [
        
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["lon", "lat"],
            get_radius="point_size",
            get_fill_color=["color_r", "color_g", "color_b", 180],
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_min_pixels=5,
            radius_max_pixels=50,
        )
    ]
    
    
    center_lat = df['lat'].mean()
    center_lon = df['lon'].mean()
    
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=4,
        pitch=0,
    )
    
    
    tooltip = {
        "html": "<b>{location}</b><br>"
                + param_info['title'] + ": {value} " + param_info['unit'],
        "style": {
            "backgroundColor": "white",
            "color": "black"
        }
    }
    
    # light Theme
    map_style = "light"
    
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style=map_style,
        tooltip=tooltip
    )
    
    return deck
