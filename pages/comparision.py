# pages/comparison.py
import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from data_processor import COLORS
import pandas as pd
from data_store import data_store

dash.register_page(__name__, path='/comparison', name='Comparison')

layout = html.Div([
    html.H1("Period Comparison Analysis", 
            className="text-center mb-4"),
    
    dbc.Container([
        # Period Selection
        dbc.Row([
            dbc.Col([
                html.H4("Period 1"),
                dcc.DatePickerRange(
                    id='period1-date-range',
                    min_date_allowed=data_store.df['date'].min(),
                    max_date_allowed=data_store.df['date'].max(),
                    start_date=data_store.df['date'].min(),
                    end_date=data_store.df['date'].min() + pd.Timedelta(days=30),
                    className="mb-3"
                )
            ], width=6),
            
            dbc.Col([
                html.H4("Period 2"),
                dcc.DatePickerRange(
                    id='period2-date-range',
                    min_date_allowed=data_store.df['date'].min(),
                    max_date_allowed=data_store.df['date'].max(),
                    start_date=data_store.df['date'].max() - pd.Timedelta(days=30),
                    end_date=data_store.df['date'].max(),
                    className="mb-3"
                )
            ], width=6)
        ]),

        # Metric Selection
        dbc.Row([
            dbc.Col([
                html.Label("Select Metrics to Compare:"),
                dcc.Dropdown(
                    id='metrics-to-compare',
                    options=[
                        {'label': 'Clicks', 'value': 'clicks'},
                        {'label': 'Impressions', 'value': 'impressions'},
                        {'label': 'CTR', 'value': 'ctr'},
                        {'label': 'Position', 'value': 'position'}
                    ],
                    value=['clicks', 'impressions'],
                    multi=True,
                    className="mb-3"
                )
            ], width=12)
        ]),

        # Comparison Graphs
        html.Div(id='comparison-graphs', className="mt-4"),

        # Summary Table
        html.Div([
            html.H3("Comparison Summary", className="mt-4 mb-3"),
            html.Div(id='comparison-table')
        ])
    ])
])

@callback(
    [Output('comparison-graphs', 'children'),
     Output('comparison-table', 'children')],
    [Input('period1-date-range', 'start_date'),
     Input('period1-date-range', 'end_date'),
     Input('period2-date-range', 'start_date'),
     Input('period2-date-range', 'end_date'),
     Input('metrics-to-compare', 'value')]
)
def update_comparison(p1_start, p1_end, p2_start, p2_end, metrics):
    df = data_store.df
    
    # Filter data for both periods
    p1_mask = (df['date'] >= p1_start) & (df['date'] <= p1_end)
    p2_mask = (df['date'] >= p2_start) & (df['date'] <= p2_end)
    
    p1_data = df[p1_mask]
    p2_data = df[p2_mask]
    
    graphs = []
    summary_data = []
    
    # Create comparison graphs for each metric
    for metric in metrics:
        # Calculate daily averages for each period
        p1_avg = p1_data.groupby('type')[metric].mean().reset_index()
        p2_avg = p2_data.groupby('type')[metric].mean().reset_index()
        
        # Create comparison bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=f'Period 1 ({p1_start} to {p1_end})',
            x=p1_avg['type'],
            y=p1_avg[metric],
            marker_color=COLORS[0]
        ))
        
        fig.add_trace(go.Bar(
            name=f'Period 2 ({p2_start} to {p2_end})',
            x=p2_avg['type'],
            y=p2_avg[metric],
            marker_color=COLORS[4]
        ))
        
        fig.update_layout(
            title=f'{metric.capitalize()} Comparison by Type',
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1
        )
        
        graphs.append(dbc.Row([
            dbc.Col([
                dcc.Graph(figure=fig)
            ], width=12)
        ]))
        
        # Calculate summary statistics
        for type_name in df['type'].unique():
            p1_type_avg = p1_avg[p1_avg['type'] == type_name][metric].iloc[0]
            p2_type_avg = p2_avg[p2_avg['type'] == type_name][metric].iloc[0]
            pct_change = ((p2_type_avg - p1_type_avg) / p1_type_avg) * 100
            
            summary_data.append({
                'Type': type_name,
                'Metric': metric.capitalize(),
                'Period 1 Avg': f'{p1_type_avg:.2f}',
                'Period 2 Avg': f'{p2_type_avg:.2f}',
                'Change %': f'{pct_change:+.2f}%'
            })
    
    # Create summary table
    summary_table = dbc.Table.from_dataframe(
        pd.DataFrame(summary_data),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mt-3"
    )
    
    return graphs, summary_table