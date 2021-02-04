import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Output,Input, State
import plotly.express as px

from urllib.request import quote

import pandas as pd
import numpy as np

import networkx as nx

import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import KBinsDiscretizer

from app import app
import plotly.graph_objects as go
# cyto.load_extra_layouts()

stylesheet_base=[
    {
        "selector":"node",
        "style":{
            "background-color":"data(fill_color)",
            "border-color":"data(line_color)",
            "border-width":3
        }
    },
    {
        "selector":"node:selected",
        "style":{
            "background-color":"#FFE985",
            "border-color":"#FFDD4A",
            "border-width":3
        }
    }
]

def collapse_headbar_callback():
    @app.callback(
        Output("headbar_collapse", "is_open"),
        [Input("headbar_toggler", "n_clicks")],
        [State("headbar_collapse", "is_open")],
    )
    def collapse_headbar(n, is_open):
        if n:
            return not is_open
        return is_open


def displayHoverNodeData_callback(prefix,G):
    @app.callback(
        [
            Output(prefix+"_title_card","children"),
            Output(prefix+"_img_card","children"),
            Output(prefix+"_attributes-list-card","children"),
            Output(prefix+"_selected_node_warning","is_open")
        ],
        [
            Input(prefix+"_graph", "mouseoverNodeData"),
            Input(prefix+"_graph", "selectedNodeData")
        ],
        [
            State(prefix+"_selected_node_warning","is_open")
        ]
    )
    def displayHoverNodeData(data,selected_data,warning):
        img=None
        if not data:
            data={"id":"","Properties":"Hover over a node (or select it) to show its properties"}
            attributes=["id","Properties"]
            link_drugbank=""
        else:
            if selected_data and len(selected_data)==1:
                data=selected_data[0]
                if not warning:
                    warning = not warning
            if data["kind"]=="Drug":
                attributes=["ID","SMILES","ATC Code Level 1","ATC Identifier","Targets","Enzymes","Carriers","Transporters","Drug Interactions"]
                link_drugbank="https://www.drugbank.ca/drugs/"+data["ID"]
                if data["ID"] != "Not Available":
                    img=html.A(html.Img(src=data["structure"], height="auto", width="100%", alt="Structure Image not Available"), href="https://www.drugbank.ca/structures/small_molecule_drugs/"+data["ID"] ,target="_blank")
            else:
                attributes=["ID","Gene","PDBID","Organism","Protein Class","Protein Family","Cellular Location","STRING Interaction Partners","Drugs","Diseases"]
                link_drugbank=data["drugbank_url"]
                if data["PDBID"] != "Not Available":
                    img=[html.A(html.Img(src=data["structure"], height="auto", width="100%", alt="Structure Image not Available"), href="https://www.rcsb.org/3d-view/"+data["PDBID"], target="_blank"), html.A(html.Small("Structure Reference", style={"position":"absolute","bottom":"1em","right":"1em", "color":"grey"}), href="http://doi.org/10.2210/pdb%s/pdb"%data["PDBID"], target="_blank")]
        attributes_list=[]
        for attribute in attributes:
            if data[attribute] != "" and data[attribute] != []:
                if attribute in ["ATC Code Level 1","ATC Identifier","Targets","Enzymes","Carriers","Transporters","Drug Interactions","STRING Interaction Partners","Drugs", "Diseases"]:
                    attributes_list.append(dbc.Container(html.Li([html.Strong(attribute+": "),", ".join(data[attribute])], className="list-group-item"), style={"max-height":"20vh","overflow-y":"auto", "padding":"0"}, fluid=True))
                elif attribute == "ID":
                    attributes_list.append(html.Li([html.Strong(attribute+": "),html.A(data[attribute], href=link_drugbank, target="_blank")], className="list-group-item"))
                elif attribute == "PDBID" and data[attribute] != "Not Available":
                    attributes_list.append(html.Li([html.Strong(attribute+": "),html.A(data[attribute], href="https://www.rcsb.org/structure/"+data[attribute], target="_blank")], className="list-group-item"))
                elif attribute == "Gene":
                    attributes_list.append(html.Li([html.Strong(attribute+": "),html.A(data[attribute], href="https://www.uniprot.org/uniprot/"+data["ID"], target="_blank")], className="list-group-item"))
                else:
                    attributes_list.append(html.Li([html.Strong(attribute+": "),data[attribute]], className="list-group-item"))
        return data["id"],img,attributes_list,warning
    return displayHoverNodeData

