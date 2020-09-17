import dash
import dash_bootstrap_components as dbc

meta=[
    {
        "name": "author",
        "content": "Luca Menestrina"
    },
    {
        "name": "title",
        "content": "COVID-19 Drugs Networker"
    },
    {
        "name": "description",
        "content": "Collects and visualizes network info about drugs and targets related to COVID-19 "
    },
    {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }
]

font_awesome = {
        "href": "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
        "rel": "stylesheet",
        "integrity": "sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf",
        "crossorigin": "anonymous"
    }

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN, font_awesome], suppress_callback_exceptions=True, meta_tags=meta, assets_folder="data")

# server = app.server
app.title="COVID-19 Drugs Networker"
