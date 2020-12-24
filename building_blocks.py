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
                    html.P(["If it takes too long (or it doesn't load at all) please let us know"]),
                    # html.Br(),
                    # html.Small("A small banner could also appear on top of your window saying that a calculation is slowing down your browser")
                ], style={"width":"40vw"}
            ), is_in=True, timeout=250)]
        ),id="page_content")

def common_data_generator(prefix,graph):
    if prefix == "dd":
        with open("data/atc_description.pickle", "rb") as bkp:
            atc_description=pickle.load(bkp)
    else:
        atc_description=[]
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
            L,evals,evects,n_clusters,clusters,L_maj,evals_maj,evects_maj,n_clusters_maj,clusters_maj=pickle.load(bkp)
    else:
        L=nx.normalized_laplacian_matrix(graph).toarray()
        evals,evects=np.linalg.eigh(L)
        relevant=[n for n,dif in enumerate(np.diff(evals)) if dif > halfnorm.ppf(0.99,*halfnorm.fit(np.diff(evals)))]
        relevant=[relevant[n] for n in range(len(relevant)-1) if relevant[n]+1 != relevant[n+1]]+[relevant[-1]] #keeps only the highest value if there are consecutive ones
        n_clusters=relevant[0]+1 if (relevant[0] > 1 and relevant[0]+1 != nx.number_connected_components(graph)) else relevant[1]+1
        km=KMeans(n_clusters=n_clusters, n_init=100)
        clusters=km.fit_predict(evects[:,:n_clusters])
        L_maj=nx.normalized_laplacian_matrix(maj).toarray()
        evals_maj,evects_maj=np.linalg.eigh(L_maj)
        relevant_maj=[n for n,dif in enumerate(np.diff(evals_maj)) if dif > halfnorm.ppf(0.99,*halfnorm.fit(np.diff(evals_maj)))]
        relevant_maj=[relevant_maj[n] for n in range(len(relevant_maj)-1) if relevant_maj[n]+1 != relevant_maj[n+1]]+[relevant_maj[-1]] #keeps only the highest value if there are consecutive ones
        n_clusters_maj=relevant_maj[0]+1 if (relevant_maj[0] > 1 and relevant_maj[0]+1 != nx.number_connected_components(maj)) else relevant_maj[1]+1
        km_maj=KMeans(n_clusters=n_clusters_maj, n_init=100)
        clusters_maj=km_maj.fit_predict(evects_maj[:,:n_clusters_maj])
        name="data/groups/"+prefix+"_spectral.pickle"
        with open(name,"wb") as bkp:
            pickle.dump([L,evals,evects,n_clusters,clusters,L_maj,evals_maj,evects_maj,n_clusters_maj,clusters_maj],bkp)
        if os.path.isfile(name+".bkp"):
            os.remove(name+".bkp")
    return graph_properties_df,L,evals,evects,n_clusters,clusters,L_maj,evals_maj,evects_maj,n_clusters_maj,clusters_maj,girvan_newman,maj,girvan_newman_maj,communities_modularity,communities_modularity_maj,n_comm,n_comm_maj, atc_description