def inspected_table_callback(prefix):
    @app.callback(
        [
            Output(prefix+"_inspected_table","children"),
            Output(prefix+"_side_inspected_table","active"),
            Output(prefix+"_side_inspected_table","disabled"),
            Output(prefix+"_inspected_data_side_tooltip","style"),
            Output(prefix+"_inspected_data","is_open"),
            Output(prefix+"_n_inspected_nodes","children"),
            Output(prefix+"_inspected_cache","value")
        ],
        [
            Input(prefix+"_graph", "selectedNodeData"),
            Input(prefix+"_highlighted_data_cache","value"),
            Input(prefix+"_inspected_dropdown","value")
        ]
    )
    def inspected_table(selected_data,highlighted_data,to_inspect):
        results=[html.H5("No Data to Show"),html.P("(Try changing the value of the dropdown menu)")]
        open=False
        visibility={"visibility":"hidden"}
        if not selected_data:
            selected_data=[]
        selected={data["ID"]:data for data in selected_data}
        highlighted={data["ID"]:data for data in highlighted_data}
        merged=selected.copy()
        merged.update(highlighted)
        if len(merged)>1:
            open=True
            visibility=None
        if to_inspect == "selected":
            data=selected_data
        elif to_inspect == "highlighted":
            data=highlighted_data
        elif to_inspect == "selected_or_highlighted":
            data=list(merged.values())
        else:
            data=[merged[id] for id in set(selected.keys()).intersection(set(highlighted.keys()))]
        if data:
            if len(data)>=1 and open:
                results=[]
                drugs_data=[d for d in data if d["kind"]=="Drug"]
                if len(drugs_data)>0:
                    attributes=["Name","ID","ATC Code Level 1","ATC Identifier","SMILES","Targets","Enzymes","Carriers","Transporters","Drug Interactions"]
                    table_header=[html.Thead(html.Tr([html.Th(attribute, style={"white-space": "nowrap"}) for attribute in ["Name","ID","ATC Level 1", "ATC Identifier", "SMILES","Targets","Enzymes","Carriers","Transporters","Drug Interactions"]]))]
                    table_body=[]
                    for drug in drugs_data:
                        row=[]
                        for attribute in attributes:
                            if attribute == "Name":
                                row.append(html.Td(drug["Name"]))
                            elif attribute == "ID":
                                row.append(html.Td(html.A(drug["ID"],href="https://www.drugbank.ca/drugs/"+drug["ID"], target="_blank")))
                            elif attribute == "SMILES":
                                row.append(html.Td(dbc.Container(drug["SMILES"], style={"max-height":"20vh","overflow-y":"auto", "padding":"0px"}, fluid=True), style={"min-width":"12vw","max-width":"20vw","word-break": "break-word","padding-right":"0px"}))
                            elif "ATC" in attribute:
                                row.append(html.Td(dbc.Container(", ".join(drug[attribute]), style={"max-height":"20vh","overflow-y":"auto","word-break": "break-word", "padding":"0px"}, fluid=True), style={"min-width":"7vw","max-width":"15vw","padding-right":"0px"}))
                            else:
                                row.append(html.Td(dbc.Container(", ".join(drug[attribute]), style={"max-height":"20vh","overflow-y":"auto","word-break": "break-word", "padding":"0px"}, fluid=True), style={"min-width":"10vw","max-width":"20vw","padding-right":"0px"}))
                        table_body.append(html.Tr(row))
                    table_body=[html.Tbody(table_body)]
                    drugs_table=dbc.Table(table_header+table_body, className="table table-hover", bordered=True)
                    drugs_href="data:text/csv;charset=utf-8,"+quote(pd.DataFrame([{key:(", ".join(value) if isinstance(value,list) else value) for key,value in d.items() if key in attributes} for d in drugs_data], columns=attributes).to_csv(sep="\t", index=False, encoding="utf-8"))
                    results+=[
                        html.Br(),
                        dbc.Row([
                            html.H4("Inspected Drugs"),
                            html.A(dbc.Button("Download", className="btn btn-outline-primary"),href=drugs_href, download="inspected_drugs.tsv", target="_blank"),
                        ], justify="around", align="center"),
                        html.Br(),
                        drugs_table]
                targets_data=[d for d in data if d["kind"]=="Target"]
                if len(targets_data)>0:
                    if len(drugs_data)>0:
                        results+=[html.Br()]
                    attributes=["Name","ID","Gene","PDBID","Organism","Protein Class","Protein Family","Cellular Location","STRING Interaction Partners","Drugs","Diseases"]
                    table_header=[html.Thead(html.Tr([html.Th(attribute, style={"white-space": "nowrap"}) for attribute in attributes]))]
                    table_body=[]
                    for target in targets_data:
                        row=[]
                        for attribute in attributes:
                            if attribute == "Name":
                                row.append(html.Td(target["Name"], style={"min-width":"8vw","max-width":"15vw"}))
                            elif attribute == "ID":
                                row.append(html.Td(html.A(target["ID"],href=target["drugbank_url"], target="_blank")))
                            elif attribute == "Gene":
                                row.append(html.Td(html.A(target["Gene"],href="https://www.uniprot.org/uniprot/"+target["ID"], target="_blank")))
                            elif attribute == "PDBID":
                                if target["PDBID"] != "Not Available":
                                    row.append(html.Td(html.A(target["PDBID"], href="https://www.rcsb.org/structure/"+target["PDBID"], target="_blank")))
                                else:
                                    row.append(html.Td(target["PDBID"]))
                            elif attribute in ["Organism","Protein Class","Protein Family","Cellular Location"]:
                                row.append(html.Td(target[attribute]))
                            else:
                                row.append(html.Td(dbc.Container(", ".join(target[attribute]), style={"max-height":"20vh","overflow-y":"auto","word-break": "break-word", "padding":"0px"}, fluid=True), style={"min-width":"10vw","max-width":"20vw","padding-right":"0px"}))
                        table_body.append(html.Tr(row))
                    table_body=[html.Tbody(table_body)]
                    targets_table=dbc.Table(table_header+table_body, className="table table-hover", bordered=True)
                    targets_href="data:text/csv;charset=utf-8,"+quote(pd.DataFrame([{key:(", ".join(value) if isinstance(value,list) else value) for key,value in d.items() if key in attributes} for d in targets_data], columns=attributes).to_csv(sep="\t", index=False, encoding="utf-8"))
                    results+=[
                        html.Br(),
                        dbc.Row([
                            html.H4("Inspected Targets"),
                            html.A(dbc.Button("Download", className="btn btn-outline-primary"),href=targets_href, download="inspected_targets.tsv", target="_blank"),
                        ], justify="around", align="center"),
                        html.Br(),
                        targets_table]

                return dbc.Container(results, fluid=True), True, False, visibility, open, "%d Nodes"%len(data), data
            else:
                return dbc.Container(results, fluid=True, style={"padding":"3%"}), False, True, visibility, open, None, []
        else:
            return dbc.Container(results, fluid=True, style={"padding":"3%"}), False, True, visibility, open, None, []
    return inspected_table

def properties_table_callback(prefix,graph_properties_df,nodes):
    @app.callback(
        [
            Output(prefix+"_graph_properties_table_container","children"),
            Output(prefix+"_download_graph_properties","href"),
            Output(prefix+"_search_properties","options")
        ],
        [
            Input(prefix+"_search_properties","value"),
            Input(prefix+"_properties_table_sorting","value"),
            Input(prefix+"_properties_table_rows","value"),
            Input(prefix+"_only_inspected_properties","value"),
            Input(prefix+"_inspected_cache", "value")
        ]
    )
    def properties_table(search,sorting,rows,only_inspected,inspected_data):
        df=graph_properties_df.copy()
        if prefix == "drug_target":
            df.drop("Clustering Coefficient", inplace=True, axis=1) # removes the clustering coefficient column from the dataframe of the Drug-Target Networks, since it is bipartited and the clustering coefficient has no meaning in this case
        if only_inspected and inspected_data:
            df=df.loc[[node["Name"] for node in inspected_data]]
            options=[{"label":name,"value":name} for name in [node["Name"] for node in inspected_data]]
        else:
            options=[{"label":data["Name"],"value":data["Name"]} for data in [node["data"] for node in nodes]]
        if search:
            df=df.loc[search]
        sorting=sorting.split(",")
        sorting={"by":[sorting[0]],"ascending":bool(int(sorting[1]))}
        df=df.sort_values(**sorting)
        href="data:text/csv;charset=utf-8,"+quote(df.to_csv(sep="\t", index=False, encoding="utf-8"))
        if rows != "all":
            df=df.head(rows)
        return dbc.Table.from_dataframe(df, bordered=True, className="table table-hover", id=prefix+"_graph_properties_table"), href, options
    return properties_table

