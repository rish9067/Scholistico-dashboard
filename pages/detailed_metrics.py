# pages/detailed_metrics.py
import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from data_store import data_store
import pandas as pd

dash.register_page(__name__, path='/detailed-metrics', name='Detailed Metrics')

def create_detailed_analysis(df):
    # Per-type metrics
    type_metrics = df.groupby('type').agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'ctr': 'mean',
        'page': 'nunique'
    }).reset_index()

    # Calculate per-page metrics
    type_metrics['clicks_per_page'] = type_metrics['clicks'] / type_metrics['page']
    type_metrics['impressions_per_page'] = type_metrics['impressions'] / type_metrics['page']
    type_metrics['ctr_per_page'] = type_metrics['ctr']

    # Time-based metrics
    time_metrics = df.groupby(['date', 'type']).agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'ctr': 'mean'
    }).reset_index()

    # Create subplots
    fig = make_subplots(
        rows=6, 
        cols=1,
        subplot_titles=(
            'Average Clicks per Page by Type', 
            'Average Impressions per Page by Type', 
            'Average CTR by Type',
            'Clicks Over Time by Type',
            'Impressions Over Time by Type',
            'CTR Over Time by Type'
        ),
        vertical_spacing=0.05
    )

    # Add traces for per-page metrics
    # 1. Clicks per page
    fig.add_trace(
        go.Bar(x=type_metrics['type'], 
               y=type_metrics['clicks_per_page'], 
               name='Clicks per Page',
               hovertemplate="Type: %{x}<br>Clicks per Page: %{y:.1f}<extra></extra>"),
        row=1, col=1
    )

    # 2. Impressions per page
    fig.add_trace(
        go.Bar(x=type_metrics['type'], 
               y=type_metrics['impressions_per_page'], 
               name='Impressions per Page',
               hovertemplate="Type: %{x}<br>Impressions per Page: %{y:.1f}<extra></extra>"),
        row=2, col=1
    )

    # 3. CTR
    fig.add_trace(
        go.Bar(x=type_metrics['type'], 
               y=type_metrics['ctr_per_page'], 
               name='CTR',
               hovertemplate="Type: %{x}<br>CTR: %{y:.2%}<extra></extra>"),
        row=3, col=1
    )

    # Add time series traces
    # 4. Clicks over time
    for type_name in df['type'].unique():
        type_data = time_metrics[time_metrics['type'] == type_name]
        fig.add_trace(
            go.Scatter(x=type_data['date'], 
                      y=type_data['clicks'],
                      name=f'{type_name} Clicks',
                      mode='lines',
                      hovertemplate="Date: %{x}<br>Clicks: %{y:.0f}<extra></extra>"),
            row=4, col=1
        )

    # 5. Impressions over time
    for type_name in df['type'].unique():
        type_data = time_metrics[time_metrics['type'] == type_name]
        fig.add_trace(
            go.Scatter(x=type_data['date'], 
                      y=type_data['impressions'],
                      name=f'{type_name} Impressions',
                      mode='lines',
                      hovertemplate="Date: %{x}<br>Impressions: %{y:.0f}<extra></extra>"),
            row=5, col=1
        )

    # 6. CTR over time
    for type_name in df['type'].unique():
        type_data = time_metrics[time_metrics['type'] == type_name]
        fig.add_trace(
            go.Scatter(x=type_data['date'], 
                      y=type_data['ctr'],
                      name=f'{type_name} CTR',
                      mode='lines',
                      hovertemplate="Date: %{x}<br>CTR: %{y:.2%}<extra></extra>"),
            row=6, col=1
        )

    # Update layout
    fig.update_layout(
        height=1800,
        title_text="Search Console Performance Metrics Analysis",
        title_x=0.5,
        plot_bgcolor='white',
        bargap=0.2,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05
        )
    )

    # Update axes labels and styling
    fig.update_yaxes(title_text="Clicks per Page", row=1, col=1, gridcolor='lightgrey')
    fig.update_yaxes(title_text="Impressions per Page", row=2, col=1, gridcolor='lightgrey')
    fig.update_yaxes(title_text="CTR", row=3, col=1, gridcolor='lightgrey')
    fig.update_yaxes(title_text="Clicks", row=4, col=1, gridcolor='lightgrey')
    fig.update_yaxes(title_text="Impressions", row=5, col=1, gridcolor='lightgrey')
    fig.update_yaxes(title_text="CTR", row=6, col=1, gridcolor='lightgrey')

    # Update x-axes
    for i in range(1, 7):
        fig.update_xaxes(gridcolor='lightgrey', row=i, col=1)

    # Add different colors for bar charts
    fig.update_traces(marker_color='rgb(158,202,225)', row=1, col=1)
    fig.update_traces(marker_color='rgb(94,158,217)', row=2, col=1)
    fig.update_traces(marker_color='rgb(32,102,148)', row=3, col=1)

    return fig, type_metrics, time_metrics

layout = html.Div([
    html.H1("Detailed Metrics Analysis", 
            className="text-center mb-4"),
    
    dbc.Container([
        # Date Range Filter
        dbc.Row([
            dbc.Col([
                html.Label("Select Date Range:"),
                dcc.DatePickerRange(
                    id='detailed-date-range',
                    min_date_allowed=data_store.df['date'].min(),
                    max_date_allowed=data_store.df['date'].max(),
                    start_date=data_store.df['date'].min(),
                    end_date=data_store.df['date'].max(),
                    className="mb-3"
                )
            ])
        ]),

        # Main Graph
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='detailed-metrics-graph')
            ])
        ]),

        # Summary Statistics
        html.H3("Summary Statistics", className="mt-4"),
        html.Div(id='summary-statistics'),

        # Export Button
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Export Analysis", 
                    id="btn-export-detailed", 
                    color="primary",
                    className="mt-3"
                ),
                dcc.Download(id="download-detailed-analysis")
            ], className="text-center")
        ])
    ])
])

@callback(
    [Output('detailed-metrics-graph', 'figure'),
     Output('summary-statistics', 'children')],
    [Input('detailed-date-range', 'start_date'),
     Input('detailed-date-range', 'end_date')]
)
def update_detailed_metrics(start_date, end_date):
    df = data_store.df
    
    # Filter data based on date range
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    filtered_df = df[mask]
    
    # Create analysis
    fig, type_metrics, time_metrics = create_detailed_analysis(filtered_df)
    
    # Create summary tables
    summary_tables = html.Div([
        html.H4("Per-Page Metrics"),
        dbc.Table.from_dataframe(
            type_metrics[['type', 'clicks_per_page', 'impressions_per_page', 'ctr_per_page', 'page']].round(2),
            striped=True,
            bordered=True,
            hover=True
        ),
        
        html.H4("Time-based Metrics", className="mt-4"),
        dbc.Table.from_dataframe(
            time_metrics.groupby('type').agg({
                'clicks': ['mean', 'min', 'max'],
                'impressions': ['mean', 'min', 'max'],
                'ctr': ['mean', 'min', 'max']
            }).round(2).reset_index(),
            striped=True,
            bordered=True,
            hover=True
        )
    ])
    
    return fig, summary_tables

@callback(
    Output("download-detailed-analysis", "data"),
    Input("btn-export-detailed", "n_clicks"),
    prevent_initial_call=True
)
def export_detailed_analysis(n_clicks):
    if n_clicks:
        # Create PDF report (you'll need to implement this)
        return dcc.send_data_frame(
            data_store.df.to_excel,
            "detailed_analysis.xlsx",
            sheet_name="Analysis"
        )