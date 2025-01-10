# components/graphs.py
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import COLORS

def create_multi_metric_chart(df, metrics, title="Multi-Metric Analysis"):
    """Create a chart with multiple metrics using secondary axis"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    for i, metric in enumerate(metrics):
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df[metric],
                name=metric.capitalize(),
                line=dict(color=COLORS[i])
            ),
            secondary_y=(i == 1)  # Second metric on secondary y-axis
        )
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        hovermode="x unified"
    )
    
    return fig

def create_heatmap(df, x_col, y_col, value_col, title="Heatmap Analysis"):
    """Create a heatmap visualization"""
    pivot_data = df.pivot_table(
        values=value_col,
        index=y_col,
        columns=x_col,
        aggfunc='mean'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale=COLORS,
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col.capitalize(),
        yaxis_title=y_col.capitalize()
    )
    
    return fig

def create_sunburst(df, path, values, title="Hierarchical View"):
    """Create a sunburst chart for hierarchical data"""
    fig = px.sunburst(
        df,
        path=path,
        values=values,
        color_discrete_sequence=COLORS,
        title=title
    )
    
    return fig

def create_scatter_matrix(df, dimensions, title="Scatter Matrix"):
    """Create a scatter matrix for multiple dimensions"""
    fig = px.scatter_matrix(
        df,
        dimensions=dimensions,
        color='type',
        color_discrete_sequence=COLORS,
        title=title
    )
    
    fig.update_layout(
        dragmode='select',
        hovermode='closest'
    )
    
    return fig

def create_funnel_chart(df, steps, values, title="Funnel Analysis"):
    """Create a funnel chart"""
    fig = go.Figure()
    
    for i, (step, value) in enumerate(zip(steps, values)):
        fig.add_trace(go.Funnel(
            name=step,
            y=[step],
            x=[value],
            textposition="inside",
            textinfo="value+percent initial",
            marker={"color": COLORS[i]}
        ))
    
    fig.update_layout(
        title=title,
        showlegend=False
    )
    
    return fig

def create_radar_chart(df, categories, values, title="Radar Analysis"):
    """Create a radar chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker_color=COLORS[0]
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values)]
            )
        ),
        showlegend=False,
        title=title
    )
    
    return fig