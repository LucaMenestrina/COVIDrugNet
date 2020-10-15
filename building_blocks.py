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
from networkx.algorithms.community import modularity

import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from sklearn.cluster import KMeans
from scipy.stats import halfnorm

from app import app

loading_banner = html.Div(
        html.Center([
            html.Div(style={"height":"20vh"}),
            dbc.Fade(
                dbc.Jumbotron([
                    html.H2("Sorry, it's taking some time to load ..."),
                    html.Hr(),
                    html.H5("Networks are becoming more and more complex"),
                    html.H5("and the browser could take a while to render the page"),
                    html.P(["If it takes too long (or it doesn't load at all) please let us know"]),#, html.A("let us know", href="mailto:luca.menestrina2@unibo.it")
                    # html.Img(src=app.get_asset_url("imgs/icon.png"), style={"height":"10vh"}),
                    html.Br(),
                    html.Small("A small banner could also appear on top of your window saing that a calculation is slowing down your browser")
                ], style={"width":"40vw"}
            ), is_in=True, timeout=250)]
        ),id="page_content")

def headbar():
    return dbc.Navbar(
                dbc.Container([
                    html.A(
                        dbc.Row([
                            html.Img(src=app.get_asset_url("imgs/logo_white.svg"), style={"height":"4vh", "margin-right":"1rem"}),#"https://drive.google.com/uc?export=view&id=1itcOUu62U0YHlNMQITA-17rR-iYIqXz3"
                            dbc.NavbarBrand("COVID-19 Drugs Networker")
                        ], no_gutters=True, justify="start", align="center"),
                    href="/covid19drugsnetworker", className="card-link"),
                    dbc.NavbarToggler(id="headbar_toggler"),
                    dbc.Collapse([
                        dbc.Nav([
                            dbc.NavItem(dbc.NavLink([html.I(className="fa fa-home", style={"margin-right":"0.4rem"}),"Home"],href="/covid19drugsnetworker", active=True, className="nav-link active", external_link=True), className="nav-item", id="home_nav"),
                            dbc.Tooltip("COVID-19 Drugs Networker Homepage", target="home_nav", placement="bottom", hide_arrow=True, delay={"show":500, "hide":250}),
                            dbc.NavItem(dbc.NavLink([html.I(className="fa fa-question", style={"margin-right":"0.4rem"}),"Help"],href="/help", active=True, className="nav-link active", external_link=True), className="nav-item", id="help_nav"),
                            dbc.Tooltip("Page Structure and Main Possible Interactions", target="help_nav", placement="bottom", hide_arrow=True, delay={"show":500, "hide":250}),
                            dbc.NavItem(dbc.NavLink([html.I(className="fa fa-info", style={"margin-right":"0.4rem"}),"About"],href="/about", active=True, className="nav-link active", external_link=True), className="nav-item", id="about_nav"),
                            dbc.Tooltip("Info About the Project", target="about_nav", placement="bottom", hide_arrow=True, delay={"show":500, "hide":250}),
                            dbc.NavItem(dbc.NavLink([html.I(className="fa fa-address-book", style={"margin-right":"0.4rem"}),"Contacts"],href="/contacts", active=True, className="nav-link active", external_link=True), className="nav-item", id="contacts_nav"),
                            dbc.Tooltip("Project Participant's Contacts", target="contacts_nav", placement="bottom", hide_arrow=True, delay={"show":500, "hide":250}),
                            dbc.Nav([
                                dbc.NavLink(html.I(className="fa fa-project-diagram"), active=True, className="nav-link active", style={"margin-right":"-0.6rem"}), # patch for graphs label icon
                                dbc.DropdownMenu([
                                    dbc.DropdownMenuItem("Drug Target", href="/drug_target", className="dropdown-item", external_link=True),
                                    dbc.DropdownMenuItem("Drug Drug", href="/drug_drug", className="dropdown-item", external_link=True),
                                    dbc.DropdownMenuItem("Target Target", href="/target_target", className="dropdown-item", external_link=True),
                                    # dbc.DropdownMenuItem("Target Disease", href="/target_disease", className="dropdown-item"), # not yet available
                                    # dbc.DropdownMenuItem("Target Interactors", href="/target_interactors", className="dropdown-item") # not yet available
                                ], nav=True, in_navbar=True, label="Graphs ...", className="nav-item dropdown active"),
                            ], className="nav-item", id="other_graphs_nav"),#patch for dropdownmeno label icon , style={"margin-right":"-0.5rem"}
                            dbc.Tooltip("Browse Other Available Graphs", target="other_graphs_nav", placement="left", hide_arrow=True, delay={"show":500, "hide":250})
                        ], className="ml-auto", navbar=True)
                    ], id="headbar_collapse", navbar=True)
                ], fluid=True),
            color="primary",
            dark=True,
            sticky="top",
            style={"box-shadow":"0px 2px 5px darkgrey"}
            )


