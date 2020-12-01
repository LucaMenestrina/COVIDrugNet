import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

from building_blocks import *
from callbacks import *

# app=dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
# app.title="COVID-19 Networker"
prefix="tt"
graph_title="Target Projection"
file_prefix="target_target"
print("Loading "+graph_title+" ...")

G=nx.read_gpickle("data/graphs/target_target.gpickle")
nx.set_node_attributes(G,nx.get_node_attributes(G,"Name"),"id")

# pos=nx.kamada_kawai_layout(G, scale=1000)
# pos=nx.spring_layout(G,k=1/(np.sqrt(len(G.nodes())/15)), scale=1000, seed=1)
pos=nx.rescale_layout_dict(graphviz_layout(G),len(G.nodes())*2.5)
nodes=[{"data":{key:value for key,value in attributes.items()}, "position":{"x":pos[node][0],"y":pos[node][1]}} for node,attributes in dict(G.nodes(data=True)).items()]
edges=[{"data":{"source":source,"target":target}} for source,target in G.edges]

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
                    custom_clustering(prefix),
                    ])
                ], no_gutters=True),
                html.Div(style={"height":"10vh"}),
                footer(),
            ], style={"padding":"0px"})




##  ----------  CALLBACKS   ------------

build_callbacks(prefix,G,nodes,*common_data_generator(prefix,G),file_prefix)


# if __name__=="__main__":
#     app.run_server(debug=False)
