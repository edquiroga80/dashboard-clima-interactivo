import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import requests
import pandas as pd

# Obtener datos de la API de Open-Meteo
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": -34.61,  # Buenos Aires
    "longitude": -58.38,
    "hourly": "temperature_2m,relative_humidity_2m",
    "timezone": "America/Argentina/Buenos_Aires",
}

response = requests.get(url, params=params)
data = response.json()

# Convertir los datos en un DataFrame
df = pd.DataFrame(
    {
        "Fecha": pd.to_datetime(data["hourly"]["time"]),
        "Temperatura (°C)": data["hourly"]["temperature_2m"],
        "Humedad (%)": data["hourly"]["relative_humidity_2m"],
    }
)

# Inicializar la aplicación Dash con estilo moderno
app = dash.Dash(__name__)

app.layout = html.Div(
    style={"backgroundColor": "#1E1E1E", "color": "white", "padding": "20px"},
    children=[
        html.H1("Dashboard Meteorológico", style={"textAlign": "center"}),
        # Selector de fechas
        dcc.DatePickerRange(
            id="date-picker",
            start_date=df["Fecha"].min(),
            end_date=df["Fecha"].max(),
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
        # Gráfico de líneas para temperatura y humedad
        dcc.Graph(id="clima-graph"),
        # Gráfico de dispersión temperatura vs humedad
        dcc.Graph(id="scatter-graph"),
    ],
)


# Callback para actualizar los gráficos según la fecha seleccionada
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
    # Filtrar datos por rango de fechas
    df_filtered = df[(df["Fecha"] >= start_date) & (df["Fecha"] <= end_date)]

    # Verificar si hay datos filtrados
    if df_filtered.empty:
        # Gráfico vacío en caso de no haber datos
        empty_fig = px.scatter(
            title="No hay datos disponibles en este rango de fechas",
            template="plotly_dark",
        )

        return empty_fig, empty_fig, "N/A", "N/A"

    # Gráfico de líneas
    fig1 = px.line(
        df_filtered,
        x="Fecha",
        y=["Temperatura (°C)", "Humedad (%)"],
        title="Evolución del Clima",
        template="plotly_dark",
    )

    # Gráfico de dispersión temperatura vs humedad sin trendline
    fig2 = px.scatter(
        df_filtered,
        x="Temperatura (°C)",
        y="Humedad (%)",
        title="Relación entre Temperatura y Humedad",
        template="plotly_dark",
    )

    # Cálculo de temperatura máxima y mínima
    temp_max = f"{df_filtered['Temperatura (°C)'].max():.1f} °C"
    temp_min = f"{df_filtered['Temperatura (°C)'].min():.1f} °C"

    return fig1, fig2, temp_max, temp_min


if __name__ == "__main__":
    app.run_server(debug=True)
