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

layout=dbc.Col([
            # headbar(prefix),
            dbc.Col([
                html.Br(),
                dbc.Col([
                    html.H3("Contacts"),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([html.Img(src="https://icon-library.com/images/user-icon-image/user-icon-image-13.jpg", style={"width":"100%"})], xs=3, md=2, xl=1, align="center"),
                        dbc.Col([
                            html.H5(html.Strong("Maurizio Recanatini")),
                            html.P("Principal Investigator"),
                            html.A("maurizio.recanatini@unibo.it", href="mailto:maurizio.recanatini@unibo.it", style={"color":"black"}),
                            html.Br(),
                            html.Br(),
                            html.P([
                                "I'm a Professor of Medicinal Chemistry since year 2000",
                                html.Br(),
                                "My research fields are the design/ identification of biologically active molecules and the study of target biological systems through the application of computational tools ranging from QSAR (today, we’d rather say statistical learning) to molecular modeling and simulations."
                                ])
                        ])
                    ], justify="around", align="center"),
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([html.Img(src="https://f0.pngfuel.com/png/363/793/person-with-brown-hair-illustration-png-clip-art.png", style={"width":"100%"})], xs=3, md=2, xl=1, align="center"),
                        dbc.Col([
                            html.H5(html.Strong("Chiara Cabrelle")),
                            html.P("PhD Student in Biotechnological, Biocomputational, Pharmaceutical and Pharmacological Science"),
                            html.A("chiara.cabrelle2@unibo.it", href="mailto:chiara.cabrelle2@unibo.it", style={"color":"black"}),
                            html.Br(),
                            html.Br(),
                            html.P("Brief introduction/description "*10)
                        ])
                    ], justify="around", align="center"),
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([html.Img(src="https://icon-library.com/images/user-icon-image/user-icon-image-13.jpg", style={"width":"100%"})], xs=3, md=2, xl=1, align="center"),
                        dbc.Col([
                            html.H5(html.Strong("Luca Menestrina")),
                            html.P("PhD Student in Data Science and Computation"),
                            html.A("luca.menestrina2@unibo.it", href="mailto:luca.menestrina2@unibo.it", style={"color":"black"}),
                            html.Br(),
                            html.Br(),
                            html.P([
                                "I'm a medicinal chemist and technology enthusiast.",
                                html.Br(),
                                "My research interests are.......",
                                html.Br(),
                                "Please help me improving this app: if you find any malfunction (sure there are...) or you have suggestions, drop me an email."
                            ])
                        ])
                    ], justify="around", align="center"),
                    html.Br()
                ], style={"padding":"2%", "width":"100%"})
            ], style={"height":"100vh"}),
            footer()
        ], style={"padding":"0px"})


##  ----------  CALLBACKS   ------------

collapse_headbar_callback(prefix)

# if __name__=="__main__":
#     app.run_server(debug=False)