def sidebar(prefix):
    if prefix in ["dt","dd","tt"]:
        return dbc.NavbarSimple([
                    dbc.Col([
                        dbc.NavItem(dbc.NavLink("Graph", href="#"+prefix+"_graph_container", external_link=True, active=True, className="nav-link"), className="nav-item", id=prefix+"_graph_side"),
                        dbc.Tooltip("Jump to Graph' Section", target=prefix+"_graph_side", placement="right", hide_arrow=True, delay={"show":500, "hide":250}),
                        dbc.NavItem(dbc.NavLink("Selected Data", href="#"+prefix+"_selected_table", external_link=True, id=prefix+"_side_selected_table", active=False, disabled=True, className="nav-link"), className="nav-item", id=prefix+"_selected_data_side"),
                        dbc.Tooltip("Jump to Selected Data' Section", target=prefix+"_selected_data_side", placement="right", hide_arrow=True, delay={"show":500, "hide":250}, id=prefix+"_selected_data_side_tooltip"),
                        dbc.NavItem(dbc.NavLink("Graph Properties", href="#"+prefix+"_graph_properties_table", external_link=True, active=True, className="nav-link"), className="nav-item", id=prefix+"_graph_properties_side"),
                        dbc.Tooltip("Jump to Graph Properties' Section", target=prefix+"_graph_properties_side", placement="right", hide_arrow=True, delay={"show":500, "hide":250}),
                        dbc.NavItem(dbc.NavLink("Clustering", href="#"+prefix+"_clustering",external_link=True, active=True, className="nav-link"), className="nav-item", id=prefix+"_clustering_side"),
                        dbc.Tooltip("Jump to Clustering' Section", target=prefix+"_clustering_side", placement="right", hide_arrow=True, delay={"show":500, "hide":250}),
                        dbc.NavItem(dbc.NavLink("Plots", href="#"+prefix+"_plots",external_link=True, active=True, className="nav-link"), className="nav-item", id=prefix+"_plots_side"),
                        dbc.Tooltip("Jump to Plots' Section", target=prefix+"_plots_side", placement="right", hide_arrow=True, delay={"show":500, "hide":250}),
                    ], align="center", style={"padding":"0px"}),
                ],expand="xl", color="light", className="navbar navbar-light bg-light position-sticky nav", style={"position":"sticky", "top":"10vh"}),
    else:
        return []

