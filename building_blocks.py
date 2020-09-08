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
import os
import pickle
from tqdm import tqdm

import networkx as nx

import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from sklearn.cluster import KMeans

def headbar(prefix):
    return dbc.NavbarSimple([
            dbc.NavItem(dbc.NavLink("Home",href="/covid19drugsnetworker", active=True, className="nav-link active"), className="nav-item"),
            dbc.NavItem(dbc.NavLink("Help",href="/help", active=True, className="nav-link active"), className="nav-item"),
            dbc.NavItem(dbc.NavLink("About",href="/about", active=True, className="nav-link active"), className="nav-item"),
            dbc.NavItem(dbc.NavLink("Contacts",href="/contacts", active=True, className="nav-link active"), className="nav-item"),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem("Drug Target", href="/drug_target", className="dropdown-item"),
                dbc.DropdownMenuItem("Drug Drug", href="/drug_drug", className="dropdown-item"),
                dbc.DropdownMenuItem("Target Target", href="/target_target", className="dropdown-item"),
                # dbc.DropdownMenuItem("Target Disease", href="/target_disease", className="dropdown-item"),
                # dbc.DropdownMenuItem("Target Interactors", href="/target_interactors", className="dropdown-item"),
                ],
                nav=True,
                in_navbar=True,
                label="Other Graphs ...",
                className="nav-item dropdown"
            )],
            className="navbar navbar-primary bg-primary m-auto position-sticky",
            brand="COVID-19 Drugs Networker",
            color="primary",
            dark=True,
            sticky="top",
            fluid=True,
            style={"box-shadow":"0px 2px 5px black"}
            )

def sidebar(prefix):
    if prefix in ["dt","dd","tt"]:
        return dbc.NavbarSimple(dbc.Col([
                    dbc.NavItem(dbc.NavLink("Graph", href="#"+prefix+"_graph_container", external_link=True, active=True, className="nav-link"), className="nav-item"),
                    dbc.NavItem(dbc.NavLink("Selected Data", href="#"+prefix+"_selected_table", external_link=True, id=prefix+"_side_selected_table", active=False, disabled=True, className="nav-link"), className="nav-item"),
                    dbc.NavItem(dbc.NavLink("Graph Properties", href="#"+prefix+"_graph_properties_table", external_link=True, active=True, className="nav-link"), className="nav-item"),
                    dbc.NavItem(dbc.NavLink("Clustering", href="#"+prefix+"_clustering",external_link=True, active=True, className="nav-link"), className="nav-item"),
                    dbc.NavItem(dbc.NavLink("Plots", href="#"+prefix+"_plots",external_link=True, active=True, className="nav-link"), className="nav-item"),
                ], align="center", style={"padding":"0rem"}), expand="xl", color="light", className="navbar navbar-light bg-light position-sticky", style={"position":"sticky", "top":"10vh"})
    else:
        return dbc.NavbarSimple(color="light", className="navbar navbar-light bg-light position-sticky")

def nodes_info(prefix):
    return dbc.Container([
                html.Div([
                    html.H4("Node Info",id=prefix+"_name_card", className="card-header"),
                    html.Div(html.H5(id=prefix+"_title_card",className="card-title"),className="card-body"),
                    dbc.Container(id=prefix+"_img_card", fluid=True, style={"padding":"0px", "position":"relative"}),
                    # html.A(html.Img(id=prefix+"_img_card", height="auto", width="100%"), target="_blank", id=prefix+"_structure3d_href"),#Structure Image Not Available
                    html.Ul(id=prefix+"_attributes-list-card",className="list-group list-group-flush")
                ],className="card border-primary mb-3", id=prefix+"_card"),
                dbc.Toast(
                    html.P(["The node's info are locked on the selected node.",html.Br(),"To show those relative to the hovered ones unselect it"]),
                    header="One node selected",
                    id=prefix+"_selected_node_warning",
                    dismissable=True,
                    is_open=False,
                    duration=10000,
                    icon="warning",
                    style={"position":"fixed","top":"22vh","left":"65vw","min-width":"20vw", "max-width":"20vw"}#just width doesn't work
                )
            ])

def graph_help(prefix):
    return html.Div([
            dbc.Button("Help", id=prefix+"_help_open", block=True),
            dbc.Popover([
                dbc.PopoverHeader("Graph's Interactions"),
                dbc.PopoverBody([
                    html.P("Pan to move around"),
                    html.P("Scroll to zoom"),
                    html.P("Click to select (and lock node's info)"),
                    html.P("CTRL or MAIUSC + Click for multiple selection"),
                    html.P("CTRL + Drag for square selection")
                ])
            ], id=prefix+"_help_popover", target=prefix+"_help_open", placement="bottom")
        ])