def group_highlighter_callback(prefix,nodes,maj):
    def unite(conjunction,ll):
        if not ll:
            return []
        ll=[set(l.split(",")) if isinstance(l,str) else l for l in ll if l]
        if len(ll)>1:
            if conjunction == "OR":
                return ll[0].union(*ll[1:])
            else:
                return ll[0].intersection(*ll[1:])
        elif len(ll)==1:
            return ll[0]
        else:
            return ll
    def centrality_filter(centrality,equality,value):
        if value:
            if equality == ">=":
                return {node["data"]["ID"] for node in nodes if node["data"][centrality] >= value}
            elif equality == ">":
                return {node["data"]["ID"] for node in nodes if node["data"][centrality] > value}
            elif equality == "=":
                return {node["data"]["ID"] for node in nodes if node["data"][centrality] == value}
            elif equality == "<=":
                return {node["data"]["ID"] for node in nodes if node["data"][centrality] <= value}
            elif equality == "<":
                return {node["data"]["ID"] for node in nodes if node["data"][centrality] < value}
        else:
            return {}
    if prefix == "drug_target":
        properties=[]
    elif prefix == "drug_projection":
        properties=["ATC Code Level 1", "ATC Code Level 2", "ATC Code Level 3", "ATC Code Level 4", "Targets", "Enzymes", "Carriers", "Transporters", "Drug Interactions"]
    elif prefix == "target_projection":
        properties=["STRING Interaction Partners", "Drugs", "Diseases", "Organism", "Protein Class", "Protein Family", "Cellular Location"]
    centralities=["Degree","Closeness Centrality","Betweenness Centrality", "Eigenvector Centrality","Clustering Coefficient","VoteRank Score"]

    @app.callback(
        [
            Output(prefix+"_highlighted_cache","value"),
            Output(prefix+"_n_highlighted","children"),
            Output(prefix+"_download_group_highlighting_button_href","href"),
            Output(prefix+"_download_group_highlighting_button","disabled"),
        ],
        [Input(prefix+"_only_major_highlighted_groups","value")]+[Input(prefix+"_highlight_dropdown_"+property,"value") for property in properties]+[Input(prefix+"_conjunction_"+property,"value") for property in properties]+[Input(prefix+"_equality_"+centrality,"value") for centrality in centralities]+[Input(prefix+"_highlight_value_"+centrality,"value") for centrality in centralities]+[Input(prefix+"_conjunction_general","value")]
    )
    def group_highlighter(only_maj,*values):
        if isinstance(only_maj,list) and len(only_maj)>0 and only_maj[0]==True: # I don't know why it is needed, maybe because of the complex input
            only_maj=True
        else:
            only_maj=False
        highlighted_values=dict(zip(["highlighted_"+property for property in properties]+["conjunction_"+property for property in properties]+["equality_"+centrality for centrality in centralities]+["value_"+centrality for centrality in centralities]+["conjunction_general"],values))
        for centrality in centralities:
            highlighted_values["highlighted_"+centrality]=centrality_filter(centrality,highlighted_values["equality_"+centrality],highlighted_values["value_"+centrality])
        highlighted=unite(highlighted_values["conjunction_general"],[unite(highlighted_values["conjunction_"+property],highlighted_values["highlighted_"+property]) for property in properties]+[highlighted_values["highlighted_"+centrality] for centrality in centralities])
        if highlighted:
            if only_maj:
                maj_id=list(nx.get_node_attributes(maj,"ID").values())
                highlighted=[id for id in highlighted if id in maj_id]
            attributes=["Name","ID"]
            if prefix == "target_projection":
                attributes+=["Gene"]
            attributes+=properties+centralities
            href="data:text/csv;charset=utf-8,"+quote(pd.DataFrame([{attribute:(", ".join(node["data"][attribute]) if isinstance(node["data"][attribute],list) else node["data"][attribute]) for attribute in attributes} for node in nodes if node["data"]["ID"] in highlighted], columns=attributes).to_csv(sep="\t", index=False, encoding="utf-8"))
            return list(highlighted),len(highlighted),href,False
        else:
            return None,0,"",True

    @app.callback(
        [Output(prefix+"_only_major_highlighted_groups","value")]+[Output(prefix+"_highlight_dropdown_"+property,"value") for property in properties]+[Output(prefix+"_conjunction_"+property,"value") for property in properties]+[Output(prefix+"_equality_"+centrality,"value") for centrality in centralities]+[Output(prefix+"_highlight_value_"+centrality,"value") for centrality in centralities]+[Output(prefix+"_conjunction_general","value")],
        # [Output(prefix+"_highlight_dropdown_"+property,"value") for property in properties]+[Output(prefix+"_conjunction_"+property,"value") for property in properties]+[Output(prefix+"_conjunction_general","value")],
        [Input(prefix+"_group_highlighter_clear", "n_clicks")]
    )
    def clear_group_highlighter(n):
        return [True]+[None for property in properties]+["OR" for property in properties]+[">=" for centrality in centralities]+[None for centrality in centralities]+["OR"]

    @app.callback(
        Output(prefix+"_highlighter_dropdown", "value"),
        [Input(prefix+"_group_highlighter_close", "n_clicks")],
        [State(prefix+"_highlighted_cache","value")]
    )
    def confirm_group_highlighter(n, highlighted):
        if n:
            return highlighted
    return group_highlighter, clear_group_highlighter,confirm_group_highlighter


