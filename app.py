# app.py
import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from data_store import data_store

# Load data
data_store.load_data('final_plotly_data.csv')  # Replace with your data file path

# Initialize the app
app = Dash(__name__, 
          use_pages=True, 
          external_stylesheets=[dbc.themes.FLATLY])

# Create navbar
# app.py (update navbar section)
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Overview", href="/")),
        dbc.NavItem(dbc.NavLink("Detailed Metrics", href="/detailed-metrics")), 
        dbc.NavItem(dbc.NavLink("Time Analysis", href="/time-analysis")),
        dbc.NavItem(dbc.NavLink("Comparison", href="/comparison"))
    ],
    brand="Search Console Analytics",
    brand_href="/",
    color="primary",
    dark=True,
)

# Define app layout
app.layout = html.Div([
    navbar,
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)