def legend(prefix):
    return html.Div([
            dbc.Button("Legend", id=prefix+"_legend_open", block=True),
            dbc.Toast(
                header="Graph's Legend",
                id=prefix+"_legend_toast",
                dismissable=True,
                style={"position":"absolute","top":"-4vh","left":"-12vw", "width":"200%","z-index":"1100"},
                is_open=False
            )
        ])

def save_graph(prefix):
    return html.Div([
            dbc.Button("Save", id=prefix+"_save_graph_open", block=True),
            dbc.Modal([
                dbc.ModalHeader("Save Graph"),
                dbc.ModalBody([
                    html.P("Format"),
                    dcc.Dropdown(id=prefix+"_save_graph", options=[
                        {"label":"Download as Adjacency List", "value":"adjlist"},
                        {"label":"Download as Pickle", "value":"pickle"},
                        {"label":"Download as Cytoscape JSON", "value":"cyjs"},
                        {"label":"Download as GRAPHML", "value":"graphml"},
                        {"label":"Download as GEXF", "value":"gexf"},
                        {"label":"Download as Edges List", "value":"edgelist"},
                        {"label":"Download as Multiline Adjacency List", "value":"multiline_adjlist"},
                        {"label":"Download as TSV", "value":"tsv"},
                        {"label":"Download as SVG", "value":"svg"},
                        {"label":"Download as PNG", "value":"png"},
                        {"label":"Download as JPEG", "value":"jpg"}
                    ], placeholder="Download as ...", clearable=False, searchable=False, className="DropdownMenu")
                ]),
                dbc.ModalFooter([
                    html.A(dbc.Button("Download", id=prefix+"_download_graph_button", className="ml-auto"),id=prefix+"_download_graph_button_href", target="_blank"),
                    dbc.Button("Close", id=prefix+"_save_graph_close", className="ml-auto")
                ]),
            ], id=prefix+"_save_graph_modal")
        ])

def coloring_dropdown(prefix):
    if prefix == "dt":
        options=[{"label":"Categorical", "value":"categorical"}]
        value="categorical"
    if prefix == "dd":
        options=[{"label":"ATC Code", "value":"atc"}]
        value="atc"
    if prefix == "tt":
        options=[{"label":"Cellular Location", "value":"location"}]
        value="location"
    options+=[
        {"label":"Components", "value":"components"},
        {"label":"Spectral Clustering", "value":"spectral"},
        {"label":"Spectral Clustering (Major Component)", "value":"spectral_maj"},
        {"label":"Girvan-Newman Communities", "value":"girvan_newman"},
        {"label":"Girvan-Newman Communities (Major Component)", "value":"girvan_newman_maj"},
        {"label":"Greedy Modularity Communities", "value":"greedy_modularity"},
        {"label":"Greedy Modularity Communities (Major Component)", "value":"greedy_modularity_maj"},
        {"label":"Custom (It might take a few seconds to update...)", "value":"custom"},
    ]
    return html.Div([
            dcc.Dropdown(id=prefix+"_coloring_dropdown", options=options, value=value, clearable=False),
            dbc.Tooltip("Select Graph Coloring", target=prefix+"_coloring_div", placement="top")
        ], id=prefix+"_coloring_div")

def highlighting(prefix, nodes):
    return dcc.Dropdown(id=prefix+"_highlighter_dropdown",options=[{"label":data["name"],"value":data["ID"]} for data in [node["data"] for node in nodes]], placeholder="Highlight a node", multi=True, className="DropdownMenu")