def headbar():
    return dbc.Navbar(
                dbc.Container([
                    html.A(
                        dbc.Row([
                            html.Img(src=app.get_asset_url("imgs/logo_white.svg"), style={"height":"4vh", "margin-right":"1rem"}),
                            dbc.NavbarBrand("COVID-19 Drugs Networker")
                        ], no_gutters=True, justify="start", align="center"),
                    href="/covid19drugsnetworker", className="card-link"),
                    dbc.NavbarToggler(id="headbar_toggler"),
                    dbc.Collapse([
                        dbc.Nav([
                            dbc.NavItem(dbc.NavLink([html.I(className="fa fa-home", style={"margin-right":"0.4rem"}),"Home"],href="/covid19drugsnetworker/home", active=True, className="nav-link active", external_link=True), className="nav-item", id="home_nav"),
                            dbc.Tooltip("COVID-19 Drugs Networker Homepage", target="home_nav", placement="bottom", hide_arrow=True, delay={"show":500, "hide":250}),
                            dbc.NavItem(dbc.NavLink([html.I(className="fa fa-question", style={"margin-right":"0.4rem"}),"Help"],href="/covid19drugsnetworker/help", active=True, className="nav-link active", external_link=True), className="nav-item", id="help_nav"),
                            dbc.Tooltip("Page Structure and Main Possible Interactions", target="help_nav", placement="bottom", hide_arrow=True, delay={"show":500, "hide":250}),
                            dbc.NavItem(dbc.NavLink([html.I(className="fa fa-info", style={"margin-right":"0.4rem"}),"About"],href="/covid19drugsnetworker/about", active=True, className="nav-link active", external_link=True), className="nav-item", id="about_nav"),
                            dbc.Tooltip("Info About the Project", target="about_nav", placement="bottom", hide_arrow=True, delay={"show":500, "hide":250}),
                            dbc.NavItem(dbc.NavLink([html.I(className="fa fa-address-book", style={"margin-right":"0.4rem"}),"Contacts"],href="/covid19drugsnetworker/contacts", active=True, className="nav-link active", external_link=True), className="nav-item", id="contacts_nav"),
                            dbc.Tooltip("Project Participant's Contacts", target="contacts_nav", placement="bottom", hide_arrow=True, delay={"show":500, "hide":250}),
                            dbc.Nav([
                                dbc.NavLink(html.I(className="fa fa-project-diagram"), active=True, className="nav-link active", style={"margin-right":"-0.6rem"}), # patch for graphs label icon
                                dbc.DropdownMenu([
                                    dbc.DropdownMenuItem("Drug-Target Network", href="/covid19drugsnetworker/drug_target", className="dropdown-item", external_link=True),
                                    dbc.DropdownMenuItem("Drug Projection", href="/covid19drugsnetworker/drug_drug", className="dropdown-item", external_link=True),
                                    dbc.DropdownMenuItem("Target Projection", href="/covid19drugsnetworker/target_target", className="dropdown-item", external_link=True),
                                    # dbc.DropdownMenuItem("Target Disease", href="/target_disease", className="dropdown-item"), # not yet available
                                    # dbc.DropdownMenuItem("Target Interactors", href="/target_interactors", className="dropdown-item") # not yet available
                                ], nav=True, in_navbar=True, right=True, label="Graphs ...", className="nav-item dropdown active"),
                            ], className="nav-item", id="other_graphs_nav"),
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
                        dbc.NavItem(dbc.NavLink("Inspected Data", href="#"+prefix+"_inspected_table", external_link=True, id=prefix+"_side_inspected_table", active=False, disabled=True, className="nav-link"), className="nav-item", id=prefix+"_inspected_data_side"),
                        dbc.Tooltip("Jump to Inspected Data' Section", target=prefix+"_inspected_data_side", placement="right", hide_arrow=True, delay={"show":500, "hide":250}, id=prefix+"_inspected_data_side_tooltip"),
                        dbc.NavItem(dbc.NavLink("Plots", href="#"+prefix+"_plots",external_link=True, active=True, className="nav-link"), className="nav-item", id=prefix+"_plots_side"),
                        dbc.Tooltip("Jump to Plots' Section", target=prefix+"_plots_side", placement="right", hide_arrow=True, delay={"show":500, "hide":250}),
                        dbc.NavItem(dbc.NavLink("Graph Properties", href="#"+prefix+"_graph_properties_table", external_link=True, active=True, className="nav-link"), className="nav-item", id=prefix+"_graph_properties_side"),
                        dbc.Tooltip("Jump to Graph Properties' Section", target=prefix+"_graph_properties_side", placement="right", hide_arrow=True, delay={"show":500, "hide":250}),
                        dbc.NavItem(dbc.NavLink("Clustering", href="#"+prefix+"_clustering",external_link=True, active=True, className="nav-link"), className="nav-item", id=prefix+"_clustering_side"),
                        dbc.Tooltip("Jump to Clustering' Section", target=prefix+"_clustering_side", placement="right", hide_arrow=True, delay={"show":500, "hide":250}),
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
            dbc.Button(html.I(className="fa fa-question-circle", style={"font-size":"0.9rem"}), id=prefix+"_help_open", block=True, className="btn btn-outline-primary"),#"Help"
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
                style={"position":"absolute","top":"-4vh","left":"-5vw", "width":"200%","z-index":"1000"},
                is_open=False
            ),
            dbc.Tooltip(["Graph's Legend",html.Br(),"(when available)"], target=prefix+"_legend_open", placement="top", hide_arrow=True, delay={"show":500, "hide":250})
        ])

def save_graph(prefix):
    return html.Div([
            dbc.Button(html.I(className="fa fa-file-download", style={"font-size":"0.9rem"}), id=prefix+"_save_graph_open", block=True, className="btn btn-outline-primary"),#"Save"
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
            dcc.Dropdown(id=prefix+"_highlighter_dropdown",options=[{"label":data["Name"],"value":data["ID"]} for data in [node["data"] for node in nodes]], placeholder="Highlight a node", multi=True, className="DropdownMenu"),#, style={"max-height":"15vh","overflow-y":"auto"} right now it is not possible to limit the overflow, otherwise it hides the selectable options
            dbc.Tooltip("Highlight Specific Nodes for Easier Spotting", target=prefix+"_highlighter_dropdown_div", placement="top", hide_arrow=True, delay={"show":500, "hide":250}),
            html.Div(id=prefix+"_highlighted_data_cache", style={"display":"none"}) #for temporary store highlighted nodes data
        ],id=prefix+"_highlighter_dropdown_div")

def group_highlighting(prefix, nodes):
    def conjunction(id):
        return dcc.Dropdown(id=id,options=[{"label":"AND","value":"AND"},{"label":"OR","value":"OR"}], value="OR", multi=False, searchable=False,clearable=False, className="DropdownMenu")
    modal_body=[
        dbc.Row([
            dbc.Col([
                html.Strong(html.P("Property", style={"text-align":"center"}, id=prefix+"_group_property")),
                dbc.Tooltip("Available Nodes' Properties for Highlighting", target=prefix+"_group_property", placement="top", hide_arrow=True, delay={"show":500, "hide":250})
            ], width=2, align="center"),
            dbc.Col([
                html.Strong(html.P("Filter", style={"text-align":"center"}, id=prefix+"_group_filter")),
                dbc.Tooltip("Chosen Filter for the Properties", target=prefix+"_group_filter", placement="top", hide_arrow=True, delay={"show":500, "hide":250})
            ], width=7, align="center"),
            dbc.Col([
                html.Strong(html.P("Logical Conjunction", style={"text-align":"center"}, id=prefix+"_group_conjunction")),
                dbc.Tooltip("Logical Operation for Joining Filters", target=prefix+"_group_conjunction", placement="top", hide_arrow=True, delay={"show":500, "hide":250})
            ], width=2, align="center")
        ], justify="around", align="center")
    ]
    if prefix == "dt":
        return html.Div([
                dbc.Button("Highlight by Property", id=prefix+"_group_highlighter_open", block=True, className="btn btn-outline-primary", disabled=True),
                ])
    elif prefix == "dd":
        properties=["ATC Code Level 1", "ATC Code Level 2", "ATC Code Level 3", "ATC Code Level 4", "Targets", "Enzymes", "Carriers", "Transporters", "Drug Interactions"]

    elif prefix == "tt":
        properties=["STRING Interaction Partners", "Drugs", "Diseases"]
        for property in ["Organism", "Protein Class", "Protein Family", "Cellular Location"]:
            all_prop=sorted(set([node["data"][property] for node in nodes]))
            options=[{"label":prop,"value":",".join([node["data"]["ID"] for node in nodes if prop == node["data"][property]])} for prop in all_prop]
            modal_body.append(
                dbc.Row([
                    dbc.Col([html.Font(property, style={"text-align":"center"})], width=2, align="center"),
                    dbc.Col([dcc.Dropdown(options=options, multi=True, className="DropdownMenu", id=prefix+"_highlight_dropdown_"+property)], width=7, align="center"),
                    dbc.Col([conjunction(prefix+"_conjunction_"+property)], width=2, align="center")
                ], justify="around", align="center")
            )
    for property in properties:
        all_prop=sorted(set([prop for node in nodes for prop in node["data"][property]]))
        options=[{"label":prop,"value":",".join([node["data"]["ID"] for node in nodes if prop in node["data"][property]])} for prop in all_prop]
        modal_body.append(
            dbc.Row([
                dbc.Col([html.Font(property, style={"text-align":"center"})], width=2, align="center"),
                dbc.Col([dcc.Dropdown(options=options, multi=True, className="DropdownMenu", id=prefix+"_highlight_dropdown_"+property)], width=7, align="center"),
                dbc.Col([conjunction(prefix+"_conjunction_"+property)], width=2, align="center")
            ], justify="around", align="center")
        )
    modal_body+=[
        html.Br(),
        dbc.Row([
            dbc.Col([html.Font("General Logical Conjunction", style={"text-align":"center"})], width=4, align="center"),
            dbc.Col([conjunction(prefix+"_conjunction_general")], width=2, align="center")
        ], justify="center", align="center"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Checklist(options=[{"label":"Only Major Component","value":True}],id=prefix+"_only_major_highlighted_groups", labelStyle={"white-space":"nowrap"}, switch=True)
            ], width=4, align="center")
        ], justify="center", align="center"),
        html.Br(),
        html.Br(),
        dbc.Row([
            dbc.Col(html.P("Highlighted nodes: ", style={"text-align":"right"}), align="center"),
            dbc.Col(html.P(id=prefix+"_n_highlighted",style={"text-align":"left"}), align="center")
        ], justify="center", align="center")
    ]
    return html.Div([
            dbc.Button("Highlight by Property", id=prefix+"_group_highlighter_open", block=True, className="btn btn-outline-primary"),
            dbc.Modal([
                dbc.ModalHeader("Custom Highlighting by Property"),
                dbc.ModalBody(modal_body),
                dbc.ModalFooter([
                    html.A(dbc.Button("Download", id=prefix+"_download_group_highlighting_button", className="btn btn-outline-primary"),download="highlighted_nodes.tsv",id=prefix+"_download_group_highlighting_button_href", target="_blank"),
                    dbc.Button("Clear", id=prefix+"_group_highlighter_clear", className="btn btn-outline-primary"),
                    dbc.Button("OK", id=prefix+"_group_highlighter_close", className="btn btn-outline-primary")
                ]),
            ],size="lg", id=prefix+"_group_highlighting_modal"),
            dbc.Tooltip("Highlight Nodes with Specific Properties", target=prefix+"_group_highlighter_open", placement="top", hide_arrow=True, delay={"show":500, "hide":250}),
            html.Div(id=prefix+"_highlighted_cache", style={"display":"none"}) #for temporary store highlighted nodes
        ])


def graph(prefix,title,nodes,edges):
    return dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H4(title,id=prefix+"_name_graph", style={"margin-bottom":"0"})
                    ]),
                    dbc.Col([
                        html.H5("%d nodes"%len(nodes), style={"margin-bottom":"0", "text-align":"right"})
                    ])
                ],no_gutters=True, justify="between", align="center", className="card-header"),
                dbc.Row([
                    dbc.Col(graph_help(prefix)),#, width=1
                    dbc.Col(legend(prefix), width=1),
                    dbc.Col(save_graph(prefix)),#, width=1
                    dbc.Col(coloring_dropdown(prefix), width=4),
                    dbc.Col(highlighting(prefix, nodes), width=4),
                    dbc.Col(group_highlighting(prefix, nodes), width=2)
                ], no_gutters=True, className="card-title", justify="around", align="center"),
                dcc.Loading(cyto.Cytoscape(
                    id=prefix+"_graph",
                    layout={
                        "name":"preset"
                        # "name":"cose",
                        # "initialTemp":2000,
                        # "coolingFactor":0.8,
                        # "minTemp":1,
                        # "refresh":30,
                        # "nodeRepulsion":2e5,
                        # "nodeOverlap":50,
                        # "numIter":2500
                    },
                    style={"width":"100%","height":"80vh"},
                    elements=nodes+edges,
                    boxSelectionEnabled=True,
                    minZoom=7.5E-2,
                    maxZoom=10,
                    responsive=True,
                    className="card border-secondary mb-3"), type="circle", color="grey"),
            ], fluid=True, id=prefix+"_graph_container")

