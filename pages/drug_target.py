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

G=nx.read_gpickle("data/drug_target.pickle")
nx.set_node_attributes(G,nx.get_node_attributes(G,"name"),"id")

nodes=[{"data":{key:value for key,value in attributes.items()}} for node,attributes in dict(G.nodes(data=True)).items()]#, "position":{"x":attributes["pos"][0]*1000,"y":attributes["pos"][1]*1000}
edges=[{"data":{"source":source,"target":target}} for source,target in G.edges]
# [node for node in nodes if node["data"]["name"]=="Remdesivir"]

graph_properties_df=pd.DataFrame({node:{prop:values[prop] for prop in ["name","degree", "Closeness_Centrality", "Betweenness_Centrality"]} for node,values in dict(G.nodes(data=True)).items()}).T

cyto.load_extra_layouts()

layout=dbc.Container([
    dbc.Row([
        dbc.Col(sidebar(prefix), width=1, className="bg-light"),
        dbc.Col([
        headbar(prefix),
        # html.Br(),
        # html.H1("COVID-19 Networker", style={"text-align":"center"}),
        html.Br(),
        dbc.Row([
            dbc.Col(graph(prefix, title=graph_title, nodes=nodes, edges=edges), width=9),
            dbc.Col(nodes_info(prefix), width=3)
        ], justify="left"),
        html.Br(),
        dbc.Row(dbc.Col(id=prefix+"_selected_table", width=10), justify="center"),
        html.Br(),
        graph_properties(prefix),
        html.Br(),
        custom_clustering(prefix),
        html.Br(),
        plots(prefix,graph=G),
        ]),
        footer()
    ], no_gutters=True)
], fluid=True)




##  ----------  CALLBACKS   ------------

displayHoverNodeData_callback(prefix,G)
selectedTable_callback(prefix)
propertiesTable_callback(prefix,graph_properties_df)
highlighter_callback(prefix,G,nodes)
toggle_download_img_callback(prefix)
toggle_help_callback(prefix)
toggle_legend_callback(prefix)
get_img_callback(prefix)
get_range_clusters_callback(prefix,G)
custom_clustering_section_callback(prefix,G)
toggle_view_clusters_callback(prefix)

# if __name__=="__main__":
#     app.run_server(debug=False)
