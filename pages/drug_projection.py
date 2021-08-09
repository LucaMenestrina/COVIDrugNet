import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

import networkx as nx

from building_blocks import *
from callbacks import *


graph_title="Drug Projection"
prefix=graph_title.lower().replace(" ","_")#"drug_projection"
print("Loading "+graph_title+" ...")

G=nx.read_gpickle("data/graphs/drug_projection/drug_projection.gpickle")
nx.set_node_attributes(G,nx.get_node_attributes(G,"Name"),"id")


try:
    from networkx.drawing.nx_agraph import graphviz_layout
    pos=nx.rescale_layout_dict(graphviz_layout(G),1000)
except:
    pos=nx.spring_layout(G,k=1/(np.sqrt(len(G.nodes())/15)), scale=1000, seed=1)

nodes=[{"data":{key:value for key,value in attributes.items()}, "position":{"x":pos[node][0],"y":pos[node][1]}} for node,attributes in dict(G.nodes(data=True)).items()]
edges=[{"data":{"source":source,"target":target}} for source,target in G.edges]
edges_to_show=edges.copy()

layout=dbc.Col([
            dbc.Row([
                dbc.Col(sidebar(prefix), width=1, className="bg-light"),
                dbc.Col([
                    html.Br(),
                    dbc.Row([
                        dbc.Col(graph(prefix, title=graph_title, nodes=nodes, edges=edges), xs=12, md=9),
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

build_callbacks(prefix,G,nodes,edges,edges_to_show,*common_data_generator(prefix,G))
