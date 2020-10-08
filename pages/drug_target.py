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
prefix="dt"
graph_title="Drug Target"
file_prefix="drug_target"

G=nx.read_gpickle("data/graphs/drug_target.gpickle")
nx.set_node_attributes(G,nx.get_node_attributes(G,"Name"),"id")

nodes=[{"data":{key:value for key,value in attributes.items()}} for node,attributes in dict(G.nodes(data=True)).items()]
edges=[{"data":{"source":source,"target":target}} for source,target in G.edges]

layout=dbc.Col([
            # headbar(prefix),
            dbc.Row([
                dbc.Col(sidebar(prefix), width=1, className="bg-light"),
                dbc.Col([
                    html.Br(),
                    dbc.Row([
                        dbc.Col(graph(prefix, title=graph_title, nodes=nodes, edges=edges), xs=12, md=9),
                        dbc.Col(nodes_info(prefix), md=3)
                    ], no_gutters=True, justify="center"),
                    html.Br(),
                    dbc.Row(dbc.Col(id=prefix+"_selected_table", align="center"), no_gutters=True, justify="center", align="center"),
                    html.Br(),
                    graph_properties(prefix),
                    html.Br(),
                    custom_clustering(prefix),
                    html.Br(),
                    plots(prefix,graph=G, title=graph_title),
                ])
            ], no_gutters=True),
            html.Div(style={"height":"5vh"}),
            footer(),
            html.Div(id=prefix+"_clusters_cache", style={"display":"none"}) #for temporary store computed clusters
        ], style={"padding":"0px"})



##  ----------  CALLBACKS   ------------

build_callbacks(prefix,G,nodes,*common_data_generator(prefix,G,graph_title),file_prefix)


# if __name__=="__main__":
#     app.run_server(debug=False)
