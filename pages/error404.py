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
# app.title="COVID-19 Drugs Networker"

prefix="about"

layout=dbc.Col([
            headbar(prefix),
            dbc.Row([
                dbc.Col(sidebar(prefix), width=1, className="bg-light"),
                dbc.Col([
                    html.Br(),
                    dbc.Col([
                        html.Center([
                            html.Div(style={"height":"10vh"}),
                            html.H2("404 Page Not Found"),
                            html.Br(),
                            html.H3("Sorry, we can't find that page ..."),
                            html.Br(),
                            html.H5("Please check the URL and try again ..."),
                            html.Div(style={"height":"25vh"})
                        ]),
                        dbc.Row([
                            dbc.Col(width=1),
                            dbc.Col([
                                html.P([html.Font("Try to go back to our "),html.A("homepage", href="/covid19drugsnetworker")]),
                                html.P([html.Font("If the problem persists feel free to "),html.A("reach us out", href="mailto:luca.menestrina2@unibo.it")])
                            ])
                        ])
                    ])
                ], className="h-100"),
                footer()
            ], no_gutters=True, style={"height":"100vh"})
        ], style={"padding":"0px"})

# if __name__=="__main__":
#     app.run_server(debug=False)