def inspected_data(prefix):
    return dbc.Collapse([
        dbc.Container([
            dbc.Row([
                dbc.Col(html.H3("Inspected Data"), xs=12, md=3),
                dbc.Col(dcc.Dropdown(options=[
                    {"label":"Only Selected", "value":"selected"},
                    {"label":"Only Highlighted", "value":"highlighted"},
                    {"label":"Selected OR Highlighted ", "value":"selected_or_highlighted"},
                    {"label":"Selected AND Highlighted ", "value":"selected_and_highlighted"}
                ], id=prefix+"_inspected_dropdown", value="selected_or_highlighted", multi=False, searchable=False, clearable=False, className="DropdownMenu"), xs=12, md=3),
                dbc.Col(html.H5("XYZ Nodes", style={"text-align":"right"}, id=prefix+"_n_inspected_nodes"), xs=12, md=2)
            ], justify="start", align="center"),
            html.Br(),
            dbc.Row(dbc.Col(id=prefix+"_inspected_table", align="center"), no_gutters=True, justify="center", align="center"),
        ] , fluid=True, style={"padding":"3%"}),
        html.Div(id=prefix+"_inspected_cache", style={"display":"none"}) #for temporary store inspected data
    ],id=prefix+"_inspected_data")

def get_frequency(l):
    l=list(l)
    d={}
    for el in set(l):
        d[el]=l.count(el)/len(l)
    return d