def graph(prefix,title,nodes,edges):#es. title="Drug Target"
    # cyto.load_extra_layouts()
    return dbc.Container([
                html.H4(title,id=prefix+"_name_graph", className="card-header"),
                dbc.Row([
                    dbc.Col(graph_help(prefix), width=1),
                    dbc.Col(legend(prefix), width=1),
                    dbc.Col(save_graph(prefix), width=1),
                    dbc.Col(coloring_dropdown(prefix), width=4),
                    dbc.Col(highlighting(prefix, nodes), width=5),
                    # dbc.Col(html.A("download", href="data:text/csv;charset=utf-8,"+quote(pd.read_csv("https://raw.githubusercontent.com/LucaMenestrina/SARS-CoV-2_Networker/master/drugtarget.tsv",index_col=0, sep="\t").to_csv(sep="\t", index=False, encoding="utf-8")), target="_blank", download="sparsematrix.tsv"), width=1.5),
                ], no_gutters=True, className="card-title"),
                cyto.Cytoscape(
                    id=prefix+"_graph",
                    layout={
                        "name":"cose-bilkent",
                        "nodeRepulsion":1e4,
                        "numIter":2500,
                        "tile":False,
                        "quality":"draft",
                        "gravity":100,
                        "animate":False,
                        # "idealEdgeLength":100,
                        # "gravity":0.2,
                        # "gravityRange":0.05

                    },
                    style={"width":"100%","height":"1000px"},
                    elements=nodes+edges,
                    boxSelectionEnabled=True,
                    minZoom=0.05,
                    maxZoom=10,
                    responsive=True,
                    className="card border-secondary mb-3")
            ], fluid=True, id=prefix+"_graph_container")

#######
# graph_properties_df=pd.DataFrame({node:{prop:values[prop] for prop in ["name","degree", "Closeness_Centrality", "Betweenness_Centrality"]} for node,values in dict(G.nodes(data=True)).items()}).T

def graph_properties(prefix):
    return dbc.Container([
                dbc.Col([
                    dbc.Row(html.H3("Graph Properties")),
                    dbc.Row([
                        # dbc.Col(width=1), # just to move everything to the right (justify doesn't work)
                        dbc.Col([dcc.Checklist(options=[{"label":"Only Selected","value":True}],id=prefix+"_only_selected_properties", labelStyle={"white-space":"nowrap", "margin-left":"1rem"}),dbc.Tooltip(["Show only those nodes that are manually selected in the Graph",html.Br(),"(If there are ...)"], target=prefix+"_only_selected_properties", placement="top")], align="center"),
                        dbc.Col([
                            dcc.Dropdown(id=prefix+"_search_properties", placeholder="Search Specific Nodes ...", multi=True, className="DropdownMenu")
                        ], align="center", width=4),
                        dbc.Col(html.Font("Sort by: ", style={"white-space":"nowrap"}),align="center", style={"text-align":"right"}),
                        dbc.Col([
                            dcc.Dropdown(id=prefix+"_properties_table_sorting",  options=[
                                {"label":"Degree: Low to High","value":"degree,1"},
                                {"label":"Degree: High to Low","value":"degree,0"},
                                {"label":"Closeness Centrality: Low to High","value":"Closeness_Centrality,1"},
                                {"label":"Closeness Centrality: High to Low","value":"Closeness_Centrality,0"},
                                {"label":"Betweenness Centrality: Low to High","value":"Betweenness_Centrality,1"},
                                {"label":"Betweenness Centrality: High to Low","value":"Betweenness_Centrality,0"}
                            ], value="degree,0", clearable=False, searchable=False, optionHeight=25,className="DropdownMenu")
                        ],align="center", width=3),
                        dbc.Col(html.Font("Rows to show: ", style={"white-space":"nowrap"}),align="center", style={"text-align":"right"}),
                        dbc.Col([
                            dcc.Dropdown(id=prefix+"_properties_table_rows",options=[
                                {"label":"10","value":10},
                                {"label":"25","value":25},
                                {"label":"50","value":50},
                                {"label":"100","value":100},
                                {"label":"all","value":"all"}
                            ], value=10, className="DropdownMenu", clearable=False, searchable=False, optionHeight=25)
                        ],align="center"),
                        dbc.Col(html.A(dbc.Button("Download", className="ml-auto"), target="_blank", download="graph_properties.tsv", id=prefix+"_download_graph_properties"), align="center")
                    ], justify="center", align="center"),
                    html.Br(),
                    dbc.Container(id=prefix+"_graph_properties_table_container", fluid=True)
                ])
            ], fluid=True, style={"padding":"3%"})

def view_custom_clusters(prefix):
    return dbc.Container([
                html.Br(),
                dbc.Button("View Table", id=prefix+"_view_clusters_open"),
                dbc.Modal([
                    dbc.ModalHeader("Custom Clusters Table"),
                    dbc.ModalBody([
                        dbc.Container(id=prefix+"_custom_clusters_table_container", fluid=True)
                    ]),
                    dbc.ModalFooter([
                        html.A(dbc.Button("Download", className="ml-auto"), target="_blank", download="custom_clusters.tsv", id=prefix+"_download_custom_clusters_modal"),
                        dbc.Button("Close", id=prefix+"_view_clusters_close", className="ml-auto")
                    ]),
                ],id=prefix+"_custom_clusters_modal", size="xl"),
            ])

