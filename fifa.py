# fifa_dashboard.py

# Deployment Link: https://your-dashboard-url.onrender.com

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pycountry

# Load cleaned dataset
df = pd.read_csv("fifa.csv")

# Strip and clean up winner/runner-up names
df["Winner"] = df["Winner"].str.strip()
df["RunnerUp"] = df["RunnerUp"].str.strip()

# --- ISO CODE MAPPING ---
# Manual mapping for tricky names or missing from pycountry
manual_codes = {
    "Germany": "DEU",
    "Czechoslovakia": "CZE",
    "Soviet Union": "RUS",
    "Yugoslavia": "SRB",
    "Netherlands": "NLD",
    "England": "GBR",
    "Brazil": "BRA",
    "Italy": "ITA",
    "Argentina": "ARG",
    "Uruguay": "URY",
    "France": "FRA",
    "Spain": "ESP"
}

# Get ISO-3 code
def get_country_code(country_name):
    name = country_name.strip()
    if name in manual_codes:
        return manual_codes[name]
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        print(f"Could not find ISO code for: {name}")
        return None

# Win counts with ISO codes
win_counts = df["Winner"].value_counts().reset_index()
win_counts.columns = ["Country", "Wins"]
win_counts["Country"] = win_counts["Country"].str.strip()
win_counts["Code"] = win_counts["Country"].apply(get_country_code)
win_counts.dropna(subset=["Code"], inplace=True)

# Debug: print table
print("Win counts with ISO-3 codes:")
print(win_counts)

# Initialize app
app = dash.Dash(__name__)
server = app.server  # For Render.com deployment

# Layout
app.layout = html.Div([
    html.H1(" FIFA World Cup Winners", style={"textAlign": "center"}),

    html.H2("Choropleth Map: Number of World Cup Wins", style={"textAlign": "center"}),
    dcc.Graph(
        id="choropleth-map",
        figure=px.choropleth(
            win_counts,
            locations="Code",
            color="Wins",
            hover_name="Country",
            color_continuous_scale="brbg",
            title="World Cup Winners by Country"
        )
    ),

    html.Label("Select a Country:"),
    dcc.Dropdown(
        id="country-dropdown",
        options=[{"label": c, "value": c} for c in sorted(df["Winner"].unique())],
        value="Brazil"
    ),
    html.Div(id="country-output", style={"marginTop": 20, "fontWeight": "bold"}),

    html.Label("Select a Year:"),
    dcc.Dropdown(
        id="year-dropdown",
        options=[{"label": y, "value": y} for y in sorted(df["Year"])],
        value=2022
    ),
    html.Div(id="year-output", style={"marginTop": 20, "fontWeight": "bold"})
])

# Callbacks
@app.callback(
    Output("country-output", "children"),
    Input("country-dropdown", "value")
)
def update_country_output(selected_country):
    wins = df[df["Winner"] == selected_country].shape[0]
    return f"{selected_country} has won the World Cup {wins} time(s)."

@app.callback(
    Output("year-output", "children"),
    Input("year-dropdown", "value")
)
def update_year_output(selected_year):
    row = df[df["Year"] == selected_year]
    if not row.empty:
        winner = row.iloc[0]["Winner"]
        runner_up = row.iloc[0]["RunnerUp"]
        return f"In {selected_year}, the winner was {winner} and the runner-up was {runner_up}."
    return "No data for that year."

# Run app
if __name__ == "__main__":
    app.run_server(debug=True)
