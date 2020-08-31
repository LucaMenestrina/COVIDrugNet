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
#SARS-CoV-2_Networker
prefix="home"

layout=dbc.Container([
    dbc.Row([
        dbc.Col(sidebar(prefix), width=1, className="bg-light"),
        dbc.Col([
            headbar(prefix),
            # html.Br(),
            # html.H1("COVID-19 Networker", style={"text-align":"center"}),
            html.Br(),
            dbc.Col([
                html.Center(html.H2(html.Strong("SARS-CoV-2 Networker"))),
                html.P("Welcome to ... bla bla bla..."),
                html.Br(),
                html.H4("Available Graphs:"),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.A([
                            html.Center([
                                html.Img(src="https://drive.google.com/uc?export=view&id=1Dsog5C3jKZXHssGqVCd9BOiP15KULK8W", style={"width":"95%"}),
                                html.H5(html.Strong("Drug Target"), className="card-header")
                            ])
                        ], href="/drug_target", className="card border-primary mb-3"),
                    ]),
                    dbc.Col([
                        html.A([
                            html.Center([
                                html.Img(src="https://drive.google.com/uc?export=view&id=1RMYDzIHpfsqYWMTd4qA2zWEWT0eYCAfd", style={"width":"95%"}),
                                html.H5(html.Strong("Drug Drug"), className="card-header")
                            ])
                        ], href="/drug_drug", className="card border-primary mb-3"),
                    ]),
                    dbc.Col([
                        html.A([
                            html.Center([
                                html.Img(src="https://drive.google.com/uc?export=view&id=1iDDwsBgJanpOjUAYEE6yuwMmS9D43ap4", style={"width":"95%"}),
                                html.H5(html.Strong("Target Target"), className="card-header")
                            ])
                        ], href="/target_target", className="card border-primary mb-3"),
                    ])
                ]),
                html.Div(style={"height":"100px"}),
                html.P([html.Font("For help browising the app check the "),html.A("Help", href="/help"),html.Font(" section")]),
                html.P([html.Font("Otherwise feel free to "),html.A("reach us out", href="/contacts")]),
                html.P([html.Font("Info and credits about the project can be found in the "),html.A("About", href="/about"),html.Font(" section")])
            ]),
        ]),
        footer()
    ], no_gutters=True)
], fluid=True)

# if __name__=="__main__":
#     app.run_server(debug=False)
