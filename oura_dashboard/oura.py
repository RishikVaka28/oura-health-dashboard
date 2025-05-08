import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go
import psycopg2
from datetime import date, datetime, timedelta
import subprocess
import threading
import webbrowser
import random
import os
import sys

# Step 1: Initial data sync from Oura API to PostgreSQL
subprocess.run(["python", "../scripts/sync_oura_api_to_postgres.py"])
last_synced_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Step 2: Load data from PostgreSQL using psycopg2
conn = psycopg2.connect(
    dbname="oura_data",
    user="postgres",
    password="password",
    host="localhost",
    port=5432
)
df = pd.read_sql_query("SELECT * FROM oura_trends ORDER BY date", conn)
conn.close()

# Handle NaNs in critical fields
if 'activity_score' in df.columns:
    df['activity_score'] = df['activity_score'].apply(lambda x: random.randint(5, 10) if pd.isna(x) else x)

if 'steps' in df.columns:
    df['steps'] = df['steps'].apply(lambda x: random.randint(500, 1000) if pd.isna(x) else x)

# Step 3: Handle NaNs in critical fields
if 'activity_score' in df.columns:
    df['activity_score'] = df['activity_score'].apply(lambda x: random.randint(5, 10) if pd.isna(x) else x)

if 'steps' in df.columns:
    df['steps'] = df['steps'].apply(lambda x: random.randint(500, 1000) if pd.isna(x) else x)
    
# Step 3: Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])
DEFAULT_DATE = df['date'].max().date() if 'date' in df.columns else date.today()

# Step 4: Initialize Dash app
external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bootswatch@5.2.3/dist/flatly/bootstrap.min.css",
    "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server
app.title = "Oura Wellness Dashboard"

# Step 5: Layout with sidebar and content
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Div([
            html.H3("🌙 Oura Dashboard", className="text-white mb-4 text-center"),
            html.Hr(),
            html.Nav([
                html.Ul([
                    html.Li(html.A("Dashboard", href="/", className="nav-link text-white fw-bold"), className="nav-item"),
                    html.Li(html.A("Trends", href="/trends", className="nav-link text-white fw-bold"), className="nav-item")
                ], className="nav flex-column")
            ])
        ], className="bg-primary p-4 vh-100 text-white col-md-2"),
        html.Div(id='page-content', className="col-md-10 p-4 bg-white")
    ], className="row no-gutters")
])

# Dashboard Layout
def get_dashboard_layout():
    return html.Div([
        html.H2("Today's Wellness Snapshot", className="text-center text-primary mb-4"),
        dcc.DatePickerSingle(
            id='date-picker',
            min_date_allowed=df['date'].min().date(),
            max_date_allowed=df['date'].max().date(),
            initial_visible_month=DEFAULT_DATE,
            date=DEFAULT_DATE,
            display_format='YYYY-MM-DD',
            style={"margin": "auto", "display": "block"}
        ),
        dcc.Loading([
            html.Button("🔁 Sync", id="sync-button", className="btn btn-warning mt-3 mb-2 d-block mx-auto"),
            html.Div(id="sync-status", className="text-center text-muted mb-4", children=f"Last synced at: {last_synced_time}")
        ]),
        html.Div(id='oura-output', className="mt-5")
    ])

# Trends Layout
def get_trends_layout():
    return html.Div([
        html.H2("📊 Health Metrics Trends", className="text-center text-info mb-4"),
        html.Div([
            html.Label("Select Time Range:", className="me-2 fw-bold"),
            dcc.Dropdown(
                id='time-range',
                options=[
                    {"label": "Today", "value": "1d"},
                    {"label": "Last 7 Days", "value": "7d"},
                    {"label": "Last 30 Days", "value": "30d"},
                    {"label": "All Time", "value": "all"},
                ],
                value="30d",
                clearable=False,
                style={"width": "200px"}
            )
        ], className="d-flex justify-content-end mb-3"),
        dcc.Tabs(id="trends-tabs", value='sleep', children=[
            dcc.Tab(label='Sleep', value='sleep'),
            dcc.Tab(label='Activity', value='activity'),
            dcc.Tab(label='Readiness', value='readiness'),
            dcc.Tab(label='HRV', value='hrv'),
            dcc.Tab(label='Temperature', value='temp'),
            dcc.Tab(label='Calories Burned', value='calories'),
            dcc.Tab(label='Heart Rate', value='heart_rate'),
            dcc.Tab(label='Sleep Efficiency', value='sleep_efficiency_bar')
        ]),
        html.Div(id='trends-tab-content', className="mt-4")
    ])

# Page Router
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    return get_trends_layout() if pathname == '/trends' else get_dashboard_layout()

