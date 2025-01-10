# pages/time_analysis.py
import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from data_processor import get_time_series_data, COLORS

from data_store import data_store



dash.register_page(__name__, path='/time-analysis', name='Time Analysis')

layout = html.Div([
    html.H1("Time-based Analysis", 
            className="text-center mb-4"),
    
    dbc.Container([
        # Controls
        dbc.Row([
            dbc.Col([
                html.Label("Select Metric:"),
                dcc.Dropdown(
                    id='metric-selector',
                    options=[
                        {'label': 'Clicks', 'value': 'clicks'},
                        {'label': 'Impressions', 'value': 'impressions'},
                        {'label': 'CTR', 'value': 'ctr'}
                    ],
                    value='clicks',
                    className="mb-3"
                )
            ], width=4),
            
            dbc.Col([
                html.Label("Time Aggregation:"),
                dcc.Dropdown(
                    id='time-aggregation',
                    options=[
                        {'label': 'Daily', 'value': 'D'},
                        {'label': 'Weekly', 'value': 'W'},
                        {'label': 'Monthly', 'value': 'M'}
                    ],
                    value='D',
                    className="mb-3"
                )
            ], width=4),
            
            dbc.Col([
                html.Label("Show Moving Average:"),
                dcc.Checklist(
                    id='show-ma',
                    options=[{'label': ' 7-day Moving Average', 'value': 'yes'}],
                    value=[],
                    className="mb-3"
                )
            ], width=4)
        ]),

        # Time Series Graph
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(id='time-series-plot')
                ], className="graph-container")
            ], width=12)
        ]),

        # Additional Analysis
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H3("Day of Week Analysis"),
                    dcc.Graph(id='weekday-analysis')
                ], className="graph-container")
            ], width=6),
            
            dbc.Col([
                html.Div([
                    html.H3("Monthly Trends"),
                    dcc.Graph(id='monthly-trends')
                ], className="graph-container")
            ], width=6)
        ])
    ])
])

@callback(
    [Output('time-series-plot', 'figure'),
     Output('weekday-analysis', 'figure'),
     Output('monthly-trends', 'figure')],
    [Input('metric-selector', 'value'),
     Input('time-aggregation', 'value'),
     Input('show-ma', 'value')]
)
def update_time_analysis(metric, aggregation, show_ma):
    df = data_store.df
    
    # Time series plot
    time_data = get_time_series_data(df, metric, aggregation)
    
    fig_time = px.line(
        time_data,
        x='date',
        y=metric,
        color='type',
        title=f'{metric.capitalize()} Over Time',
        color_discrete_sequence=COLORS
    )
    
    if show_ma and 'yes' in show_ma:
        # Add moving average
        for type_name in df['type'].unique():
            type_data = time_data[time_data['type'] == type_name]
            ma = type_data[metric].rolling(window=7).mean()
            fig_time.add_scatter(
                x=type_data['date'],
                y=ma,
                name=f'{type_name} (7-day MA)',
                line=dict(dash='dash'),
                showlegend=True
            )
    
    # Weekday analysis
    df['weekday'] = df['date'].dt.day_name()
    weekday_data = df.groupby('weekday')[metric].mean().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    
    fig_weekday = px.bar(
        weekday_data,
        title=f'Average {metric.capitalize()} by Day of Week',
        color_discrete_sequence=[COLORS[0]]
    )
    
    # Monthly trends
    df['month'] = df['date'].dt.strftime('%Y-%m')
    monthly_data = df.groupby(['month', 'type'])[metric].mean().reset_index()
    
    fig_monthly = px.line(
        monthly_data,
        x='month',
        y=metric,
        color='type',
        title=f'Monthly {metric.capitalize()} Trends',
        color_discrete_sequence=COLORS
    )
    
    return fig_time, fig_weekday, fig_monthly