def degree_distribution(graph, title):
    K=dict(nx.get_node_attributes(graph,"Degree"))
    n=len(graph.nodes())
    p=len(graph.edges())/(n*(n-1)/2)
    ER=nx.fast_gnp_random_graph(n,p)
    ERK=dict(nx.degree(ER))
    plot=go.Figure(layout={"title":{"text":"Node Degree Distribution","x":0.5, "xanchor": "center"},"xaxis":{"title_text":"Node degree, k", "type":"log"}, "yaxis":{"title_text":"Frequency of Nodes with degree k, n(k)", "type":"log"}, "template":"ggplot2"})
    yrange=[np.inf,-np.inf]
    for deg,name,order,color,trendline_order in [(K,title,1,"Tomato","Linear"),(ERK,"Erdős Rényi",2,"DeepSkyBlue","Quadratic")]:# Equivalent Graph
        x=list(get_frequency(deg.values()).keys())
        y=list(get_frequency(deg.values()).values())
        if x[0]==0: # to avoid problems with log10, they wouldn't be display anyway because of the loglog
            x=x[1:]
            y=y[1:]
        #in order to avoid that the trendline stretches too much yaxis
        if np.log10(min(y))<yrange[0]:
            yrange[0]=np.log10(min(y)*0.75)
        if np.log10(max(y))>yrange[1]:
            yrange[1]=np.log10(max(y)*2)
        plot.add_trace(go.Scatter(x=x,y=y, mode="markers", name=name, marker_color=color))
        #trendline
        coeff = np.polyfit(np.log10(x), np.log10(y),order)
        poly = np.poly1d(coeff)
        yfit = lambda x: 10**(poly(np.log10(x)))
        plot.add_trace(go.Scatter(x=x,y=yfit(x), mode="lines", name=name+"'s "+trendline_order+" Trendline", line_color=color))
    plot.update_layout({"paper_bgcolor": "rgba(0, 0, 0, 0)", "modebar":{"bgcolor":"rgba(0, 0, 0, 0)","color":"silver","activecolor":"grey"}, "legend":{"orientation":"h","yanchor":"top","y":-0.25, "xanchor":"center","x":0.5}, "yaxis":{"range":yrange}}) # for a transparent background but keeping modebar acceptable colors, "x":1.25
    return plot