# Trends Chart Rendering
@app.callback(Output('trends-tab-content', 'children'), Input('trends-tabs', 'value'), Input('time-range', 'value'))
def render_trends_tab(tab, time_range):
    end_date = df['date'].max()
    start_date = df['date'].min() if time_range == 'all' else end_date - timedelta(days=int(time_range.replace("d", "")))
    dff = df[df['date'].between(start_date, end_date)]

    if tab == 'sleep_efficiency_bar':
        return dcc.Graph(
            figure=go.Figure([
                go.Bar(x=dff['date'], y=dff['sleep_efficiency'], marker_color="#00c0ef")
            ]).update_layout(title="Sleep Efficiency (%)", xaxis_title="Date", yaxis_title="Efficiency")
        )

    metric_map = {
        'sleep': ('total_sleep_duration', 'Sleep Duration (hrs)', '#1f77b4'),
        'activity': ('activity_score', 'Activity Score', '#2ca02c'),
        'readiness': ('readiness_score', 'Readiness Score', '#ff7f0e'),
        'hrv': ('average_hrv', 'HRV (ms)', '#9467bd'),
        'temp': ('temperature_deviation', 'Temp Deviation (°C)', '#e377c2'),
        'calories': ('activity_burn', 'Calories Burned', '#d62728'),
        'heart_rate': ('lowest_resting_heart_rate', 'Heart Rate (bpm)', '#17becf')
    }
    metric, label, color = metric_map[tab]
    y_data = dff[metric] / 60 if tab == 'sleep' else dff[metric]

    return dcc.Graph(
        figure=go.Figure([
            go.Scatter(x=dff['date'], y=y_data, mode='lines+markers', name=label, line=dict(color=color))
        ]).update_layout(title=label + " Over Time", xaxis_title="Date", yaxis_title=label)
    )

# Dashboard Metrics Output
@app.callback(Output("oura-output", "children"), Input("date-picker", "date"))
def display_oura_data(selected_date):
    df_day = df[df['date'] == pd.to_datetime(selected_date)]
    if df_day.empty:
        return html.P(f"No data for {selected_date}", className="text-center text-danger")

    row = df_day.iloc[0]
    return html.Div([
        html.Div([
            html.Div([
                html.H5("Readiness", className="text-muted"),
                html.H3(f"{row['readiness_score']}", className="text-primary")
            ], className="col-md-2 text-center"),
            html.Div([
                html.H5("Sleep Score", className="text-muted"),
                html.H3(f"{row['sleep_score']}", className="text-success")
            ], className="col-md-2 text-center"),
            html.Div([
                html.H5("Activity Score", className="text-muted"),
                html.H3(f"{row['activity_score']}", className="text-warning")
            ], className="col-md-2 text-center"),
            html.Div([
                html.H5("Steps", className="text-muted"),
                html.H3(f"{row['steps']:,}", className="text-info")
            ], className="col-md-2 text-center"),
            html.Div([
                html.H5("Heart Rate", className="text-muted"),
                html.H3(f"{row['lowest_resting_heart_rate']} bpm", className="text-danger")
            ], className="col-md-2 text-center")
        ], className="row mb-4 justify-content-around"),

        html.Div([
            html.Div([
                dcc.Graph(
                    figure=go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=row['sleep_efficiency'],
                        title={'text': "Sleep Efficiency (%)"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#00c0ef"},
                            'steps': [
                                {'range': [0, 60], 'color': "#f8d7da"},
                                {'range': [60, 85], 'color': "#fcefc7"},
                                {'range': [85, 100], 'color': "#d4f4dd"}
                            ]
                        }
                    ))
                )
            ], className="col-md-6"),
            html.Div([
                dcc.Graph(
                    figure=go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=row['average_hrv'],
                        title={'text': "HRV (ms)"},
                        gauge={
                            'axis': {'range': [0, 200]},
                            'bar': {'color': "#9467bd"},
                            'steps': [
                                {'range': [0, 50], 'color': "#f8d7da"},
                                {'range': [50, 100], 'color': "#fcefc7"},
                                {'range': [100, 200], 'color': "#d4f4dd"}
                            ]
                        }
                    ))
                )
            ], className="col-md-6")
        ], className="row")
    ])

# Sync Button Callback
@app.callback(Output("sync-status", "children"), Input("sync-button", "n_clicks"), prevent_initial_call=True)
def manual_sync(n):
    subprocess.run(["python", "../scripts/sync_oura_api_to_postgres.py"])
    return f"✅ Last synced at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Run App
if __name__ == '__main__':
    app.run(debug=True, port=8051)