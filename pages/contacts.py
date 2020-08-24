import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Output,Input, State
import plotly.graph_objs as go
import plotly.express as px
import dash_table

from urllib.request import quote

import pandas as pd
import numpy as np

import networkx as nx

import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from sklearn.cluster import KMeans

from app import app
from building_blocks import *
from callbacks import *

# app=dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
# app.title="COVID-19 Networker"

prefix="contacts"

layout=dbc.Container([
    dbc.Row([
        dbc.Col(sidebar(prefix), width=1, className="bg-light"),
        dbc.Col([
            headbar(prefix),
            # html.Br(),
            # html.H1("COVID-19 Networker", style={"text-align":"center"}),
            html.Br(),
            dbc.Col([
                html.Div([
                    html.Strong("Maurizio Recanatini"),
                    html.P("Principal Investigator"),
                    html.Address("maurizio.recanatini@unibo.it")
                ]),
                html.Div([
                    html.Strong("Chiara Cabrelle"),
                    html.P("PhD Student"),
                    html.Address("chiara.cabrelle2@unibo.it")
                ]),
                html.Div([
                    html.Strong("Luca Menestrina"),
                    html.P("PhD Student"),
                    html.Address("luca.menestrina2@unibo.it")
                ])
            ]),
        footer()
        ]),
    ], no_gutters=True)
], fluid=True)

# if __name__=="__main__":
#     app.run_server(debug=False)