def nodes_info(prefix):
    return dbc.Container([
                html.Div([
                    html.H4("Node Info",id=prefix+"_name_card", className="card-header"),
                    html.Div(html.H5(id=prefix+"_title_card",className="card-title"),className="card-body"),
                    dbc.Container(id=prefix+"_img_card", fluid=True, style={"padding":"0px", "position":"relative"}),
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
            dbc.Button("Help", id=prefix+"_help_open", block=True, className="btn btn-outline-primary"),
            dbc.Popover([
                dbc.PopoverHeader("Graph's Interactions"),
                dbc.PopoverBody([
                    html.P("Pan to move around"),
                    html.P("Scroll to zoom"),
                    html.P("Click to select (and lock node's info)"),
                    html.P("CTRL or MAIUSC + Click for multiple selection"),
                    html.P("CTRL + Drag for square selection")
                ])
            ], id=prefix+"_help_popover", target=prefix+"_help_open", placement="bottom"),
            dbc.Tooltip("Tips for Graph's Interactions", target=prefix+"_help_open", placement="top", hide_arrow=True, delay={"show":500, "hide":250})
        ])

def legend(prefix):
    return html.Div([
            dbc.Button("Legend", id=prefix+"_legend_open", block=True, className="btn btn-outline-primary"),
            dbc.Toast(
                header="Graph's Legend",
                id=prefix+"_legend_toast",
                dismissable=True,
                style={"position":"absolute","top":"-4vh","left":"-12vw", "width":"200%","z-index":"1000"},
                is_open=False
            ),
            dbc.Tooltip(["Graph's Legend",html.Br(),"(when available)"], target=prefix+"_legend_open", placement="top", hide_arrow=True, delay={"show":500, "hide":250})
        ])

def save_graph(prefix):
    return html.Div([
            dbc.Button("Save", id=prefix+"_save_graph_open", block=True, className="btn btn-outline-primary"),
            dbc.Modal([
                dbc.ModalHeader("Save Graph"),
                dbc.ModalBody([
                    html.P("Format"),
                    dcc.Dropdown(id=prefix+"_save_graph", options=[
                        {"label":"Download as Adjacency List", "value":"adjlist"},
                        {"label":"Download as Pickle", "value":"gpickle"},
                        {"label":"Download as Cytoscape JSON", "value":"cyjs"},
                        {"label":"Download as GRAPHML", "value":"graphml"},
                        {"label":"Download as GEXF", "value":"gexf"},
                        {"label":"Download as Edges List", "value":"edgelist"},
                        {"label":"Download as Multiline Adjacency List", "value":"multiline_adjlist"},
                        {"label":"Download as TSV", "value":"tsv"},
                        # {"label":"Download as SVG", "value":"svg"}, #temporary not working (why?)
                        {"label":"Download as PNG", "value":"png"},
                        {"label":"Download as JPEG", "value":"jpg"}
                    ], placeholder="Download as ...", clearable=False, searchable=False, className="DropdownMenu")
                ]),
                dbc.ModalFooter([
                    html.A(dbc.Button("Download", id=prefix+"_download_graph_button", className="btn btn-outline-primary"),id=prefix+"_download_graph_button_href", target="_blank"),
                    dbc.Button("Close", id=prefix+"_save_graph_close", className="btn btn-outline-primary")
                ]),
            ], id=prefix+"_save_graph_modal"),
            dbc.Tooltip("Download Graph File", target=prefix+"_save_graph_open", placement="top", hide_arrow=True, delay={"show":500, "hide":250})
        ])

def coloring_dropdown(prefix):
    if prefix == "dt":
        options=[{"label":"Categorical", "value":"categorical"}]
        value="categorical"
    if prefix == "dd":
        options=[{"label":"ATC Code", "value":"atc"},{"label":"Target Class", "value":"targetclass"}]
        value="atc"
    if prefix == "tt":
        options=[{"label":"Protein Class", "value":"class"},{"label":"Protein Family", "value":"family"},{"label":"Cellular Location", "value":"location"}]
        value="class"
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
            dbc.Tooltip("Select Graph Coloring", target=prefix+"_coloring_dropdown_div", placement="top", hide_arrow=True, delay={"show":500, "hide":250})
        ], id=prefix+"_coloring_dropdown_div")

def highlighting(prefix, nodes):
    return html.Div([
            dcc.Dropdown(id=prefix+"_highlighter_dropdown",options=[{"label":data["Name"],"value":data["ID"]} for data in [node["data"] for node in nodes]], placeholder="Highlight a node", multi=True, className="DropdownMenu"),
            dbc.Tooltip("Highlight Specific Nodes for Easier Spotting", target=prefix+"_highlighter_dropdown_div", placement="top", hide_arrow=True, delay={"show":500, "hide":250})
        ],id=prefix+"_highlighter_dropdown_div")

