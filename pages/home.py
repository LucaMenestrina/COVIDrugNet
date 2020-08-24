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
                dbc.Row([
                    dbc.Col([
                        html.A([
                            html.Img(src="data/drug_target_img.jpg"),
                            html.H5(html.Strong("Drug Target"))
                        ], href="/drug_target"),
                    ]),
                    dbc.Col([
                        html.A([
                            html.Img(src="data/drug_drug_img.jpg"),
                            html.H5(html.Strong("Drug Drug"))
                        ], href="/drug_drug"),
                    ]),
                    dbc.Col([
                        html.A([
                            html.Img(src="data/target_target_img.jpg"),
                            html.H5(html.Strong("Target Target"))
                        ], href="/target_target"),
                    ])
                ]),
                html.Br(),
                html.P([html.Font("For help browising the app check the "),html.A("Help", href="/help"),html.Font(" section")]),
                html.P([html.Font("Otherwise feel free to "),html.A("reach us out", href="/contacts")]),
                html.Br(),
                html.P([html.Font("Info and credits about the project can be found in the "),html.A("About", href="/about"),html.Font(" section")])
            ]),
        ]),
        footer()
    ], no_gutters=True)
], fluid=True)

# if __name__=="__main__":
#     app.run_server(debug=False)
