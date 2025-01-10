# pages/overview.py
import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from data_processor import calculate_metrics, COLORS
from data_store import data_store


dash.register_page(__name__, path='/', name='Overview')

def create_metric_card(title, value, color):
    return dbc.Card(
        dbc.CardBody([
            html.H4(title, className="metric-label"),
            html.P(value, className="metric-value", style={'color': color})
        ]),
        className="metric-card"
    )

layout = html.Div([
    html.H1("Search Console Analytics Overview", 
            className="text-center mb-4"),
    
    dbc.Container([
        # Date Range Selector
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label("Select Date Range:"),
                    dcc.DatePickerRange(
                        id='overview-date-range',
                        min_date_allowed=data_store.df['date'].min(),
                        max_date_allowed=data_store.df['date'].max(),
                        start_date=data_store.df['date'].min(),
                        end_date=data_store.df['date'].max(),
                        className="mb-3"
                    )
                ], className="date-picker-container")
            ])
        ]),

        # Metric Cards
        html.Div(id='metric-cards', className="mb-4"),

        # Graphs
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H3("Performance by Content Type"),
                    dcc.Graph(id='type-performance')
                ], className="graph-container")
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H3("CTR Distribution"),
                    dcc.Graph(id='ctr-distribution')
                ], className="graph-container")
            ], width=6)
        ]),

        # Export Button
        dbc.Row([
            dbc.Col([
                dbc.Button("Export as PDF", id="btn-export-pdf", 
                          color="primary", className="mt-3"),
                dcc.Download(id="download-pdf")
            ], width=12, className="text-center")
        ])
    ])
])

@callback(
    [Output('metric-cards', 'children'),
     Output('type-performance', 'figure'),
     Output('ctr-distribution', 'figure')],
    [Input('overview-date-range', 'start_date'),
     Input('overview-date-range', 'end_date')]
)
def update_overview(start_date, end_date):
    df = data_store.df
    
    # Filter data based on date range
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    filtered_df = df[mask]
    
    # Calculate metrics
    metrics = calculate_metrics(filtered_df)
    
    # Create metric cards
    cards = dbc.Row([
        dbc.Col(create_metric_card("Total Clicks", f"{metrics['total_clicks']:,}", COLORS[0]), width=3),
        dbc.Col(create_metric_card("Total Impressions", f"{metrics['total_impressions']:,}", COLORS[2]), width=3),
        dbc.Col(create_metric_card("Average CTR", f"{metrics['avg_ctr']:.2f}%", COLORS[4]), width=3),
        dbc.Col(create_metric_card("Average Position", f"{metrics['avg_position']:.2f}", COLORS[6]), width=3),
    ])
    
    # Create performance by type figure
    type_perf = px.bar(
        filtered_df.groupby('type').agg({
            'clicks': 'sum',
            'impressions': 'sum'
        }).reset_index(),
        x='type',
        y=['clicks', 'impressions'],
        barmode='group',
        title='Performance by Content Type',
        color_discrete_sequence=[COLORS[0], COLORS[4]]
    )
    
    # Create CTR distribution figure
    ctr_dist = px.box(
        filtered_df,
        x='type',
        y='ctr',
        color='type',
        title='CTR Distribution by Content Type',
        color_discrete_sequence=COLORS
    )
    
    return cards, type_perf, ctr_dist

@callback(
    Output("download-pdf", "data"),
    Input("btn-export-pdf", "n_clicks"),
    prevent_initial_call=True
)
def export_pdf(n_clicks):
    # Add PDF export functionality here
    # You'll need to implement this based on your specific needs
    pass