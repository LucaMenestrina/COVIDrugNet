import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_daq as daq

import networkx as nx

from building_blocks import *
from callbacks import *


graph_title="Target Projection"
prefix=graph_title.lower().replace(" ","_")#"target_projection"
print("Loading "+graph_title+" ...")

G=nx.read_gpickle("data/graphs/target_projection/target_projection.gpickle")
nx.set_node_attributes(G,nx.get_node_attributes(G,"nameID"),"id")

try:
    from networkx.drawing.nx_agraph import graphviz_layout
    pos=nx.rescale_layout_dict(graphviz_layout(G),len(G.nodes())*2.5)
except:
    pos=nx.spring_layout(G,k=1/(np.sqrt(len(G.nodes())/15)), scale=1000, seed=1)

nodes=[{"data":{key:value for key,value in attributes.items()}, "position":{"x":pos[node][0],"y":pos[node][1]}} for node,attributes in dict(G.nodes(data=True)).items()]
edges=[{"data":{"source":source,"target":target}} for source,target in G.edges]
print("\tComputing edges to show ...")
dt=nx.read_gpickle("data/graphs/drug_target/drug_target.gpickle")
neighbors=set(dt.neighbors("Fostamatinib (DB12010)")).difference(set(dt.neighbors("Artenimol (DB11638)")))
edges_to_show=[edge for edge in edges if not (edge["data"]["source"] in neighbors and edge["data"]["target"] in neighbors)]


layout=dbc.Col([
            dbc.Modal([
                dbc.ModalHeader("Show Edges"),
                dbc.ModalBody([
                    html.Center([
                        # html.P("The Target Projection has %d edges and displaying all of them would severely slow down the page loading and responsiveness"%len(G.edges), style={"font-size":"110%"}),
                        html.Br(),
                        html.P("In order to improve the user experience, we decided to hide some of the edges connecting the neighbors of Fostamatinib and Artenimol (%d),"%(len(edges)-len(edges_to_show)), style={"font-size":"110%"}),
                        html.Br(),
                        # html.P("most of them would be hidden behind the two jumbles induced by these two drugs anyway", style={"font-size":"110%"}),
                        html.P("! This will only affect the visualization, analyses will not be influenced !", style={"font-size":"133%"}),
                        html.Br(),
                        html.Br(),#H
                        html.P("It is possible to override this choice here:", style={"font-size":"110%"}),
                        daq.BooleanSwitch(on=False, label="Show All Edges", id=prefix+"_show_all_edges_modal"),
                        html.Br(),
                        html.P([
                            "This selection can be changed at any time from the ",
                            html.I(className="fa fa-question-circle"),
                            " button at the top-left of the graph"
                        ], style={"font-size":"110%"}),
                        html.Br(),
                        html.Br(),#H
                        html.P("Please wait a few seconds while the page loads..."),
                        dcc.Interval(id=prefix+"_progress_interval",n_intervals=0, interval=500, max_intervals=3),
                        dbc.Progress(id=prefix+"_loading_progress"),
                        html.Br(),
                    ])
                ]),
                dbc.ModalFooter([
                    dbc.Button("OK", id=prefix+"_show_edges_close", className="btn btn-outline-primary", style={"visibility":"hidden"})
                ]),
            ], is_open=True, id=prefix+"_show_edges_modal",size="xl", style={"margin":"10rem auto"}),
            dbc.Row([
                dbc.Col(sidebar(prefix), width=1, className="bg-light"),
                dbc.Col([
                    html.Br(),
                    dbc.Row([
                        dbc.Col(graph(prefix, title=graph_title, nodes=nodes, edges=edges_to_show), xs=12, md=9),
                        dbc.Col(nodes_info(prefix), md=3)
                    ], no_gutters=True, justify="center"),
                    html.Br(),
                    inspected_data(prefix),
                    html.Br(),
                    plots(prefix,graph=G, title=graph_title),
                    html.Br(),
                    graph_properties(prefix),
                    html.Br(),
                    advanced_section(prefix, G, graph_title)
                    ])
                ], no_gutters=True),
                html.Div(style={"height":"10vh"}),
                footer(),
            ], style={"padding":"0px"})




##  ----------  CALLBACKS   ------------

@app.callback(
    [
        Output(prefix+"_loading_progress", "value"),
        Output(prefix+"_show_edges_close", "style"),
    ],
    [Input(prefix+"_progress_interval", "n_intervals")],
)
def update_progress(n):
    progress = (n/3)*100
    if progress == 100:
        visibility=None
    else:
        visibility={"visibility":"hidden"}
    return progress, visibility

build_callbacks(prefix,G,nodes,edges,edges_to_show,*common_data_generator(prefix,G))
