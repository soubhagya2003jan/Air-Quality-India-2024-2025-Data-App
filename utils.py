import pandas as pd
import plotly.express as px
import numpy as np

def get_unique_values(df, column):
    """
    Get unique values from a DataFrame column.
    
    Args:
        df: DataFrame containing the data
        column: Column name to get unique values from
        
    Returns:
        List of unique values
    """
    return df[column].unique().tolist()

def get_parameter_info(parameter, df=None):
    """
    Get descriptive information for a parameter.
    
    Args:
        parameter: The parameter to get information for
        df: Optional DataFrame to extract units from
        
    Returns:
        Dictionary containing parameter information
    """
    # Define parameter information dictionary
    parameter_info = {
        'pm25': {
            'title': 'PM2.5',
            'unit': 'µg/m³',
            'description': 'Fine particulate matter with diameter less than 2.5 micrometers',
            'threshold': {'good': 12, 'moderate': 35.4, 'unhealthy': 55.4, 'very_unhealthy': 150.4}
        },
        'pm1': {
            'title': 'PM1',
            'unit': 'µg/m³',
            'description': 'Particulate matter with diameter less than 1 micrometer',
            'threshold': {'good': 10, 'moderate': 25, 'unhealthy': 50, 'very_unhealthy': 100}
        },
        'pm10': {
            'title': 'PM10',
            'unit': 'µg/m³',
            'description': 'Particulate matter with diameter less than 10 micrometers',
            'threshold': {'good': 54, 'moderate': 154, 'unhealthy': 254, 'very_unhealthy': 354}
        },
        'co': {
            'title': 'Carbon Monoxide',
            'unit': 'ppb',
            'description': 'Carbon monoxide concentration',
            'threshold': {'good': 4.4, 'moderate': 9.4, 'unhealthy': 12.4, 'very_unhealthy': 15.4}
        },
        'no': {
            'title': 'Nitric Oxide',
            'unit': 'ppb',
            'description': 'Nitric oxide concentration',
            'threshold': {'good': 40, 'moderate': 80, 'unhealthy': 180, 'very_unhealthy': 280}
        },
        'no2': {
            'title': 'Nitrogen Dioxide',
            'unit': 'ppb',
            'description': 'Nitrogen dioxide concentration',
            'threshold': {'good': 53, 'moderate': 100, 'unhealthy': 360, 'very_unhealthy': 649}
        },
        'o3': {
            'title': 'Ozone',
            'unit': 'µg/m³',
            'description': 'Ozone concentration',
            'threshold': {'good': 54, 'moderate': 70, 'unhealthy': 85, 'very_unhealthy': 105}
        },
        'so2': {
            'title': 'Sulfur Dioxide',
            'unit': 'ppb',
            'description': 'Sulfur dioxide concentration',
            'threshold': {'good': 35, 'moderate': 75, 'unhealthy': 185, 'very_unhealthy': 304}
        },
        'temperature': {
            'title': 'Temperature',
            'unit': '°C',
            'description': 'Ambient temperature',
            'threshold': {'cold': 0, 'cool': 15, 'moderate': 25, 'hot': 30}
        },
        'pressure': {
            'title': 'Atmospheric Pressure',
            'unit': 'hPa',
            'description': 'Atmospheric pressure',
            'threshold': {'low': 980, 'normal': 1013, 'high': 1030}
        },
        'relativehumidity': {
            'title': 'Relative Humidity',
            'unit': '%',
            'description': 'Relative humidity',
            'threshold': {'dry': 30, 'comfortable': 50, 'humid': 70}
        },
        'wind_speed': {
            'title': 'Wind Speed',
            'unit': 'm/s',
            'description': 'Wind speed',
            'threshold': {'calm': 1, 'light': 3, 'moderate': 7, 'strong': 10}
        },
        'wind_direction': {
            'title': 'Wind Direction',
            'unit': 'deg',
            'description': 'Wind direction in degrees',
            'threshold': {}
        },
        'um003': {
            'title': 'Ultrafine Particles',
            'unit': 'count/cm³',
            'description': 'Ultrafine particles concentration',
            'threshold': {'low': 1000, 'moderate': 10000, 'high': 50000}
        }
    }
    
    
    if parameter not in parameter_info:
        default_info = {
            'title': parameter.replace('_', ' ').title(),
            'unit': '',
            'description': f'{parameter.replace("_", " ").title()} measurement',
            'threshold': {}
        }
        if df is not None:
            try:
                
                unit_data = df[df['parameter'] == parameter]['unit'].unique()
                if len(unit_data) > 0:
                    default_info['unit'] = unit_data[0]
            except:
                pass
        return default_info
    
    
    if df is not None and parameter not in parameter_info:
        try:
            unit_data = df[df['parameter'] == parameter]['unit'].unique()
            if len(unit_data) > 0:
                default_info['unit'] = unit_data[0]
        except:
            pass
    
    return parameter_info[parameter]

