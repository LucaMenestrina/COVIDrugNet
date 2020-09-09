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

prefix="home"

layout=dbc.Col([
            headbar(prefix),
            dbc.Row([
                dbc.Col(sidebar(prefix), width=1, className="bg-light"),
                dbc.Col([
                    html.Br(),
                    dbc.Col([
                        html.Center(html.H2(html.Strong("COVID-19 Drugs Networker"))),
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
                            ], xs=12, md=4),
                            dbc.Col([
                                html.A([
                                    html.Center([
                                        html.Img(src="https://drive.google.com/uc?export=view&id=1RMYDzIHpfsqYWMTd4qA2zWEWT0eYCAfd", style={"width":"95%"}),
                                        html.H5(html.Strong("Drug Drug"), className="card-header")
                                    ])
                                ], href="/drug_drug", className="card border-primary mb-3"),
                            ], xs=12, md=4),
                            dbc.Col([
                                html.A([
                                    html.Center([
                                        html.Img(src="https://drive.google.com/uc?export=view&id=1iDDwsBgJanpOjUAYEE6yuwMmS9D43ap4", style={"width":"95%"}),
                                        html.H5(html.Strong("Target Target"), className="card-header")
                                    ])
                                ], href="/target_target", className="card border-primary mb-3"),
                            ], xs=12, md=4)
                        ]),
                        html.Br(),
                        html.P([html.Font("For help browsing the app check the "),html.A("Help", href="/help"),html.Font(" section")]),
                        html.P([html.Font("Otherwise feel free to "),html.A("reach us out", href="/contacts")]),
                        html.P([html.Font("Info and credits about the project can be found in the "),html.A("About", href="/about"),html.Font(" section")])
                    ]),
                ], className="h-100"),
                footer()
            ], no_gutters=True, style={"height":"100vh"})
        ], style={"padding":"0px"})

# if __name__=="__main__":
#     app.run_server(debug=False)