def graph(prefix,title,nodes,edges):
    return dbc.Container([
                html.H4(title,id=prefix+"_name_graph", className="card-header"),
                dbc.Row([
                    dbc.Col(graph_help(prefix), width=1),
                    dbc.Col(legend(prefix), width=1),
                    dbc.Col(save_graph(prefix), width=1),
                    dbc.Col(coloring_dropdown(prefix), width=4),
                    dbc.Col(highlighting(prefix, nodes), width=5),
                ], no_gutters=True, className="card-title", justify="around", align="center"),
                dcc.Loading(cyto.Cytoscape(
                    id=prefix+"_graph",
                    layout={
                        "name":"cose",
                        "initialTemp":2000,
                        "coolingFactor":0.8,
                        "minTemp":1,
                        "refresh":30,
                        "nodeRepulsion":2e5,
                        "nodeOverlap":50,
                        "numIter":2500
                        # "nodeRepulsion":1e4,
                        # "numIter":2500,
                        # "tile":False,
                        # "quality":"draft",
                        # "gravity":100,
                        # "animate":False,

                        # "idealEdgeLength":100,
                        # "gravity":0.2,
                        # "gravityRange":0.05
                    },
                    style={"width":"100%","height":"80vh"},
                    elements=nodes+edges,
                    boxSelectionEnabled=True,
                    minZoom=5E-2,
                    maxZoom=10,
                    responsive=True,
                    className="card border-secondary mb-3"), type="circle", color="grey"),
            ], fluid=True, id=prefix+"_graph_container")


def graph_properties(prefix):
    return dbc.Container([
                dbc.Col([
                    html.H3("Graph Properties"),
                    dbc.Row([
                        # dbc.Col(width=1), # just to move everything to the right (justify doesn't work)
                        dbc.Col([
                            dbc.Checklist(options=[{"label":"Selected","value":True}],id=prefix+"_only_selected_properties", labelStyle={"white-space":"nowrap"}, switch=True),
                            dbc.Tooltip(["Show only those nodes that are manually selected in the Graph",html.Br(),"(If there are...)"], target=prefix+"_only_selected_properties", placement="top", hide_arrow=True, delay={"show":500, "hide":250})
                        ], align="center", xs=2, lg=1),
                        dbc.Col([
                            dcc.Dropdown(id=prefix+"_search_properties", placeholder="Search Specific Nodes ...", multi=True, className="DropdownMenu")
                        ], align="center", xs=10, lg=4),
                        dbc.Col(html.Font("Sort by: ", style={"white-space":"nowrap"}),align="center", style={"text-align":"right"}, xs=2, lg=1),
                        dbc.Col([
                            dcc.Dropdown(id=prefix+"_properties_table_sorting",  options=[
                                {"label":"Degree: Low to High","value":"Degree,1"},
                                {"label":"Degree: High to Low","value":"Degree,0"},
                                {"label":"Closeness Centrality: Low to High","value":"Closeness Centrality,1"},
                                {"label":"Closeness Centrality: High to Low","value":"Closeness Centrality,0"},
                                {"label":"Betweenness Centrality: Low to High","value":"Betweenness Centrality,1"},
                                {"label":"Betweenness Centrality: High to Low","value":"Betweenness Centrality,0"},
                                {"label":"Eigenvector Centrality: Low to High","value":"Eigenvector Centrality,1"},
                                {"label":"Eigenvector Centrality: High to Low","value":"Eigenvector Centrality,0"},
                                {"label":"Clustering Coefficient: Low to High","value":"Clustering Coefficient,1"},
                                {"label":"Clustering Coefficient: High to Low","value":"Clustering Coefficient,0"},
                                {"label":"VoteRank Score: Low to High","value":"VoteRank Score,1"},
                                {"label":"VoteRank Score: High to Low","value":"VoteRank Score,0"},
                            ], value="Degree,0", clearable=False, searchable=False, optionHeight=25,className="DropdownMenu")
                        ], align="center", xs=10, lg=3),
                        dbc.Col(html.Font("Rows to show: ", style={"white-space":"nowrap"}),align="center", style={"text-align":"right"}, xs=2, lg=1),
                        dbc.Col([
                            dcc.Dropdown(id=prefix+"_properties_table_rows",options=[
                                {"label":"10","value":10},
                                {"label":"25","value":25},
                                {"label":"50","value":50},
                                {"label":"100","value":100},
                                {"label":"all","value":"all"}
                            ], value=10, className="DropdownMenu", clearable=False, searchable=False, optionHeight=25)
                        ], align="center", xs=10, lg=1),
                        dbc.Col(html.A(dbc.Button("Download", className="btn btn-outline-primary"), target="_blank", download="graph_properties.tsv", id=prefix+"_download_graph_properties"), align="center")
                    ], justify="around", align="center"),
                    html.Br(),
                    dcc.Loading(dbc.Container(id=prefix+"_graph_properties_table_container", fluid=True), type="dot", color="grey")
                ])
            ], fluid=True, style={"padding":"3%"})

