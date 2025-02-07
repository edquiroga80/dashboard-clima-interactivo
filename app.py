import dash
from dash import dcc, html  # Se actualizó importación (Dash >=2.0)
from dash.dependencies import Input, Output
import plotly.express as px
import requests
import pandas as pd

# 🔹 Obtener datos de Open-Meteo con manejo de errores
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": -34.61,  # Buenos Aires
    "longitude": -58.38,
    "hourly": "temperature_2m,relative_humidity_2m",
    "timezone": "America/Argentina/Buenos_Aires",
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()  # ⚠️ Manejo de errores HTTP
    data = response.json()

    # Convertir los datos en un DataFrame
    df = pd.DataFrame(
        {
            "Fecha": pd.to_datetime(data["hourly"]["time"]),
            "Temperatura (°C)": data["hourly"]["temperature_2m"],
            "Humedad (%)": data["hourly"]["relative_humidity_2m"],
        }
    )
except requests.exceptions.RequestException as e:
    print(f"⚠️ Error al obtener datos de Open-Meteo: {e}")
    df = pd.DataFrame(columns=["Fecha", "Temperatura (°C)", "Humedad (%)"])

# 🔹 Inicializar la aplicación Dash
app = dash.Dash(__name__)
server = app.server  # ⚠️ Render necesita esto para ejecutarlo con Gunicorn

app.layout = html.Div(
    style={"backgroundColor": "#1E1E1E", "color": "white", "padding": "20px"},
    children=[
        html.H1("Dashboard Meteorológico", style={"textAlign": "center"}),
        # Selector de fechas
        dcc.DatePickerRange(
            id="date-picker",
            start_date=df["Fecha"].min() if not df.empty else None,
            end_date=df["Fecha"].max() if not df.empty else None,
            display_format="YYYY-MM-DD",
            style={"backgroundColor": "#333", "color": "white", "padding": "10px"},
        ),
        # Indicadores de temperatura
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Temp. Máxima", style={"textAlign": "center"}),
                        html.P(
                            id="temp-max",
                            style={"fontSize": "24px", "textAlign": "center"},
                        ),
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        html.H3("Temp. Mínima", style={"textAlign": "center"}),
                        html.P(
                            id="temp-min",
                            style={"fontSize": "24px", "textAlign": "center"},
                        ),
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
            ],
            style={"display": "flex", "justify-content": "center", "padding": "20px"},
        ),
        # Gráficos interactivos
        dcc.Graph(id="clima-graph"),
        dcc.Graph(id="scatter-graph"),
    ],
)


# 🔹 Callback para actualizar los gráficos según la fecha seleccionada
@app.callback(
    [
        Output("clima-graph", "figure"),
        Output("scatter-graph", "figure"),
        Output("temp-max", "children"),
        Output("temp-min", "children"),
    ],
    [Input("date-picker", "start_date"), Input("date-picker", "end_date")],
)
def update_graphs(start_date, end_date):
    if df.empty or start_date is None or end_date is None:
        empty_fig = px.scatter(title="No hay datos disponibles", template="plotly_dark")
        return empty_fig, empty_fig, "N/A", "N/A"

    # Filtrar datos por rango de fechas
    df_filtered = df[(df["Fecha"] >= start_date) & (df["Fecha"] <= end_date)]

    # Si no hay datos en el rango, devolver gráficos vacíos
    if df_filtered.empty:
        empty_fig = px.scatter(
            title="No hay datos en este rango", template="plotly_dark"
        )
        return empty_fig, empty_fig, "N/A", "N/A"

    # Gráfico de líneas de temperatura y humedad
    fig1 = px.line(
        df_filtered,
        x="Fecha",
        y=["Temperatura (°C)", "Humedad (%)"],
        title="Evolución del Clima",
        template="plotly_dark",
    )

    # Gráfico de dispersión temperatura vs humedad
    fig2 = px.scatter(
        df_filtered,
        x="Temperatura (°C)",
        y="Humedad (%)",
        title="Relación entre Temperatura y Humedad",
        template="plotly_dark",
    )

    # Calcular temperatura máxima y mínima
    temp_max = f"{df_filtered['Temperatura (°C)'].max():.1f} °C"
    temp_min = f"{df_filtered['Temperatura (°C)'].min():.1f} °C"

    return fig1, fig2, temp_max, temp_min


# 🔹 Ejecutar la aplicación localmente
if __name__ == "__main__":
    app.run_server(debug=True)
