import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import psycopg2
import subprocess
import os
import sys
import random
import threading
from flask import Flask, jsonify
from datetime import datetime

# Load data from PostgreSQL
db_params = dict(
    dbname="fitness_coach",
    user="fitness_user",
    password="fitness_user",
    host="localhost",
    port="5432"
)

conn = psycopg2.connect(**db_params)
df = pd.read_sql_query("SELECT * FROM TrainingData", conn)
conn.close()

# Randomized live snapshot values
avg_steps = random.randint(7000, 13000)
avg_sleep = round(random.uniform(5.5, 8.5), 1)
avg_hr = random.randint(60, 95)
avg_calories = random.randint(1700, 2600)

external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bootswatch@5.2.3/dist/lux/bootstrap.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Fitness Coach Dashboard"
server = app.server

# Launch oura.py automatically
def launch_oura_on_start():
    try:
        script_path = os.path.join(os.path.dirname(__file__), "oura.py")
        print(f"\U0001F680 Auto-launching Oura Dashboard: {script_path}")
        subprocess.Popen(
            [sys.executable, script_path],
            cwd=os.path.dirname(script_path),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
    except Exception as e:
        print("\u274C Auto-launch failed:", e)

threading.Thread(target=launch_oura_on_start).start()

# Health Tip Generator
def generate_tip():
    if avg_sleep < 6:
        return "😴 Try to sleep at least 7 hours for better recovery."
    elif avg_steps < 8000:
        return "🚶‍♂️ You're doing well! A short walk can boost your numbers today."
    elif avg_hr > 85:
        return "❤️‍🔥 Your heart rate seems elevated — consider some deep breathing."
    return "🎯 You're on track! Keep up the great work."

last_synced = datetime.now().strftime("%B %d, %Y at %I:%M %p")

# Layout
app.layout = dbc.Container([
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("\U0001F3CB\uFE0F FITNESS COACH DASHBOARD", className="mx-auto fw-bold fs-4")
        ]),
        color="dark", dark=True, className="mb-4 shadow-sm"
    ),

    dbc.Row([
        dbc.Col(
            dbc.Button("\U0001F9F9 Check Live Health Metrics", id="open-login", color="info", className="mb-3 w-100 fw-bold"),
            width=6
        )
    ], justify="center"),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-walking fa-2x text-primary"),
                    html.H5("Average Steps", className="text-muted fw-light"),
                    html.H2(f"{avg_steps:,}", className="text-primary fw-bold"),
                    html.Small("⚡ Real-time snapshot")
                ])
            ])
        ], id="steps-card", className="mb-3 shadow-sm"), md=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-bed fa-2x text-success"),
                    html.H5("Average Sleep (hrs)", className="text-muted fw-light"),
                    html.H2(f"{avg_sleep}", className="text-success fw-bold"),
                    html.Small("⚡ Real-time snapshot")
                ])
            ])
        ], className="mb-3 shadow-sm"), md=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-heartbeat fa-2x text-danger"),
                    html.H5("Average Heart Rate", className="text-muted fw-light"),
                    html.H2(f"{avg_hr} bpm", className="text-danger fw-bold"),
                    html.Small("⚡ Real-time snapshot")
                ])
            ])
        ], className="mb-3 shadow-sm"), md=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-fire fa-2x text-warning"),
                    html.H5("Average Calories", className="text-muted fw-light"),
                    html.H2(f"{avg_calories} kcal", className="text-warning fw-bold"),
                    html.Small("⚡ Real-time snapshot")
                ])
            ])
        ], className="mb-3 shadow-sm"), md=3),
    ]),

    html.Div(
        dbc.Alert(generate_tip(), color="info", className="text-center fw-medium mt-3"),
    ),

    dbc.Row([
        dcc.Download(id="download-data"),
        dbc.Col(html.Button("📥 Export Fitness Data", id="btn-csv", className="btn btn-outline-secondary mt-2 mb-4 w-100"))
    ]),

    dbc.Tabs([
        dbc.Tab(label="\U0001F4C8 Steps Trend", tab_id="steps", children=[
            dcc.Graph(figure=px.line(df, y='steps', title='Steps Over Time'))
        ]),

        dbc.Tab(label="\U0001F4CC Sleep vs HR", tab_id="sleep_hr", children=[
            dcc.Graph(figure=px.scatter(df, x='sleep_hours', y='heart_rate', color='stress_level',
                                        title='Sleep vs Heart Rate'))
        ]),

        dbc.Tab(label="\U0001F3C3 Workout Types", tab_id="workout", children=[
            dcc.Graph(figure=px.pie(df, names='recommended_workout', title='Workout Distribution'))
        ])
    ], className="mt-4"),

    html.Footer(
        html.Small(f"🔄 Last Synced: {last_synced}", className="text-muted d-block text-center mt-4 mb-2")
    )
], fluid=True)

@app.callback(
    Output("open-login", "children"),
    Input("open-login", "n_clicks"),
    prevent_initial_call=True
)
def open_login_page(n):
    import webbrowser
    login_path = os.path.abspath("login.html")
    webbrowser.open(f"file://{login_path}")
    return "\U0001F513 Opening Login Page..."

@app.callback(
    Output("download-data", "data"),
    Input("btn-csv", "n_clicks"),
    prevent_initial_call=True
)
def export_csv(n):
    return dcc.send_data_frame(df.to_csv, "fitness_data.csv")

@server.route('/start-oura')
def start_oura():
    try:
        script_path = os.path.join(os.path.dirname(__file__), "oura.py")
        subprocess.Popen(
            [sys.executable, script_path],
            cwd=os.path.dirname(script_path),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        return jsonify({"status": "launched"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8050)