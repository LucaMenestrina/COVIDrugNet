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

prefix="about"

layout=dbc.Container([
    dbc.Row([
        dbc.Col(sidebar(prefix), width=1, className="bg-light"),
        dbc.Col([
            headbar(prefix),
            # html.Br(),
            # html.H1("COVID-19 Networker", style={"text-align":"center"}),
            html.Br(),
            dbc.Col([
                html.H3("Info about the project..."),
                html.P("Reference to article... and citing..."),
                html.Br(),
                html.H3("Credits:"),
                html.Ul([
                    html.Li("DrugBank"),
                    html.Li("Uniprot"),
                    html.Li("String"),
                    html.Li("Dash"),
                    html.Li("Networkx"),
                    html.Li(html.P([html.Font("Favicon made by "),html.A("Becris", href="https://creativemarket.com/Becris"),html.Font(" from "),html.A("www.flaticon.com", href="https://www.flaticon.com/")]))
                ]),
            html.Br(),
            html.H4("Terms of Use"),
            html.P("Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")
            ])
        ]),
        footer()

    ], no_gutters=True)
], fluid=True)

# if __name__=="__main__":
#     app.run_server(debug=False)
