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

prefix="help"

layout=dbc.Col([
            headbar(prefix),
            dbc.Row([
                dbc.Col(sidebar(prefix), width=1, className="bg-light"),
                dbc.Col([
                    html.Br(),
                    dbc.Col([
                        html.Br(),
                        html.Center([
                            html.Img(src="https://drive.google.com/uc?export=view&id=1Wz-BWDC-hbsm1GMoGlHcE2UpvW6xnEwy", style={"width":"100%"})
                        ]),
                        html.Br(),
                        html.Br(),
                        html.P([html.Font("If there still is something unclear feel free to "),html.A("reach us out", href="/contacts")]),
                        html.Br(),
                    ]),
                ], className="h-100"),
                footer()
            ], no_gutters=True)
        ], style={"padding":"0px"})

# if __name__=="__main__":
#     app.run_server(debug=False)