def highlighter_callback(prefix,G,nodes,L,evals,evects,n_clusters,clusters,L_maj,evals_maj,evects_maj,n_clusters_maj,clusters_maj,girvan_newman,maj,girvan_newman_maj,n_comm,n_comm_maj, atc_description):
    print("\tColoring Precomputing ...")
    ##coloring precomputing
    #components
    components=list(nx.connected_components(G))
    d_comp={}
    for n,comp in enumerate(components):
        d_comp.update({d:n for d in comp})
    name2id=dict(dict(nx.get_node_attributes(G,"ID")))
    cmap=dict(zip(sorted(set(d_comp.values())),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(components))]))
    id2component={name2id[node]:cmap.get(d_comp[node],"#708090") for node in G.nodes()}
    stylesheet_components=[]
    for ID in id2component:
        stylesheet_components.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2component[ID]}})
    pie_data=go.Pie(labels=list(range(1,len(components)+1)), values=[len(component) for component in components], marker_colors=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(components))])
    pie_components=go.Figure(data=pie_data, layout={"title":{"text":"Components' Node Distribution","x":0.5, "xanchor": "center"}})
    pie_components.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" Component: %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
    legend_body_components=html.P("Nodes are colored on the corresponding component")
    #spectral
    cmap=dict(zip(sorted(set(clusters)),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/n_clusters)]))
    id_cluster=dict(zip(dict(nx.get_node_attributes(G,"ID")).values(),clusters))
    stylesheet_spectral=[]
    for ID in id_cluster:
        stylesheet_spectral.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":cmap[id_cluster[ID]]}})
    pie_data=go.Pie(labels=list(range(1,len(clusters)+1)), values=[list(clusters).count(cluster) for cluster in range(len(set(clusters)))], marker_colors=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(set(clusters)))])
    pie_spectral=go.Figure(data=pie_data, layout={"title":{"text":"Clusters' Node Distribution","x":0.5, "xanchor": "center"}})
    pie_spectral.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" Cluster: %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
    legend_body_spectral=html.P(["Nodes are colored on the corresponding cluster, check the ",html.A("clustering", href="#"+prefix+"_clustering")," or ",html.A("plots sections", href="#"+prefix+"_plots")," for more info"])
    #spectral_maj
    cmap=dict(zip(sorted(set(clusters_maj)),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/n_clusters_maj)]))
    id_cluster=dict(zip(dict(nx.get_node_attributes(maj,"ID")).values(),clusters_maj))
    stylesheet_spectral_maj=[]
    for ID in id_cluster:
        stylesheet_spectral_maj.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":cmap[id_cluster.get(ID,"#708090")]}})
    pie_data=go.Pie(labels=list(range(1,len(clusters_maj)+1)), values=[list(clusters_maj).count(cluster) for cluster in range(len(set(clusters_maj)))], marker_colors=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(set(clusters_maj)))])
    pie_spectral_maj=go.Figure(data=pie_data, layout={"title":{"text":"Clusters' Node Distribution","x":0.5, "xanchor": "center"}})
    pie_spectral_maj.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" Cluster: %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
    legend_body_spectral_maj=html.P(["Nodes are colored on the corresponding cluster, check the ",html.A("clustering", href="#"+prefix+"_clustering")," or ",html.A("plots sections", href="#"+prefix+"_plots")," for more info"])
    #girvan_newman
    communities=girvan_newman[n_comm]
    d_comm={}
    for n,comm in enumerate(communities):
        d_comm.update({d:n for d in comm})
    name2id=dict(dict(nx.get_node_attributes(G,"ID")))
    cmap=dict(zip(sorted(set(d_comm.values())),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))]))
    id2community={name2id[node]:cmap.get(d_comm[node],"#708090") for node in G.nodes()}
    stylesheet_girvan_newman=[]
    for ID in id2community:
        stylesheet_girvan_newman.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2community[ID]}})
    pie_data=go.Pie(labels=list(range(1,len(communities)+1)), values=[len(community) for community in communities], marker_colors=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))])
    pie_girvan_newman=go.Figure(data=pie_data, layout={"title":{"text":"Communities' Node Distribution","x":0.5, "xanchor": "center"}})
    pie_girvan_newman.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" Community: %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
    legend_body_girvan_newman=html.P(["Nodes are colored on the corresponding community, check the ",html.A("clustering", href="#"+prefix+"_clustering")," or ",html.A("plots sections", href="#"+prefix+"_plots")," for more info"])
    #girvan_newman_maj
    communities=girvan_newman_maj[n_comm_maj]
    d_comm={}
    for i,comm in enumerate(communities):
        d_comm.update({d:i for d in comm})
    name2id=dict(dict(nx.get_node_attributes(maj,"ID")))
    cmap=dict(zip(sorted(set(d_comm.values())),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))]))
    id2community={name2id[node]:cmap.get(d_comm[node],"#708090") for node in maj.nodes()}
    stylesheet_girvan_newman_maj=[]
    for ID in id2community:
        stylesheet_girvan_newman_maj.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2community.get(ID,"#708090")}})
    pie_data=go.Pie(labels=list(range(1,len(communities)+1)), values=[len(community) for community in communities], marker_colors=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))])
    pie_girvan_newman_maj=go.Figure(data=pie_data, layout={"title":{"text":"Communities' Node Distribution","x":0.5, "xanchor": "center"}})
    pie_girvan_newman_maj.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" Community: %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
    legend_body_girvan_newman_maj=html.P(["Nodes are colored on the corresponding community, check the ",html.A("clustering", href="#"+prefix+"_clustering")," or ",html.A("plots sections", href="#"+prefix+"_plots")," for more info"])
    #greedy_modularity
    communities=nx.algorithms.community.greedy_modularity_communities(G)
    d_comm={}
    for i,comm in enumerate(communities):
        d_comm.update({d:i for d in comm})
    name2id=dict(dict(nx.get_node_attributes(G,"ID")))
    cmap=dict(zip(sorted(set(d_comm.values())),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))]))
    id2community={name2id[node]:cmap.get(d_comm[node],"#708090") for node in G.nodes()}
    stylesheet_greedy_modularity=[]
    for ID in id2community:
        stylesheet_greedy_modularity.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2community.get(ID,"#708090")}})
    pie_data=go.Pie(labels=list(range(1,len(communities)+1)), values=[len(community) for community in communities], marker_colors=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))])
    pie_greedy_modularity=go.Figure(data=pie_data, layout={"title":{"text":"Communities' Node Distribution","x":0.5, "xanchor": "center"}})
    pie_greedy_modularity.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" Community: %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
    legend_body_greedy_modularity=html.P(["Nodes are colored on the corresponding community, check the ",html.A("clustering", href="#"+prefix+"_clustering")," or ",html.A("plots sections", href="#"+prefix+"_plots")," for more info"])
    #greedy_modularity_maj
    communities=nx.algorithms.community.greedy_modularity_communities(maj)
    d_comm={}
    for i,comm in enumerate(communities):
        d_comm.update({d:i for d in comm})
    name2id=dict(dict(nx.get_node_attributes(maj,"ID")))
    cmap=dict(zip(sorted(set(d_comm.values())),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))]))
    id2community={name2id[node]:cmap.get(d_comm[node],"#708090") for node in maj.nodes()}
    stylesheet_greedy_modularity_maj=[]
    for ID in id2community:
        stylesheet_greedy_modularity_maj.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2community.get(ID,"#708090")}})
    pie_data=go.Pie(labels=list(range(1,len(communities)+1)), values=[len(community) for community in communities], marker_colors=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))])
    pie_greedy_modularity_maj=go.Figure(data=pie_data, layout={"title":{"text":"Communities' Node Distribution","x":0.5, "xanchor": "center"}})
    pie_greedy_modularity_maj.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" Community: %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
    legend_body_greedy_modularity_maj=html.P(["Nodes are colored on the corresponding community, check the ",html.A("clustering", href="#"+prefix+"_clustering")," or ",html.A("plots sections", href="#"+prefix+"_plots")," for more info"])

    @app.callback(
        [
            Output(prefix+"_graph","stylesheet"),
            Output(prefix+"_piechart","figure"),
            Output(prefix+"_legend_toast","children"),
            Output(prefix+"_clusters_cache","value"),
            Output(prefix+"_highlighted_data_cache","value"),
        ],
        [
            Input(prefix+"_highlighter_dropdown", "value"),
            Input(prefix+"_coloring_dropdown","value"),
            Input(prefix+"_custom_clustering_method","value"),
            Input(prefix+"_custom_clustering_component","value"),
            Input(prefix+"_custom_clustering_number_clusters","value")
        ],
        [
            State(prefix+"_graph","stylesheet"),
            State(prefix+"_piechart","figure"),
            State(prefix+"_legend_toast","children")
        ]
    )
    def highlighter(highlighted,coloring,custom_method,custom_component,custom_n, current_stylesheet, current_pie, current_legend_body):
        if custom_component == "entire":
            clusters_cache = clusters
        else:
            clusters_cache = clusters_maj
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if changed_id != prefix+"_highlighter_dropdown.value":
            if "Centrality" in coloring or coloring in [name+comp for name in ["Degree","Clustering Coefficient","VoteRank Score"] for comp in ["","_maj"]]:
                if "maj" in coloring:
                    coloring=coloring.split("_")[0]
                    centrality=dict(zip(nx.get_node_attributes(maj,"ID").values(),nx.get_node_attributes(maj,coloring).values()))
                else:
                    centrality={node["data"]["ID"]:node["data"][coloring] for node in nodes}
                values_unique=sorted(set(centrality.values()))
                scaled=sorted(MinMaxScaler().fit_transform(np.array(values_unique).reshape(-1, 1)).reshape(1,-1)[0].tolist())
                cmap=dict(zip(values_unique,[rgb2hex(plt.cm.coolwarm(i)) for i in scaled]))
                stylesheet=[]
                for ID,c in centrality.items():
                    stylesheet.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":cmap.get(c,"#708090")}})
                values=sorted(centrality.values())
                nbins=20
                binner=KBinsDiscretizer(nbins,strategy="uniform", encode="ordinal")
                bins=binner.fit_transform(np.array(values).reshape(-1,1)).reshape(1,-1)[0].tolist()
                counts=[bins.count(n) for n in set(bins)]
                if "Degree" not in coloring:
                    bin_edges=[(round(binner.bin_edges_[0][i],3),round(binner.bin_edges_[0][i+1],3)) for i in range(nbins)]
                    labels=np.array(["%.3f \u2264 %s \u2264 %.3f"%(edge[0],coloring,edge[1]) for edge in bin_edges])[[int(n) for n in set(bins)]]
                else:
                    bin_edges=[(int(binner.bin_edges_[0][i]),int(binner.bin_edges_[0][i+1])) for i in range(nbins)]
                    labels=np.array(["%d \u2264 %s \u2264 %d"%(int(edge[0]),coloring,int(edge[1])) for edge in bin_edges])[[int(n) for n in set(bins)]]
                mid_points=np.array([(edge[0]+edge[1])/2 for edge in bin_edges]).reshape(-1, 1)
                marker_colors=np.array([rgb2hex(plt.cm.coolwarm(i)) for i in sorted(MinMaxScaler().fit_transform(mid_points).reshape(1,-1)[0].tolist())])[[int(n) for n in set(bins)]]
                pie_data=go.Pie(labels=labels,values=counts, marker_colors=marker_colors)
                pie=go.Figure(data=pie_data, layout={"title":{"text":"Nodes' Centrality Distribution","x":0.5, "xanchor": "center"}})
                pie.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
                colors=np.array([rgb2hex(plt.cm.coolwarm(i)) for i in np.linspace(0,1,10)])
                legend_palette=px.imshow(np.linspace(min(values),max(values),1000).reshape(-1,1),color_continuous_scale=colors,y=np.linspace(min(values),max(values),1000), labels={"y":coloring}, aspect="auto")
                legend_palette.update(layout_coloraxis_showscale=False)
                legend_palette.update_xaxes(showticklabels=False)
                legend_palette.update_traces(hovertemplate=" "+coloring+": %{y:.3f} <extra></extra>")
                legend_palette.update_layout(margin={"pad":0, "t":5, "b":5})
                legend_body=dcc.Graph(figure=legend_palette, responsive=True, config={"displayModeBar": False})

            if coloring == "categorical":
                stylesheet=stylesheet_base.copy()
                pie_data=go.Pie(labels=["Drugs","Targets"],values=[len([node for node,kind in G.nodes("kind") if kind == "Drug"]),len([node for node,kind in G.nodes("kind") if kind == "Target"])], marker_colors=["#FC5F67","#12EAEA"])
                pie=go.Figure(data=pie_data, layout={"title":{"text":"Nodes' Categories Distribution","x":0.5, "xanchor": "center"}})
                pie.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
                legend_body=dbc.Table(html.Tbody([html.Tr([html.Td("",style={"background-color":"#FC5F67"}),html.Td("Drugs")]),html.Tr([html.Td("",style={"background-color":"#12EAEA"}),html.Td("Targets")])]), borderless=True, size="sm")

            elif coloring == "targetclass":
                target_classes={node["data"]["Name"]:node["data"]["Target Class"] for node in nodes}
                all_classes=sorted(set([l for ll in target_classes.values() for l in ll]))
                cmap=dict(zip(all_classes,[rgb2hex(plt.cm.Spectral(n)) for n in np.arange(0,1.1,1/len(all_classes))]))
                cmap.update({"Not Available":"#708090"})
                class2num={list(cmap.keys())[num]:str(num+1) for num in range(len(all_classes))}
                stylesheets=[]
                classes_count={}
                tot_classes=0
                for node,classes in target_classes.items():
                    stylesheet={"selector":"[ID = '"+[element["data"]["ID"] for element in nodes if element["data"]["Name"]==node][0]+"']"}
                    style={"pie-size":"100%", "border-color":"#303633","border-width":2}
                    for target_class in classes:
                        style.update({"pie-"+class2num[target_class]+"-background-color":cmap[target_class],"pie-"+class2num[target_class]+"-background-size":100/len(classes)})
                        try:
                            classes_count[target_class]+=1/len(classes)
                        except:
                            classes_count[target_class]=1/len(classes)
                        tot_classes+=1
                    stylesheet.update({"style":style})
                    stylesheets.append(stylesheet)
                stylesheet=stylesheets

                pie_data=go.Pie(labels=list(classes_count.keys()), values=[int(value) for value in classes_count.values()], marker_colors=[cmap[target_class] for target_class in classes_count.keys()])
                pie=go.Figure(data=pie_data, layout={"title":{"text":"Nodes' Categories Distribution","x":0.5, "xanchor": "center"}})
                pie.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
                table_body=[]
                for target_class in cmap:
                    table_body.append(html.Tr([html.Td("",style={"background-color":cmap[target_class]}),html.Td(target_class)]))
                legend_body=dbc.Table(html.Tbody(table_body), borderless=True, size="sm")

            elif coloring == "atc":
                all_atc=["A","B","C","D","G","H","J","L","M","N","P","R","S","V"]
                # long_atc={"A":"A: Alimentary tract and metabolism","B":"B: Blood and blood forming organs","C":"C: Cardiovascular system","D":"D: Dermatologicals","G":"G: Genito-urinary system and sex hormones","H":"H: Systemic hormonal preparations, excluding sex hormones and insulins","J":"J: Antiinfectives for systemic use","L":"L: Antineoplastic and immunomodulating agents","M":"M: Musculo-skeletal system","N":"N: Nervous system","P":"P: Antiparasitic products, insecticides and repellents","R":"R: Respiratory system","S":"S: Sensory organs","V":"V: Various","Not Available": "Not Available"}
                long_atc,long_atc3=atc_description

                cmap=dict(zip(all_atc,[rgb2hex(plt.cm.Spectral(n)) for n in np.arange(0,1.1,1/14)]))
                cmap.update({"Not Available":"#708090"})
                atc2num={list(cmap.keys())[num]:str(num+1) for num in range(15)}
                stylesheets=[]
                for node in nodes:
                    stylesheet={"selector":"[ID = '"+node["data"]["ID"]+"']"}
                    style={"pie-size":"100%", "border-color":"#303633","border-width":2}
                    for atc in node["data"]["ATC Code Level 1"]:
                        style.update({"pie-"+atc2num[atc]+"-background-color":cmap[atc],"pie-"+atc2num[atc]+"-background-size":100/len(node["data"]["ATC Code Level 1"])})
                    stylesheet.update({"style":style})
                    stylesheets.append(stylesheet)
                ATC_dict=dict(nx.get_node_attributes(G,"ATC Code Level 1"))
                tmp_atc_values=[l for ll in ATC_dict.values() for l in ll]
                ATC_count={atc:tmp_atc_values.count(atc) for atc in cmap.keys()}
                ATC_count={k: v for k, v in sorted(ATC_count.items(), key=lambda item: item[1], reverse=True)}#sort by value

                stylesheet=stylesheets

                ATC3_dict=dict(nx.get_node_attributes(G,"ATC Code Level 3"))
                tmp_atc3_values=[l for ll in ATC3_dict.values() for l in ll]
                ATC3_count={atc:tmp_atc3_values.count(atc) for atc in set(tmp_atc3_values)}
                ATC3_count={k: v for k, v in sorted(ATC3_count.items(), key=lambda item: item[1], reverse=True)}#sort by value
                ATC1_getter={atc3:atc3[0] if atc3 != "Not Available" else "Not Available" for atc3 in ATC3_count.keys()}
                rule=list(ATC_count.keys())

                ATC1_apparent_count={}
                for code,value in ATC3_count.items():
                    if ATC1_getter[code] in ATC1_apparent_count:
                        ATC1_apparent_count[ATC1_getter[code]]+=value
                    else:
                        ATC1_apparent_count[ATC1_getter[code]]=value
                ATC3_count_normalized={k:v*ATC_count[ATC1_getter[k]]/ATC1_apparent_count[ATC1_getter[k]] for k,v in ATC3_count.items()}

                pie_data=[]
                for atc3 in ATC3_count:
                    y=[0]*len(rule)
                    y[rule.index(ATC1_getter[atc3])]=ATC3_count_normalized[atc3]
                    text=[""]*len(rule)
                    text[rule.index(ATC1_getter[atc3])]=long_atc3[atc3]
                    pie_data.append(go.Bar(x=rule, y=y, marker={"color":cmap[ATC1_getter[atc3]], "line":{"color":"lightgrey","width":1}}, text=text, meta=[ATC3_count[atc3],long_atc[ATC1_getter[atc3]], ATC_count[ATC1_getter[atc3]]]))
                pie=go.Figure(data=pie_data, layout={"title":{"text":"Nodes' Categories Distribution","x":0.5, "xanchor": "center"}})
                pie.update_traces(hovertemplate="<b> ATC Level 3 </b> <br> %{text} <br> Nodes: %{meta[0]} <br><br><b> ATC Level 1 </b> <br> %{meta[1]}  <br> Nodes: %{meta[2]} <extra></extra>")
                pie.update_layout(barmode="stack")
                table_body=[]
                for code in cmap:
                    table_body.append(html.Tr([html.Td("",style={"background-color":cmap[code]}),html.Td(long_atc[code])]))
                legend_body=dbc.Table(html.Tbody(table_body), borderless=True, size="sm")
            elif coloring in ["class","family","location"]:
                property_name={"class":"Protein Class","family":"Protein Family","location":"Cellular Location"}[coloring]
                all_properties=sorted(set([node["data"][property_name] for node in nodes]))
                cmap=dict(zip(all_properties,[rgb2hex(plt.cm.Spectral(n)) for n in np.arange(0,1.1,1/len(all_properties))]))
                cmap.update({"Not Available":"#708090"})
                stylesheets=[]
                for node in nodes:
                    stylesheet={"selector":"[ID = '"+node["data"]["ID"]+"']"}
                    style={"background-color":cmap[node["data"][property_name]], "border-color":"#303633","border-width":2}
                    stylesheet.update({"style":style})
                    stylesheets.append(stylesheet)
                properties_dict=dict(nx.get_node_attributes(G,property_name))
                properties_count={property:list(properties_dict.values()).count(property) for property in all_properties}
                stylesheet=stylesheets

                pie_data=go.Pie(labels=all_properties, values=list(properties_count.values()), marker_colors=[cmap[property] for property in all_properties])
                pie=go.Figure(data=pie_data, layout={"title":{"text":"Nodes' Categories Distribution","x":0.5, "xanchor": "center"}})
                pie.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
                table_body=[]
                for property in all_properties:
                    table_body.append(html.Tr([html.Td("",style={"background-color":cmap[property]}),html.Td(property)]))
                legend_body=dbc.Table(html.Tbody(table_body), borderless=True, size="sm")
            elif coloring == "components":
                stylesheet=stylesheet_components.copy()
                pie=pie_components
                legend_body=legend_body_components
            elif coloring == "spectral_group":
                stylesheet=stylesheet_spectral.copy()
                pie=pie_spectral
                legend_body=legend_body_spectral
            elif coloring == "spectral_group_maj":
                stylesheet=stylesheet_spectral_maj.copy()
                pie=pie_spectral_maj
                legend_body=legend_body_spectral_maj
                clusters_cache=clusters_maj
            elif coloring == "girvan_newman_group":
                stylesheet=stylesheet_girvan_newman.copy()
                pie=pie_girvan_newman
                legend_body=legend_body_girvan_newman
            elif coloring == "girvan_newman_group_maj":
                stylesheet=stylesheet_girvan_newman_maj.copy()
                pie=pie_girvan_newman_maj
                legend_body=legend_body_girvan_newman_maj
            elif coloring == "greedy_modularity_group":
                stylesheet=stylesheet_greedy_modularity.copy()
                pie=pie_greedy_modularity
                legend_body=legend_body_greedy_modularity
            elif coloring == "greedy_modularity_group_maj":
                stylesheet=stylesheet_greedy_modularity_maj.copy()
                pie=pie_greedy_modularity_maj
                legend_body=legend_body_greedy_modularity_maj
            elif coloring == "custom":
                if custom_component=="maj":
                    graph=maj.copy()
                    girvan_newman_custom=girvan_newman_maj
                    greedy_modularity_custom_stylesheet=stylesheet_greedy_modularity_maj.copy()
                    greedy_modularity_custom_pie=pie_greedy_modularity_maj
                    evals_custom,evects_custom=evals_maj,evects_maj
                else:
                    graph=G.copy()
                    girvan_newman_custom=girvan_newman
                    greedy_modularity_custom_stylesheet=stylesheet_greedy_modularity.copy()
                    greedy_modularity_custom_pie=pie_greedy_modularity
                    evals_custom,evects_custom=evals,evects
                if custom_method == "spectral_group":
                    km_custom=KMeans(n_clusters=custom_n, n_init=100)
                    clusters_custom=km_custom.fit_predict(evects_custom[:,:custom_n])
                    cmap_custom=dict(zip(sorted(set(clusters_custom)),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/custom_n)]))
                    id_cluster_custom=dict(zip(dict(nx.get_node_attributes(graph,"ID")).values(),clusters_custom))
                    stylesheet=[]
                    for ID in id_cluster_custom:
                        stylesheet.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":cmap_custom[id_cluster_custom[ID]]}})
                    pie_data=go.Pie(labels=list(range(1,len(clusters_custom)+1)), values=[list(clusters_custom).count(cluster) for cluster in range(len(set(clusters_custom)))], marker_colors=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(set(clusters_custom)))])
                    pie=go.Figure(data=pie_data, layout={"title":{"text":"Clusters' Node Distribution","x":0.5, "xanchor": "center"}})
                    pie.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" Cluster: %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
                    clusters_cache=clusters_custom
                elif custom_method == "girvan_newman_group":
                    communities=girvan_newman_custom[custom_n]
                    d_comm={}
                    for n,comm in enumerate(communities):
                        d_comm.update({d:n for d in comm})
                    name2id=dict(dict(nx.get_node_attributes(graph,"ID")))
                    cmap=dict(zip(sorted(set(d_comm.values())),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/custom_n)]))
                    id2community={name2id[node]:cmap.get(d_comm[node],"#708090") for node in graph.nodes()}
                    stylesheet=[]
                    for ID in id2community:
                        stylesheet.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2community.get(ID,"#708090")}})
                    pie_data=go.Pie(labels=list(range(1,len(communities)+1)), values=[len(community) for community in communities], marker_colors=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))])
                    pie=go.Figure(data=pie_data, layout={"title":{"text":"Communities' Node Distribution","x":0.5, "xanchor": "center"}})
                    pie.update_traces(textposition="inside", textinfo="label+percent", hovertemplate=" Community: %{label} <br> Nodes: %{value} </br> %{percent} <extra></extra>")
                elif custom_method == "greedy_modularity_group":
                    stylesheet=greedy_modularity_custom_stylesheet
                    pie=greedy_modularity_custom_pie

                legend_body=html.P(["Nodes are colored on the corresponding cluster/community, check the ",html.A("clustering", href="#"+prefix+"_clustering")," or ",html.A("plots sections", href="#"+prefix+"_plots")," for more info"])
            pie.update_layout(plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", modebar={"bgcolor":"rgba(0, 0, 0, 0)","color":"silver","activecolor":"grey"}, uniformtext_minsize=8, uniformtext_mode="hide", showlegend=False)#title={"text":"Groups' Node Distribution","x":0.5, "xanchor": "center"}
        else:
            stylesheet=[style for style in current_stylesheet if style["style"].get("border-style") != "double"]
            pie=current_pie
            legend_body=current_legend_body
        stylesheet+=[{
            "selector":"node:selected",
            "style":{
                "background-color":"#FFE985",
                "border-color":"#FFDD4A",
                "border-width":6
            }
        }]
        if highlighted:
            data={node["data"]["ID"]:node["data"] for node in nodes}
            highlighted_data=[data[id] for id in highlighted]
            for val in highlighted:
                stylesheet+=[
                    {
                        "selector":"[ID = '"+val+"']",
                        "style":{
                            "content":"data(id)",
                            "border-style":"double",
                            "border-width":25,
                            "border-color":"#0ddfa6"
                        }
                    }
                ]
        else:
            highlighted_data=[]
        return stylesheet, pie, legend_body, clusters_cache.tolist(), highlighted_data
    return highlighter

def toggle_download_graph_callback(prefix):
    @app.callback(
        Output(prefix+"_save_graph_modal", "is_open"),
        [Input(prefix+"_save_graph_open", "n_clicks"), Input(prefix+"_save_graph_close", "n_clicks")],
        [State(prefix+"_save_graph_modal", "is_open")],
    )
    def toggle_download_graph(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open
    return toggle_download_graph

def toggle_help_callback(prefix):
    @app.callback(
        Output(prefix+"_help_popover", "is_open"),
        [Input(prefix+"_help_open", "n_clicks")],
        [State(prefix+"_help_popover", "is_open")],
    )
    def toggle_help(n, is_open):
        if n:
            return not is_open
        return is_open
    return toggle_help

def toggle_legend_callback(prefix):
    @app.callback(
        Output(prefix+"_legend_toast", "is_open"),
        [Input(prefix+"_legend_open", "n_clicks")],
    )
    def open_legend(n):
        if n:
            return True
    return open_legend


def download_graph_callback(prefix):
    @app.callback(
        [
            Output(prefix+"_download_graph_button_href","download"),
            Output(prefix+"_download_graph_button_href","href"),
            Output(prefix+"_graph","generateImage")
        ],
        [
            Input(prefix+"_save_graph","value"),
            Input(prefix+"_download_graph_button","n_clicks")
        ]
    )
    def download_graph(ftype,n_clicks):
        download=None
        href=None
        action="store"
        if ftype in ["svg", "png", "jpg"]:
            changed_id = dash.callback_context.triggered[0]["prop_id"]
            if changed_id==prefix+"_download_graph_button.n_clicks":
                action="download"
            else:
                ftype="tmp"
        else:
            if ftype:
                download=prefix+"."+ftype
                href=app.get_asset_url("graphs/"+prefix+"/"+download)
        return download,href,{"type":ftype,"action":action, "filename":prefix}
    return download_graph

def open_advanced_section(prefix):
    if "projection" in prefix:
        @app.callback(
            [
                Output(prefix+"_advanced_section_collapse", "is_open"),
                Output(prefix+"_side_clustering","active"),
                Output(prefix+"_side_clustering","disabled"),
                Output(prefix+"_clustering_side_tooltip","style"),
                Output(prefix+"_side_adv_degree_distribution","active"),
                Output(prefix+"_side_adv_degree_distribution","disabled"),
                Output(prefix+"_adv_degree_distribution_side_tooltip","style"),
                Output(prefix+"_side_virus_host_interactome","active"),
                Output(prefix+"_side_virus_host_interactome","disabled"),
                Output(prefix+"_virus_host_interactome_side_tooltip","style"),
            ],
            [Input(prefix+"_advanced_section_open", "n_clicks")],
            [State(prefix+"_advanced_section_collapse", "is_open")]
        )
        def open_advanced_section(n, is_open):
            if n:
                is_open = not is_open
            if is_open:
                sides = True, False, None
            else:
                sides = False, True, {"visibility":"hidden"}
            return [is_open, *sides, *sides, *sides]
    else:
        @app.callback(
            [
                Output(prefix+"_advanced_section_collapse", "is_open"),
                Output(prefix+"_side_clustering","active"),
                Output(prefix+"_side_clustering","disabled"),
                Output(prefix+"_clustering_side_tooltip","style"),
                Output(prefix+"_side_virus_host_interactome","active"),
                Output(prefix+"_side_virus_host_interactome","disabled"),
                Output(prefix+"_virus_host_interactome_side_tooltip","style"),
            ],
            [Input(prefix+"_advanced_section_open", "n_clicks")],
            [State(prefix+"_advanced_section_collapse", "is_open")]
        )
        def open_advanced_section(n, is_open):
            if n:
                is_open = not is_open
            if is_open:
                sides = True, False, None
            else:
                sides = False, True, {"visibility":"hidden"}
            return [is_open, *sides, *sides]
    return open_advanced_section

def toggle_group_highlighter_callback(prefix):
    @app.callback(
        Output(prefix+"_group_highlighting_modal", "is_open"),
        [Input(prefix+"_group_highlighter_open", "n_clicks"), Input(prefix+"_group_highlighter_close", "n_clicks")],
        [State(prefix+"_group_highlighting_modal", "is_open")],
    )
    def toggle_group_highlighter(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open
    return toggle_group_highlighter

def get_selected_clustering_callback(prefix):
    @app.callback(
        [
            Output(prefix+"_custom_clustering_component","value"),
            Output(prefix+"_custom_clustering_method","value")
        ],
        [Input(prefix+"_coloring_dropdown", "value")],
        [
            State(prefix+"_custom_clustering_component","value"),
            State(prefix+"_custom_clustering_method","value")
        ]
    )
    def get_selected_clustering(value,current_component,current_method):
        if "group" in value:
            if "maj" in value:
                component = "maj"
                method=value[:-4]
            else:
                component = "entire"
                method = value
        else:
            component = current_component
            method = current_method
        return component, method
    return get_selected_clustering

def get_range_clusters_callback(prefix,G,maj,Evals,Evals_maj,N_clusters,N_clusters_maj,Girvan_newman,Girvan_newman_maj,N_comm,N_comm_maj):
    @app.callback(
        [
            Output(prefix+"_custom_clustering_number_clusters","options"),
            Output(prefix+"_custom_clustering_number_clusters","value"),
            Output(prefix+"_custom_clustering_number_clusters","disabled"),
        ],
        [
            Input(prefix+"_custom_clustering_component","value"),
            Input(prefix+"_custom_clustering_method","value")
        ],
        [
            State(prefix+"_coloring_dropdown", "value"),
            State(prefix+"_custom_clustering_number_clusters","value")
        ]
    )
    def get_range_clusters(component,method,coloring,n_custom):
        if component=="maj":
            graph=maj.copy()
            evals=Evals_maj
            n_clusters=N_clusters_maj
            communities=Girvan_newman_maj
            n_comm=N_comm_maj
        else:
            graph=G.copy()
            evals=Evals
            n_clusters=N_clusters
            communities=Girvan_newman
            n_comm=N_comm
        if method == "spectral_group":
            n=n_clusters
            options=[{"label":str(n),"value":n} for n in range(2,len(evals)-1)]
            disabled=False
        elif method == "girvan_newman_group":
            n=n_comm
            options=[{"label":str(n),"value":n} for n in communities.keys()]
            disabled=False
        elif method == "greedy_modularity_group":
            n=len(nx.algorithms.community.greedy_modularity_communities(graph))
            options=[{"label":str(n),"value":n}]
            disabled=True
        if coloring == "custom" and n != n_custom and dash.callback_context.triggered[0]["prop_id"] == prefix+"_coloring_dropdown.value":
            n=n_custom
        return options,n,disabled
    return get_range_clusters

def custom_clustering_section_callback(prefix,G,Evals,Evects,Evals_maj,Evects_maj,Girvan_newman,maj,Girvan_newman_maj,Communities_modularity,Communities_modularity_maj):
    @app.callback(
        [
            Output(prefix+"_custom_clustering_graph","figure"),
            Output(prefix+"_custom_clusters_table_container","children"),
            Output(prefix+"_download_custom_clusters_modal","href"),
            Output(prefix+"_custom_clustering_graph_col","style")
        ],
        [
            Input(prefix+"_custom_clustering_component","value"),
            Input(prefix+"_custom_clustering_method","value"),
            Input(prefix+"_custom_clustering_number_clusters","value"),
            Input(prefix+"_clusters_cache","value")
        ]
    )
    def custom_clustering_section(component, method, n_clusters, clusters):
        style={}
        if component=="maj":
            graph=maj.copy()
            evals,evects=Evals_maj,Evects_maj
            girvan_newman=Girvan_newman_maj
            communities_modularity=Communities_modularity_maj
        else:
            graph=G.copy()
            evals,evects=Evals,Evects
            girvan_newman=Girvan_newman
            communities_modularity=Communities_modularity
        if method == "spectral_group":
            clusters_data={}
            for n,cl in enumerate(clusters):
                try:
                    clusters_data[cl].append(list(dict(graph.nodes("Name")).values())[n])
                except:
                    clusters_data[cl]=[list(dict(graph.nodes("Name")).values())[n]]
            clusters_data={n:", ".join(clusters_data[n]) for n in range(len(clusters_data))}
            table_header=[html.Thead(html.Tr([html.Th("Cluster"),html.Th("Nodes")]))]
            table_body=[]
            for cluster in clusters_data:
                table_body+=[html.Tr([html.Td(cluster+1), html.Td(clusters_data[cluster])])]
            table=dbc.Table(table_header+[html.Tbody(table_body)], className="table table-hover", bordered=True, id=prefix+"_custom_clusters_table")
            href="data:text/csv;charset=utf-8,"+quote(pd.DataFrame({"Cluster":list(clusters_data.keys()),"Nodes":list(clusters_data.values())}).to_csv(sep="\t", index=False, encoding="utf-8"))
            clustering_data=pd.DataFrame({"Eigenvalue Number":range(len(evals)),"Eigenvalue":evals})
            figure=px.scatter(data_frame=clustering_data,x="Eigenvalue Number",y="Eigenvalue", title="Eigenvalues Distribution", template="ggplot2")
        elif method == "girvan_newman_group":
            communities=girvan_newman[n_clusters]
            table_header=[html.Thead(html.Tr([html.Th("Community"),html.Th("Nodes")]))]
            table_body=[]
            for n, community in enumerate(communities):
                table_body+=[html.Tr([html.Td(n+1), html.Td(", ".join(community))])]
            table=dbc.Table(table_header+[html.Tbody(table_body)], className="table table-hover", bordered=True, id=prefix+"_custom_clusters_table")
            href="data:text/csv;charset=utf-8,"+quote(pd.DataFrame({"Cluster":range(len(communities)),"Nodes":[", ".join(comm) for comm in communities]}).to_csv(sep="\t", index=False, encoding="utf-8"))
            communities_data=pd.DataFrame({"Number of Communities":list(communities_modularity.values()),"Modularity":list(communities_modularity.keys())})
            figure=px.scatter(data_frame=communities_data,x="Number of Communities",y="Modularity", title="Modularity Trend in Different Communities Partitioning", template="ggplot2")
        elif method == "greedy_modularity_group":
            communities=nx.algorithms.community.greedy_modularity_communities(graph)
            table_header=[html.Thead(html.Tr([html.Th("Community"),html.Th("Nodes")]))]
            table_body=[]
            for n, community in enumerate(communities):
                table_body+=[html.Tr([html.Td(n+1), html.Td(", ".join(community))])]
            table=dbc.Table(table_header+[html.Tbody(table_body)], className="table table-hover", bordered=True, id=prefix+"_custom_clusters_table")
            href="data:text/csv;charset=utf-8,"+quote(pd.DataFrame({"Cluster":range(len(communities)),"Nodes":[", ".join(comm) for comm in communities]}).to_csv(sep="\t", index=False, encoding="utf-8"))
            clustering_data=pd.DataFrame({"Eigenvalue Number":range(len(evals)),"Eigenvalue":evals})
            figure = go.Figure()
            style={"display":"none"}
        figure.update_layout({"paper_bgcolor": "rgba(0, 0, 0, 0)", "modebar":{"bgcolor":"rgba(0, 0, 0, 0)","color":"silver","activecolor":"grey"}})
        return figure, table, href, style
    return custom_clustering_section

def toggle_view_clusters_callback(prefix):
    @app.callback(
        Output(prefix+"_custom_clusters_modal", "is_open"),
        [Input(prefix+"_view_clusters_open", "n_clicks"), Input(prefix+"_view_clusters_close", "n_clicks")],
        [State(prefix+"_custom_clusters_modal", "is_open")],
    )
    def toggle_view_clusters(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open
    return toggle_view_clusters

def fittings_callback(prefix, graph):
    @app.callback(
        Output(prefix+"_adv_degree_distribution_plot", "figure"),
        [
            Input(prefix+"_projection_xmin", "value"),
            Input(prefix+"_ER_xmin", "value")
        ]
    )
    def fittings(value,ERvalue):
        import powerlaw
        import warnings
        warnings.filterwarnings("ignore")
        K=dict(nx.get_node_attributes(graph,"Degree"))
        data=np.array([v for v in K.values() if v > 0])
        n=len(graph.nodes())
        p=len(graph.edges())/(n*(n-1)/2)
        ER=nx.fast_gnp_random_graph(n,p)
        ERK=dict(nx.degree(ER))
        ERdata=np.array([v for v in ERK.values() if v > 0])
        plot=go.Figure(layout={"title":{"text":"Node Degree Distribution","x":0.5, "xanchor": "center"},"xaxis":{"title_text":"Node degree, k", "type":"log"}, "yaxis":{"title_text":"Normalized Frequency of Nodes with degree k, n(k)", "type":"log"}, "template":"ggplot2"})
        yvalues=np.array([])
        for d,val,title,to_show in [[data,value,prefix.replace("_"," ").title(),"power_law"],[ERdata,ERvalue,"Erdős Rényi","stretched_exponential"]]:
            fitted=powerlaw.Fit(d, discrete=True, verbose=False, xmin=val)
            x,y=np.unique(d,return_counts=True)
            y=y/len(d)  # normalization on data higher than 0
            yvalues=np.concatenate([yvalues,y])
            plot.add_trace(go.Scatter(x=x,y=y, mode="markers", name=title))
            reduced=sorted([v for v in d if v>=val])
            scalefactor=len(d[d>=val])/len(d)
            for dist in ["power_law","lognormal","exponential","truncated_power_law","stretched_exponential","lognormal_positive"]:
                if dist != to_show:
                    visible="legendonly"
                else:
                    visible=True
                plot.add_trace(go.Scatter(x=reduced,y=getattr(fitted,dist).pdf(reduced)*scalefactor, mode="lines", name=title+" "+dist.replace("_"," ").title(), visible=visible))
        yrange=[np.log10(min(yvalues)*0.75),np.log10(max(yvalues)*1.25)]
        plot.update_layout({"paper_bgcolor": "rgba(0, 0, 0, 0)", "modebar":{"bgcolor":"rgba(0, 0, 0, 0)","color":"silver","activecolor":"grey"}, "legend":{"orientation":"h","yanchor":"top","y":-0.25, "xanchor":"center","x":0.5}, "yaxis":{"range":yrange}}) # for a transparent background but keeping modebar acceptable colors, "x":1.25
        return plot
    return fittings

def toggle_download_interactome_callback(prefix):
    @app.callback(
        Output(prefix+"_save_interactome_modal", "is_open"),
        [Input(prefix+"_save_interactome_open", "n_clicks"), Input(prefix+"_save_interactome_close", "n_clicks")],
        [State(prefix+"_save_interactome_modal", "is_open")],
    )
    def toggle_download_interactome(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open
    return toggle_download_interactome

def download_interactome_callback(prefix):
    @app.callback(
        [
            Output(prefix+"_download_interactome_button_href","download"),
            Output(prefix+"_download_interactome_button_href","href")
        ],
        [
            Input(prefix+"_save_interactome","value")
        ]
    )
    def download_interactome(ftype):
        if ftype:
            download="virus_host_interactome."+ftype
            href=app.get_asset_url("graphs/virus_host_interactome/"+download)
            return download,href
        else:
            return None, None
    return download_interactome

def build_callbacks(prefix,G,nodes,graph_properties_df,L,evals,evects,n_clusters,clusters,L_maj,evals_maj,evects_maj,n_clusters_maj,clusters_maj,girvan_newman,maj,girvan_newman_maj,communities_modularity,communities_modularity_maj,n_comm,n_comm_maj,atc_description):
    # collapse_headbar_callback()
    displayHoverNodeData_callback(prefix,G)
    group_highlighter_callback(prefix,nodes,maj)
    highlighter_callback(prefix,G,nodes,L,evals,evects,n_clusters,clusters,L_maj,evals_maj,evects_maj,n_clusters_maj,clusters_maj,girvan_newman,maj,girvan_newman_maj,n_comm,n_comm_maj,atc_description)
    get_selected_clustering_callback(prefix)
    custom_clustering_section_callback(prefix,G,evals,evects,evals_maj,evects_maj,girvan_newman,maj,girvan_newman_maj,communities_modularity,communities_modularity_maj)
    # get_img_callback(prefix,prefix)
    # download_graph_file_callback(prefix,prefix)
    download_graph_callback(prefix)
    toggle_download_graph_callback(prefix)
    toggle_help_callback(prefix)
    toggle_legend_callback(prefix)
    toggle_group_highlighter_callback(prefix)
    open_advanced_section(prefix)
    get_range_clusters_callback(prefix,G,maj,evals,evals_maj,n_clusters,n_clusters_maj,girvan_newman,girvan_newman_maj,n_comm,n_comm_maj)
    toggle_view_clusters_callback(prefix)
    inspected_table_callback(prefix)
    properties_table_callback(prefix,graph_properties_df,nodes)
    fittings_callback(prefix,G)
    toggle_download_interactome_callback(prefix)
    download_interactome_callback(prefix)
