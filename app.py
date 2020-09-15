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

font_awesome="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/css/all.min.css"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN, font_awesome], suppress_callback_exceptions=True, meta_tags=meta)

# server = app.server
app.title="COVID-19 Drugs Networker"
