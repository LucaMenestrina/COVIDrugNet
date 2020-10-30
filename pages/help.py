# import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
# import dash_cytoscape as cyto
# from dash.dependencies import Output,Input, State
# import plotly.graph_objs as go
# import plotly.express as px
# import dash_table
#
# from urllib.request import quote
#
# import pandas as pd
# import numpy as np
#
# import networkx as nx
#
# import matplotlib.pyplot as plt
# from matplotlib.colors import rgb2hex
# from sklearn.cluster import KMeans
#
# from app import app
from building_blocks import *
from callbacks import *

# app=dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
# app.title="COVID-19 Networker"

prefix="help"

layout=dbc.Col([
            # headbar(prefix),
            dbc.Col([
                html.Br(),
                dbc.Col([
                    html.H3("Help"),
                    html.Br(),
                    html.Center([
                        html.Img(src=app.get_asset_url("imgs/help.svg"), style={"width":"100%"})
                    ]),
                    # html.Br(),
                    # html.Br(),
                    # dbc.Row([
                    #     dbc.Col([
                    #         html.Center(html.H5([html.Font("If there still is something unclear feel free to "),html.A("reach us out", href="/contacts")], style={"margin":"0px"}))
                    #     ], className="card border-primary", width=5, align="center", style={"padding":"2%"})
                    # ], no_gutters=True, justify="center", align="center"),
                    html.Div(style={"height":"10vh"})
                    ], style={"padding":"2%", "width":"100%"}),
            ]),
        footer()
        ], style={"padding":"0px"})


##  ----------  CALLBACKS   ------------

collapse_headbar_callback(prefix)

# if __name__=="__main__":
#     app.run_server(debug=False)