def get_color_scale(parameter, as_rgb_tuples=False):
    """
    Get appropriate color scale for a parameter.
    
    Args:
        parameter: The parameter to get color scale for
        as_rgb_tuples: Whether to return as RGB tuples (for pydeck)
        
    Returns:
        Color scale appropriate for the parameter
    """
    
    pollution_params = ['pm25', 'pm1', 'pm10', 'co', 'no', 'no2', 'o3', 'so2', 'um003']
    temperature_params = ['temperature']
    moisture_params = ['relativehumidity']
    pressure_params = ['pressure']
    wind_params = ['wind_speed', 'wind_direction']
    
    if parameter in pollution_params:
        if as_rgb_tuples:
            return [
                (0, 150, 0),  # Green (low pollution)
                (255, 255, 0),  # Yellow (moderate)
                (255, 150, 0),  # Orange (unhealthy)
                (255, 0, 0),  # Red (very unhealthy)
                (150, 0, 150)   # Purple (hazardous)
            ]
        return "Reds"
    
    elif parameter in temperature_params:
        if as_rgb_tuples:
            return [
                (0, 0, 255),  # Blue (cold)
                (0, 255, 255),  # Cyan (cool)
                (0, 255, 0),  # Green (moderate)
                (255, 255, 0),  # Yellow (warm)
                (255, 0, 0)   # Red (hot)
            ]
        return "RdYlBu_r"
    
    elif parameter in moisture_params:
        if as_rgb_tuples:
            return [
                (255, 170, 0),  # Orange (dry)
                (0, 255, 0),  # Green (comfortable)
                (0, 0, 255)   # Blue (humid)
            ]
        return "Blues"
    
    elif parameter in pressure_params:
        if as_rgb_tuples:
            return [
                (255, 0, 0),  # Red (low pressure)
                (255, 255, 255),  # White (normal pressure)
                (0, 0, 255)   # Blue (high pressure)
            ]
        return "RdBu"
    
    elif parameter in wind_params:
        if as_rgb_tuples:
            return [
                (0, 255, 0),  # Green (calm)
                (255, 255, 0),  # Yellow (light)
                (255, 150, 0),  # Orange (moderate)
                (255, 0, 0)   # Red (strong)
            ]
        return "YlOrRd"
    
    # Default color scale
    if as_rgb_tuples:
        return [
            (0, 0, 255),  # Blue (low)
            (0, 255, 0),  # Green (medium)
            (255, 255, 0),  # Yellow (high)
            (255, 0, 0)   # Red (very high)
        ]
    return "Viridis"

def calculate_aqi_stats(df, parameter):
    """
    Calculate statistics for the selected parameter.
    
    Args:
        df: DataFrame containing filtered air quality data
        parameter: The air quality parameter to calculate statistics for
        
    Returns:
        Dictionary containing statistics
    """
    
    param_df = df[df['parameter'] == parameter].copy()
    
    
    param_info = get_parameter_info(parameter, df)
    
    
    stats = {
        'mean_value': param_df['value'].mean(),
        'max_value': param_df['value'].max(),
        'min_value': param_df['value'].min(),
        'unit': param_info['unit'],
        'location_count': param_df['location'].nunique()
    }
    
    return stats

def classify_aqi_level(value, parameter):
    """
    Classify AQI value into appropriate level.
    
    Args:
        value: The AQI value to classify
        parameter: The parameter used for classification
        
    Returns:
        Classification string and color
    """
   
    param_info = get_parameter_info(parameter)
    thresholds = param_info['threshold']
    
    
    if parameter in ['pm25', 'pm10', 'co', 'no2', 'o3', 'so2']:
        if value <= thresholds.get('good', 0):
            return "Good", "#00E400"
        elif value <= thresholds.get('moderate', 0):
            return "Moderate", "#FFFF00"
        elif value <= thresholds.get('unhealthy', 0):
            return "Unhealthy for Sensitive Groups", "#FF7E00"
        elif value <= thresholds.get('very_unhealthy', 0):
            return "Unhealthy", "#FF0000"
        else:
            return "Hazardous", "#99004C"
    
    
    elif parameter == 'temperature':
        if value <= thresholds.get('cold', 0):
            return "Cold", "#0000FF"
        elif value <= thresholds.get('cool', 0):
            return "Cool", "#00FFFF"
        elif value <= thresholds.get('moderate', 0):
            return "Moderate", "#00FF00"
        elif value <= thresholds.get('hot', 0):
            return "Warm", "#FFFF00"
        else:
            return "Hot", "#FF0000"
    
    
    elif parameter == 'relativehumidity':
        if value <= thresholds.get('dry', 0):
            return "Dry", "#FFA500"
        elif value <= thresholds.get('comfortable', 0):
            return "Comfortable", "#00FF00"
        else:
            return "Humid", "#0000FF"
    
    # Default
    return "Normal", "#00FF00"