def view_custom_clusters(prefix):
    return html.Center([
                html.Br(),
                dbc.Button("View Table", id=prefix+"_view_clusters_open", className="btn btn-outline-primary"),
                dbc.Modal([
                    dbc.ModalHeader("Custom Groups"),
                    dbc.ModalBody([
                        dbc.Container(id=prefix+"_custom_clusters_table_container", fluid=True)
                    ]),
                    dbc.ModalFooter([
                        html.A(dbc.Button("Download", className="btn btn-outline-primary"), target="_blank", download="custom_groups.tsv", id=prefix+"_download_custom_clusters_modal"),
                        dbc.Button("Close", id=prefix+"_view_clusters_close", className="btn btn-outline-primary")
                    ]),
                ],id=prefix+"_custom_clusters_modal", size="xl"),
            ])

def custom_clustering(prefix):
    return dbc.Container([
                html.H3("Clustering"),
                dbc.Row([
                    dbc.Col([dbc.Spinner(dcc.Graph(id=prefix+"_custom_clustering_graph", responsive=True))], style={"padding":"0px"}, xs=12, md=6, id=prefix+"_custom_clustering_graph_col"), # I don't know why the dcc.Loading component moves the graph outside the column (covering the lower one)
                    dbc.Col([
                        dbc.Row([
                            dbc.Col(width=4),
                            dbc.Col(dcc.Dropdown(id=prefix+"_custom_clustering_component", options=[
                                {"label":"Entire Graph","value":"entire"},
                                {"label":"Major Component","value":"maj"}
                            ], value="entire", clearable=False, searchable=False, optionHeight=25,className="DropdownMenu"), width=8),
                        ]),
                        dbc.Row([
                            dbc.Col(html.Font("Method:"), width=4),
                            dbc.Col(dcc.Dropdown(id=prefix+"_custom_clustering_method", options=[
                                {"label":"Spectral Clustering","value":"spectral"},
                                {"label":"Girvan Newman","value":"girvan_newman"},
                                {"label":"Greedy Modularity","value":"greedy_modularity"}
                            ], value="spectral", clearable=False, searchable=False, optionHeight=25,className="DropdownMenu"), width=8),
                        ], justify="around", align="center"),
                        dbc.Row([
                            dbc.Col(html.Font("Number of clusters:"), width=4),
                            dbc.Col(dcc.Dropdown(id=prefix+"_custom_clustering_number_clusters", clearable=False, optionHeight=25,className="DropdownMenu"), width=8),
                        ], justify="around", align="center"),
                        view_custom_clusters(prefix)
                    ], align="center", style={"padding":"1%"}, xs=12, md=4)
                ], justify="around", align="center", no_gutters=True)
            ], id=prefix+"_clustering", fluid=True, style={"padding":"3%"})