def custom_clustering(prefix):
    return dbc.Container([
                html.H3("Clustering"),
                dbc.Row([
                    dbc.Col(dbc.Spinner(dcc.Graph(id=prefix+"_custom_clustering_graph")), width=6),
                    dbc.Col([
                        dcc.Dropdown(id=prefix+"_custom_clustering_component", options=[
                            {"label":"Entire Graph","value":"entire"},
                            {"label":"Major Component","value":"maj"}
                        ], value="entire", clearable=False, searchable=False, optionHeight=25,className="DropdownMenu"),
                        html.Label("Method:"),
                        dcc.Dropdown(id=prefix+"_custom_clustering_method", options=[
                            {"label":"Spectral Clustering","value":"spectral"},
                            {"label":"Girvan Newman","value":"girvan_newman"},
                            {"label":"Greedy Modularity","value":"greedy_modularity"}
                        ], value="spectral", clearable=False, searchable=False, optionHeight=25,className="DropdownMenu"),
                        html.Label("Number of clusters:"),
                        dcc.Dropdown(id=prefix+"_custom_clustering_number_clusters", clearable=False, optionHeight=25,className="DropdownMenu"),
                        view_custom_clusters(prefix)
                    ], align="center", width=2)
                ], justify="center", align="center", no_gutters=True)
            ], id=prefix+"_clustering", fluid=True, style={"padding":"3%"})

def common_data_generator(prefix,graph):
    print(prefix)
    graph_properties_df=pd.DataFrame({node:{prop:values[prop] for prop in ["name","degree", "Closeness_Centrality", "Betweenness_Centrality"]} for node,values in dict(graph.nodes(data=True)).items()}).T
    maj=graph.subgraph(max(list(nx.connected_components(graph)), key=len))
    if os.path.isfile("data/gn_communities/"+prefix+"_communities.pickle"):
        with open("data/gn_communities/"+prefix+"_communities.pickle","rb") as bkp:
            girvan_newman,girvan_newman_maj=pickle.load(bkp)
    else:
        girvan_newman={len(comm):comm for comm in tqdm(nx.algorithms.community.girvan_newman(graph))}
        girvan_newman_maj={len(comm):comm for comm in tqdm(nx.algorithms.community.girvan_newman(maj))}
        name="data/gn_communities/"+prefix+"_communities.pickle"
        with open(name,"wb") as bkp:
            pickle.dump([girvan_newman,girvan_newman_maj],bkp)
        if os.path.isfile(name+".bkp"):
                os.remove(name+".bkp")
    return graph_properties_df,girvan_newman,maj,girvan_newman_maj

def get_frequency(list):
  d={}
  for el in list:
    try:
      d[el]+=1
    except:
      d[el]=1
  return d

def powerplot(graph):
    K=dict(nx.get_node_attributes(graph,"degree"))
    power_data=pd.DataFrame({"Node degree, k":list(get_frequency(K.values()).values()),"Number of Nodes with degree k, n(k)":list(get_frequency(K.values()).keys())})

    return px.scatter(data_frame=power_data,x="Node degree, k",y="Number of Nodes with degree k, n(k)", title="Node Degree Distribution", height=600, width=600)

def plots(prefix, graph):
    return dbc.Container([
                html.H3("Plots"),
                dbc.Row([
                    dbc.Col([dbc.Spinner(dcc.Graph(figure=powerplot(graph), id=prefix+"_powerplot"))], width=4, align="center"),
                    dbc.Col([dbc.Spinner(dcc.Graph(id=prefix+"_piechart"))],width=6 , align="center")
                ], justify="center", align="around", no_gutters=True)
            ], id=prefix+"_plots", fluid=True, style={"padding":"3%"})

def footer():
    return dbc.Container([
                html.Br(),
                html.P([html.A(html.Small("Write us"), href="mailto:luca.menestrina2@unibo.it"),html.Small(" if you have questions and suggestions"), html.Br(), html.Small("App developed by Luca Menestrina, Department of Pharmacy and Biotechnology, University of Bologna, Italy")]),
                # dbc.Row(html.Small("Copyright \u00A9 2020 Luca Menestrina All rights reserved")) # controllo le licenze di github
            ], fluid=True, className="bg-light")