def plots(prefix, graph, title):
    # title=title.split(" ")[0]
    children=[dbc.Col([dbc.Spinner(dbc.Container(dcc.Graph(id=prefix+"_piechart", responsive=True)))], style={"padding":"0px"}, xs=12, lg=6)]
    if prefix != "dt":
        children+=[dbc.Col([dbc.Spinner(dcc.Graph(figure=degree_distribution(graph,title), id=prefix+"_degree_distribution", responsive=True))], style={"padding":"0px"}, xs=12, lg=6)]
    return dbc.Container([
                html.H3("Plots"),
                dbc.Row(
                children=children
                # [
                #     # dbc.Col([dbc.Spinner(dbc.Container(dcc.Graph(id=prefix+"_piechart", responsive=True)))], style={"padding":"0px"}, xs=12, lg=6),
                #     # dbc.Col([dbc.Spinner(dcc.Graph(figure=degree_distribution(graph,title), id=prefix+"_degree_distribution", responsive=True))], style={"padding":"0px"}, xs=12, lg=6)
                # ]
                , justify="around", align="center", no_gutters=True)
            ], id=prefix+"_plots", fluid=True, style={"padding":"3%"})

def graph_properties(prefix):
    if prefix == "dt":
        options=[
            {"label":"Degree: Low to High","value":"Degree,1"},
            {"label":"Degree: High to Low","value":"Degree,0"},
            {"label":"Closeness Centrality: Low to High","value":"Closeness Centrality,1"},
            {"label":"Closeness Centrality: High to Low","value":"Closeness Centrality,0"},
            {"label":"Betweenness Centrality: Low to High","value":"Betweenness Centrality,1"},
            {"label":"Betweenness Centrality: High to Low","value":"Betweenness Centrality,0"},
            {"label":"Eigenvector Centrality: Low to High","value":"Eigenvector Centrality,1"},
            {"label":"Eigenvector Centrality: High to Low","value":"Eigenvector Centrality,0"},
            {"label":"VoteRank Score: Low to High","value":"VoteRank Score,1"},
            {"label":"VoteRank Score: High to Low","value":"VoteRank Score,0"},
        ]
    else:
        options=[
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
        ]
    return dbc.Container([
                dbc.Col([
                    html.H3("Graph Properties"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Checklist(options=[{"label":"Inspected","value":True}],id=prefix+"_only_inspected_properties", labelStyle={"white-space":"nowrap"}, switch=True),
                            dbc.Tooltip(["Show only those nodes that are manually selected or highlighted in the Graph",html.Br(),"(If there are...)"], target=prefix+"_only_inspected_properties", placement="top", hide_arrow=True, delay={"show":500, "hide":250})
                        ], align="center", xs=2, lg=1),
                        dbc.Col([
                            dcc.Dropdown(id=prefix+"_search_properties", placeholder="Search Specific Nodes ...", multi=True, className="DropdownMenu")
                        ], align="center", xs=10, lg=4),
                        dbc.Col(html.Font("Sort by: ", style={"white-space":"nowrap"}),align="center", style={"text-align":"right"}, xs=2, lg=1),
                        dbc.Col([
                            dcc.Dropdown(id=prefix+"_properties_table_sorting",  options=options, value="Degree,0", clearable=False, searchable=False, optionHeight=25,className="DropdownMenu")
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
                ], justify="around", align="center", no_gutters=True),
                html.Div(id=prefix+"_clusters_cache", style={"display":"none"}) #for temporary store computed clusters
            ], id=prefix+"_clustering", fluid=True, style={"padding":"3%"})

def footer():
    return dbc.Container([
                html.P([
                    html.A(html.Small("Write us"), href="mailto:luca.menestrina2@unibo.it"),html.Small(" if you have any questions or suggestions"),
                    html.Br(),
                    html.Small("App developed by Luca Menestrina, Department of Pharmacy and Biotechnology, University of Bologna, Italy")
                ], style={"margin":"0px"})
            ], fluid=True, className="bg-light", style={"box-shadow":"0 0 0.4rem #CDCDCD", "z-index":"1000", "padding":"0.5%", "padding-left":"1%", "position":"absolute","bottom":"0"})
