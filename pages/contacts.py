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

layout=dbc.Row([
        dbc.Col(sidebar(prefix), width=1, className="bg-light"),
        dbc.Col([
            headbar(prefix),
            # html.Br(),
            # html.H1("COVID-19 Networker", style={"text-align":"center"}),
            html.Br(),
            html.H3("Contacts"),
            html.Br(),
            dbc.Col([
                html.Div([
                    dbc.Row([
                        dbc.Col([html.Img(src="https://icon-library.com/images/user-icon-image/user-icon-image-13.jpg", style={"width":"75%"})], width=1),
                        dbc.Col([
                            html.Strong("Maurizio Recanatini"),
                            html.P("Principal Investigator"),
                            html.Address("maurizio.recanatini@unibo.it")
                        ])
                    ]),
                    html.P("Brief introduction/description "*10)
                ]),
                html.Br(),
                html.Br(),
                html.Div([
                    dbc.Row([
                        dbc.Col([html.Img(src="https://f0.pngfuel.com/png/363/793/person-with-brown-hair-illustration-png-clip-art.png", style={"width":"75%"})], width=1),
                        dbc.Col([
                            html.Strong("Chiara Cabrelle"),
                            html.P("PhD Student in Biotechnological, Biocomputational, Pharmaceutical and Pharmacological Science"),
                            html.Address("chiara.cabrelle2@unibo.it")
                        ])
                    ]),
                    html.P("Brief introduction/description "*10)
                ]),
                html.Br(),
                html.Br(),
                html.Div([
                    dbc.Row([
                        dbc.Col([html.Img(src="https://icon-library.com/images/user-icon-image/user-icon-image-13.jpg", style={"width":"75%"})], width=1),
                        dbc.Col([
                            html.Strong("Luca Menestrina"),
                            html.P("PhD Student in Data Science and Computation"),
                            html.Address("luca.menestrina2@unibo.it")
                        ])
                    ]),
                    html.P("Brief introduction/description "*10)
                ]),
            html.Br()
            ]),
        ], className="h-100"),
        footer()
    ], no_gutters=True, style={"height":"100vh"})

# if __name__=="__main__":
#     app.run_server(debug=False)
