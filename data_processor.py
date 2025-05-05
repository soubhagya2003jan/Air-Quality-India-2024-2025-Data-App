import pandas as pd
import numpy as np
from datetime import datetime

def load_and_process_data(file_path):

    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Handle any missing values
    df = df.dropna(subset=['value', 'lat', 'lon'])
    
    return df

def filter_data_by_date_range(df, start_date, end_date):

    
    if not isinstance(start_date, datetime):
        start_date = pd.to_datetime(start_date)
    
    if not isinstance(end_date, datetime):
        end_date = pd.to_datetime(end_date)
    
    
    end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1)
    
    #
    return df[(df['date'] >= start_date) & (df['date'] < end_date)]

def filter_data_by_location(df, locations):
 
    if not locations:
        return df  
    
    return df[df['location'].isin(locations)]

def filter_data_by_parameter(df, parameters):

    if isinstance(parameters, str):
        parameters = [parameters]
    
    return df[df['parameter'].isin(parameters)]

def aggregate_data_for_time_series(df, parameter, freq='D'):

    
    param_df = df[df['parameter'] == parameter].copy()
    
    
    grouped = param_df.groupby(['date', 'location'])['value'].mean().reset_index()
    
    return grouped

def aggregate_data_for_comparison(df, parameter):

    
    param_df = df[df['parameter'] == parameter].copy()
    
    
    grouped = param_df.groupby('location').agg({
        'value': ['mean', 'min', 'max']
    }).reset_index()
    
    
    grouped.columns = ['location', 'mean', 'min', 'max']
    
    return grouped

def prepare_correlation_data(df, param1, param2):

    
    df1 = df[df['parameter'] == param1].copy()
    df1 = df1.rename(columns={'value': param1})
    df1 = df1[['date', 'location', param1]]
    
    
    df2 = df[df['parameter'] == param2].copy()
    df2 = df2.rename(columns={'value': param2})
    df2 = df2[['date', 'location', param2]]
    
    
    merged = pd.merge(df1, df2, on=['date', 'location'], how='inner')
    
    return merged
