# data_processor.py
import pandas as pd
from data_store import data_store

def calculate_metrics(df):
    """Calculate basic metrics from the data"""
    metrics = {
        'total_clicks': df['clicks'].sum(),
        'total_impressions': df['impressions'].sum(),
        'avg_ctr': (df['clicks'].sum() / df['impressions'].sum()) * 100,
        'avg_position': df['position'].mean(),
        'total_pages': df['page'].nunique()
    }
    return metrics

def get_time_series_data(df, metric='clicks', freq='D'):
    """Aggregate data by time frequency"""
    return df.groupby([pd.Grouper(key='date', freq=freq), 'type'])[metric].sum().reset_index()

COLORS = ['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', 
          '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921']