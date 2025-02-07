import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import requests
import pandas as pd

# Inicializar la app de Dash
app = dash.Dash(__name__)
server = app.server  # 🔹 Render necesita esta línea

# Obtener datos desde Open-Meteo
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": -34.61,
    "longitude": -58.38,
    "hourly": "temperature_2m,relative_humidity_2m",
    "timezone": "America/Argentina/Buenos_Aires",
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(
        {
            "Fecha": pd.to_datetime(data["hourly"]["time"]),
            "Temperatura (°C)": data["hourly"]["temperature_2m"],
            "Humedad (%)": data["hourly"]["relative_humidity_2m"],
        }
    )
except requests.exceptions.RequestException as e:
    print(f"⚠️ Error al obtener datos: {e}")
    df = pd.DataFrame(columns=["Fecha", "Temperatura (°C)", "Humedad (%)"])

# Diseño del Dashboard
app.layout = html.Div(
    style={"backgroundColor": "#1E1E1E", "color": "white", "padding": "20px"},
    children=[
        html.H1("Dashboard Meteorológico", style={"textAlign": "center"}),
        dcc.DatePickerRange(
            id="date-picker",
            start_date=df["Fecha"].min() if not df.empty else None,
            end_date=df["Fecha"].max() if not df.empty else None,
            display_format="YYYY-MM-DD",
            style={"backgroundColor": "#333", "color": "white", "padding": "10px"},
        ),
        dcc.Graph(id="clima-graph"),
        dcc.Graph(id="scatter-graph"),
    ],
)


# Callback para actualizar gráficos
@app.callback(
    [
        Output("clima-graph", "figure"),
        Output("scatter-graph", "figure"),
    ],
    [Input("date-picker", "start_date"), Input("date-picker", "end_date")],
)
def update_graphs(start_date, end_date):
    if df.empty or start_date is None or end_date is None:
        empty_fig = px.scatter(title="No hay datos disponibles", template="plotly_dark")
        return empty_fig, empty_fig

    df_filtered = df[(df["Fecha"] >= start_date) & (df["Fecha"] <= end_date)]
    if df_filtered.empty:
        empty_fig = px.scatter(
            title="No hay datos en este rango", template="plotly_dark"
        )
        return empty_fig, empty_fig

    fig1 = px.line(
        df_filtered,
        x="Fecha",
        y="Temperatura (°C)",
        title="Evolución del Clima",
        template="plotly_dark",
    )
    fig2 = px.scatter(
        df_filtered,
        x="Temperatura (°C)",
        y="Humedad (%)",
        title="Relación entre Temperatura y Humedad",
        template="plotly_dark",
    )

    return fig1, fig2


# Ejecutar localmente
if __name__ == "__main__":
    app.run_server()
