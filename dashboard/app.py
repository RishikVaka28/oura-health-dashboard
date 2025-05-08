import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import psycopg2
import subprocess

external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bootswatch@5.2.3/dist/lux/bootstrap.min.css",
    "https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap"
]

# Run Oura import script on startup
subprocess.run(["python", "../backend/oura_import.py"])

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="fitness_coach",
    user="fitness_user",
    password="fitness_user",
    host="localhost",
    port="5432"
)
query = "SELECT * FROM TrainingData"
df = pd.read_sql_query(query, conn)
conn.close()

# Calculate summary stats
avg_steps = int(df['steps'].mean())
avg_sleep = round(df['sleep_hours'].mean(), 1)
avg_hr = int(df['heart_rate'].mean())
avg_calories = int(df['calories'].mean()) if 'calories' in df.columns else 0
avg_sleep = round(df['sleep_hours'].mean(), 1)
avg_hr = int(df['heart_rate'].mean())

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Fitness Coach Dashboard"

# Layout
app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="🏋️‍♂️ Fitness Coach Dashboard",
        color="primary",
        dark=True,
        className="mb-4",
    ),

    dbc.Row([
        dbc.Col(
            dbc.Button("🔄 Refresh Oura Data", id="refresh-button", color="info", className="mb-3 w-100"),
            width=4
        )
    ], justify="center"),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Average Steps", className="text-muted"),
                html.H3(f"{avg_steps:,}", className="text-primary")
            ])
        ], className="shadow-lg rounded text-center"), md=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Average Sleep (hrs)", className="text-muted"),
                html.H3(f"{avg_sleep}", className="text-success")
            ])
        ], className="shadow-lg rounded text-center"), md=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Average Heart Rate", className="text-muted"),
                html.H3(f"{avg_hr} bpm", className="text-danger")
            ])
        ], className="shadow-lg rounded text-center"), md=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Average Calories", className="text-muted"),
                html.H3(f"{avg_calories} kcal", className="text-warning")
            ])
        ], className="shadow-lg rounded text-center"), md=3),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Blockquote([
                        html.P("Your body can stand almost anything. It’s your mind you have to convince."),
                        html.Footer("💡 Stay consistent and trust the process", className="blockquote-footer")
                    ], className="mb-0")
                ])
            ),
            className="shadow-sm p-3 rounded bg-light"
        )
    ], className="mb-4"),

    dbc.Tabs([
        dbc.Tab(label="📈 Steps Over Time", children=[
            dcc.Graph(
                figure=px.line(df, y='steps', title='Steps Trend Over Records', markers=True)
            )
        ]),
        dbc.Tab(label="💤 Sleep vs Heart Rate", children=[
            dcc.Graph(
                figure=px.scatter(df, x='sleep_hours', y='heart_rate', color='stress_level',
                                  title='Sleep vs Heart Rate (Colored by Stress Level)',
                                  labels={'sleep_hours': 'Sleep (hrs)', 'heart_rate': 'Heart Rate'})
            )
        ]),
        dbc.Tab(label="🧠 Workout Recommendations", children=[
            dcc.Graph(
                figure=px.pie(df, names='recommended_workout', title='Workout Recommendation Distribution')
            )
        ])
    ])
], fluid=True)

# Callback for Refresh Button
@app.callback(
    Output("refresh-button", "children"),
    Input("refresh-button", "n_clicks"),
    prevent_initial_call=True
)
def refresh_oura_data(n_clicks):
    subprocess.run(["python", "../backend/oura_import.py"])
    return "✅ Refreshed!"

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)