def common_data_generator(prefix,graph,graph_title):
    print(graph_title)
    graph_properties_df=pd.DataFrame({node:{prop:values[prop] for prop in ["Name","Degree", "Closeness Centrality", "Betweenness Centrality", "Eigenvector Centrality", "Clustering Coefficient", "VoteRank Score"]} for node,values in dict(graph.nodes(data=True)).items()}).T
    maj=graph.subgraph(max(list(nx.connected_components(graph)), key=len))
    print("\tCommunities Detection Data Precomputing ...")
    if os.path.isfile("data/groups/"+prefix+"_communities.pickle"):
        with open("data/groups/"+prefix+"_communities.pickle","rb") as bkp:
            girvan_newman,girvan_newman_maj,communities_modularity,communities_modularity_maj,n_comm,n_comm_maj=pickle.load(bkp)
    else:
        girvan_newman={len(comm):comm for comm in tqdm(nx.algorithms.community.girvan_newman(graph))}
        girvan_newman_maj={len(comm):comm for comm in tqdm(nx.algorithms.community.girvan_newman(maj))}
        communities_modularity={modularity(graph,community):n for n,community in girvan_newman.items()}
        n_comm=communities_modularity[max(communities_modularity)]
        communities_modularity_maj={modularity(maj,community):n for n,community in girvan_newman_maj.items()}
        n_comm_maj=communities_modularity_maj[max(communities_modularity_maj)]
        name="data/groups/"+prefix+"_communities.pickle"
        with open(name,"wb") as bkp:
            pickle.dump([girvan_newman,girvan_newman_maj,communities_modularity,communities_modularity_maj,n_comm,n_comm_maj],bkp)
        if os.path.isfile(name+".bkp"):
            os.remove(name+".bkp")
    print("\tSpectral Clustering Data Precomputing ...")
    if os.path.isfile("data/groups/"+prefix+"_spectral.pickle"):
        with open("data/groups/"+prefix+"_spectral.pickle","rb") as bkp:
            L,evals,evects,n_clusters,L_maj,evals_maj,evects_maj,n_clusters_maj=pickle.load(bkp)
    else:
        L=nx.normalized_laplacian_matrix(graph).toarray()
        evals,evects=np.linalg.eigh(L)
        # n_clusters=[n for n,dif in enumerate(np.diff(evals)) if dif > 2*np.average([d for d in np.diff(evals) if d>0.00001])][0]+1
        # clusters_list=[n for n,dif in enumerate(np.diff(evals)) if dif in sorted(np.diff(evals),reverse=True)[:len(evals)//20]]
        # n_clusters=clusters_list[0]+1 if clusters_list[0] != 0 else clusters_list[1]+1
        relevant=[n for n,dif in enumerate(np.diff(evals)) if dif > halfnorm.ppf(0.99,*halfnorm.fit(np.diff(evals)))]
        relevant=[relevant[n] for n in range(len(relevant)-1) if relevant[n]+1 != relevant[n+1]]+[relevant[-1]] #keeps only the highest value if there are consecutive ones
        n_clusters=relevant[0]+1 if (relevant[0] > 1 and relevant[0]+1 != nx.number_connected_components(graph)) else relevant[1]+1
        L_maj=nx.normalized_laplacian_matrix(maj).toarray()
        evals_maj,evects_maj=np.linalg.eigh(L_maj)
        # n_clusters_maj=[n for n,dif in enumerate(np.diff(evals_maj)) if dif > 2*np.average([d for d in np.diff(evals_maj) if d>0.00001])][0]+1
        # n_clusters_maj=[n for n,dif in enumerate(np.diff(evals_maj)) if dif in sorted(np.diff(evals_maj),reverse=True)[:len(evals_maj)//20]][0]+1
        # clusters_list_maj=[n for n,dif in enumerate(np.diff(evals_maj)) if dif in sorted(np.diff(evals_maj),reverse=True)[:len(evals_maj)//20]]
        # n_clusters_maj=clusters_list_maj[0]+1 if clusters_list_maj[0] != 0 else clusters_list_maj[1]+1
        relevant_maj=[n for n,dif in enumerate(np.diff(evals_maj)) if dif > halfnorm.ppf(0.99,*halfnorm.fit(np.diff(evals_maj)))]
        relevant_maj=[relevant_maj[n] for n in range(len(relevant_maj)-1) if relevant_maj[n]+1 != relevant_maj[n+1]]+[relevant_maj[-1]] #keeps only the highest value if there are consecutive ones
        n_clusters_maj=relevant_maj[0]+1 if (relevant_maj[0] > 1 and relevant_maj[0]+1 != nx.number_connected_components(maj)) else relevant_maj[1]+1
        name="data/groups/"+prefix+"_spectral.pickle"
        with open(name,"wb") as bkp:
            pickle.dump([L,evals,evects,n_clusters,L_maj,evals_maj,evects_maj,n_clusters_maj],bkp)
        if os.path.isfile(name+".bkp"):
            os.remove(name+".bkp")
    return graph_properties_df,L,evals,evects,L_maj,evals_maj,evects_maj,n_clusters,n_clusters_maj,girvan_newman,maj,girvan_newman_maj,communities_modularity,communities_modularity_maj,n_comm,n_comm_maj

def get_frequency(l):
    l=list(l)
    d={}
    for el in set(l):
        d[el]=l.count(el)/len(l)
    # try:
    #   d[el]+=1
    # except:
    #   d[el]=1
    return d

def degree_distribution(graph, title):
    K=dict(nx.get_node_attributes(graph,"Degree"))
    n=len(graph.nodes())
    p=len(graph.edges())/(n*(n-1)/2)
    ER=nx.fast_gnp_random_graph(n,p)
    ERK=dict(nx.degree(ER))
    power_data=pd.DataFrame({"Node degree, k":list(get_frequency(K.values()).keys())+list(get_frequency(ERK.values()).keys()),"Frequency of Nodes with degree k, n(k)":list(get_frequency(K.values()).values())+list(get_frequency(ERK.values()).values()), "Graph":[title]*len(set(K.values()))+["Erdősh Rényi Equivalent Graph"]*len(set(ERK.values()))})
    plot=px.scatter(data_frame=power_data,x="Node degree, k",y="Frequency of Nodes with degree k, n(k)", title="Node Degree Distribution", log_x=True, log_y=True, template="ggplot2", color="Graph", trendline="lowess")
    plot.update_layout({"paper_bgcolor": "rgba(0, 0, 0, 0)", "modebar":{"bgcolor":"rgba(0, 0, 0, 0)","color":"silver","activecolor":"grey"}}) # for a transparent background but keeping modebar acceptable colors
    return plot

def plots(prefix, graph,title):
    return dbc.Container([
                html.H3("Plots"),
                dbc.Row([
                    dbc.Col([dbc.Spinner(dcc.Graph(figure=degree_distribution(graph,title), id=prefix+"_degree_distribution", responsive=True))], style={"padding":"0px"}, xs=12, lg=5),
                    dbc.Col([dbc.Spinner(dbc.Container(dcc.Graph(id=prefix+"_piechart", responsive=True)))], style={"padding":"0px"}, xs=12, lg=7)
                ], justify="around", align="center", no_gutters=True)
            ], id=prefix+"_plots", fluid=True, style={"padding":"3%"})

def footer():
    return dbc.Container([
                html.P([
                    html.A(html.Small("Write us"), href="mailto:luca.menestrina2@unibo.it"),html.Small(" if you have questions and suggestions"),
                    html.Br(),
                    html.Small("App developed by Luca Menestrina, Department of Pharmacy and Biotechnology, University of Bologna, Italy")
                ], style={"margin":"0px"})
                # dbc.Row(html.Small("Copyright \u00A9 2020 Luca Menestrina All rights reserved")) # controllo le licenze di github
            ], fluid=True, className="bg-light", style={"box-shadow":"0 0 0.4rem #CDCDCD", "z-index":"1000", "padding":"0.5%", "padding-left":"1%", "position":"absolute","bottom":"0"})
