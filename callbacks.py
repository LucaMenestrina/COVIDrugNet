import dash
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

from app import app

cyto.load_extra_layouts()

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

def displayHoverNodeData_callback(prefix,G):
    @app.callback(
        [
            Output(prefix+"_title_card","children"),
            Output(prefix+"_img_card","src"),
            Output(prefix+"_attributes-list-card","children")
        ],
        [Input(prefix+"_graph", "mouseoverNodeData")]
    )
    def displayHoverNodeData(data):
        if not data:
            data={"id":"","structure":"","Properties":"Hover over a node to show its properties"}
            attributes=["id","Properties"]
            link_drugbank=""
            # if prefix == "dt" or prefix == "dd":
            #     data={key:value for key,value in G.nodes(data=True)["Remdesivir"].items()}
            #     print(data)
            # if prefix == "tt":
            #     data={key:value for key,value in G.nodes(data=True)["Angiotensin-converting enzyme 2"].items()}
        elif data["kind"]=="Drug":
            attributes=["ID","SMILES","ATC Code1","ATC Code5","Targets","Enzymes","Carriers","Transporters","Drug Interactions"]
            link_drugbank="https://www.drugbank.ca/drugs/"+data["ID"]
        else:
            attributes=["ID","Gene","PDBID","Organism","Cellular Location","String Interaction Partners","Drugs"]#,"Diseases"
            link_drugbank=data["drugbank_url"]

        attributes_list=[]
        for attribute in attributes:
            if data[attribute] != "" and data[attribute] != []:
                if attribute in ["ATC Code1","ATC Code5","Targets","Enzymes","Carriers","Transporters","Drug Interactions","String Interaction Partners","Drugs"]:
                    attributes_list.append(html.Li([html.Strong(attribute+": "),", ".join(data[attribute])], className="list-group-item"))
                elif attribute == "ID":
                    attributes_list.append(html.Li([html.Strong(attribute+": "),html.A(data[attribute], href=link_drugbank, target="_blank")], className="list-group-item"))
                elif attribute == "PDBID" and data[attribute] != "Not Available":
                    attributes_list.append(html.Li([html.Strong(attribute+": "),html.A(data[attribute], href="https://www.rcsb.org/structure/"+data[attribute], target="_blank")], className="list-group-item"))
                elif attribute == "Gene":
                    attributes_list.append(html.Li([html.Strong(attribute+": "),html.A(data[attribute], href="https://www.uniprot.org/uniprot/"+data["ID"], target="_blank")], className="list-group-item"))
                else:
                    attributes_list.append(html.Li([html.Strong(attribute+": "),data[attribute]], className="list-group-item"))
        return data["id"],data["structure"],attributes_list
    return displayHoverNodeData

def selectedTable_callback(prefix):
    @app.callback(
        [
            Output(prefix+"_selected_table","children"),
            Output(prefix+"_side_selected_table","active"),
            Output(prefix+"_side_selected_table","disabled")
        ],
        [Input(prefix+"_graph", "selectedNodeData")]
    )
    def selectedTable(data):
        if data:
            if len(data)>1:
                results=[]
                drugs_data=[d for d in data if d["kind"]=="Drug"]
                if len(drugs_data)>0:
                    attributes=["name","ID","ATC Code1","ATC Code5","SMILES","Targets","Enzymes","Carriers","Transporters","Drug Interactions"]
                    table_header=[html.Thead(html.Tr([html.Th(attribute) for attribute in ["Name","ID","ATC Code Level 1", "ATC Identifier", "SMILES","Targets","Enzymes","Carriers","Transporters","Drug Interactions"]]))]
                    table_body=[html.Tbody([html.Tr([html.Td(d[attribute]) if attribute in ["name","ID","SMILES"] else html.Td(", ".join(d[attribute])) for attribute in attributes]) for d in drugs_data])]
                    drugs_table=dbc.Table(table_header+table_body, className="table table-hover", bordered=True)
                    results+=[
                        html.Br(),
                        html.H3("Selected Drugs"),
                        drugs_table]
                targets_data=[d for d in data if d["kind"]=="Target"]
                if len(targets_data)>0:
                    attributes=["name","ID","Gene","PDBID","Organism","Cellular Location","String Interaction Partners","Drugs","Diseases"]
                    table_header=[html.Thead(html.Tr([html.Th(attribute) for attribute in ["Name","ID","Gene","PDBID","Organism","Cellular Location","String Interaction Partners","Drugs","Diseases"]]))]
                    table_body=[html.Tbody([html.Tr([html.Td(d[attribute]) if attribute not in ["String Interaction Partners","Drugs","Diseases"] else html.Td(", ".join(d[attribute])) for attribute in attributes]) for d in targets_data])]
                    targets_table=dbc.Table(table_header+table_body, className="table table-hover", bordered=True)
                    results+=[
                        html.Br(),
                        html.H3("Selected Targets"),
                        targets_table]

                return dbc.Container(results, fluid=True), True, False
            else:
                return None, False, True
        else:
            return None, False, True
    return selectedTable

def propertiesTable_callback(prefix,graph_properties_df):
    @app.callback(
        [
            Output(prefix+"_graph_properties_table_container","children"),
            Output(prefix+"_download_graph_properties","href")
        ],
        [
            Input(prefix+"_properties_table_sorting","value"),
            Input(prefix+"_properties_table_rows","value")
        ]
    )
    def propertiesTable(sorting,rows):
        sorting=sorting.split(",")
        sorting={"by":[sorting[0]],"ascending":bool(int(sorting[1]))}
        df=graph_properties_df.sort_values(**sorting)
        href="data:text/csv;charset=utf-8,"+quote(df.to_csv(sep="\t", index=False, encoding="utf-8"))
        if rows == "all":
            return dbc.Table.from_dataframe(df, bordered=True, className="table table-hover", id=prefix+"_graph_properties_table")
        else:
            df=df.head(rows)
            attributes=df.columns
            table_header=[html.Thead(html.Tr([html.Th(attribute) for attribute in ["Name", "Degree", "Closeness Centrality", "Betweenness Centrality"]]))]
            table_body=[html.Tbody([html.Tr([html.Td(d[attribute]) for attribute in attributes]) for d in df.to_dict("records")])]
            table=dbc.Table(table_header+table_body, className="table table-hover", bordered=True, id=prefix+"_graph_properties_table")
            return table,href
    return propertiesTable

def highlighter_callback(prefix,G,nodes, girvan_newman,maj,girvan_newman_maj):
    ##coloring precomputing
    L=nx.normalized_laplacian_matrix(G).toarray()
    evals,evects=np.linalg.eigh(L)
    # n_comp=[n for n,dif in enumerate(np.diff(evals)) if dif > 1.5*np.average(np.diff(evals))][0]+1
    n_comp=[n for n,dif in enumerate(np.diff(evals)) if dif > 1.5*np.average([d for d in np.diff([v for v in evals if v<1]) if d>0.00001])][0]+1
    # maj=G.subgraph(max(list(nx.connected_components(G)), key=len))
    L_maj=nx.normalized_laplacian_matrix(maj).toarray()
    evals_maj,evects_maj=np.linalg.eigh(L_maj)
    # n_maj=[n for n,dif in enumerate(np.diff(evals_maj)) if dif > 1.5*np.average(np.diff(evals_maj))][0]+1
    n_maj=[n for n,dif in enumerate(np.diff(evals_maj)) if dif > 1.5*np.average([d for d in np.diff([v for v in evals_maj if v<1]) if d>0.00001])][0]+1
    #components
    components=list(nx.connected_components(G))
    d_comp={}
    for n,comp in enumerate(components):
        d_comp.update({d:n for d in comp})
    name2id=dict(dict(nx.get_node_attributes(G,"ID")))
    cmap=dict(zip(set(d_comp.values()),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(components))]))
    id2component={name2id[node]:cmap.get(d_comp[node],"#708090") for node in G.nodes()}
    stylesheet_components=[]
    for ID in id2component:
        stylesheet_components.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2component[ID]}})
    pie_data=pd.DataFrame({"Component":range(1,len(components)+1),"Nodes":[len(component) for component in components]})
    pie_components=px.pie(pie_data,values="Nodes",names="Component", title="Components' Node Distribution",color_discrete_sequence=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(components))])
    legend_body_components=html.P("Nodes are colored on the corresponding component")
    #spectral
    km=KMeans(n_clusters=n_comp)
    clusters=km.fit_predict(evects[:,:n_comp])
    cmap=dict(zip(set(clusters),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/n_comp)]))
    id_cluster=dict(zip(dict(nx.get_node_attributes(G,"ID")).values(),clusters))
    stylesheet_spectral=[]
    for ID in id_cluster:
        stylesheet_spectral.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":cmap[id_cluster[ID]]}})
    pie_data=pd.DataFrame({"Cluster":range(1,len(set(clusters))+1),"Nodes":[list(clusters).count(cluster) for cluster in range(len(set(clusters)))]})
    pie_spectral=px.pie(pie_data,values="Nodes",names="Cluster", title="Clusters' Node Distribution",color_discrete_sequence=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(set(clusters)))])
    legend_body_spectral=html.P(["Nodes are colored on the corresponding cluster, check the ",html.A("clustering section", href="#dt_clustering")," for more info"])
    #spectral_maj
    km=KMeans(n_clusters=n_maj)
    clusters=km.fit_predict(evects_maj[:,:n_maj])
    cmap=dict(zip(set(clusters),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/n_maj)]))
    id_cluster=dict(zip(dict(nx.get_node_attributes(maj,"ID")).values(),clusters))
    stylesheet_spectral_maj=[]
    for ID in id_cluster:
        stylesheet_spectral_maj.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":cmap[id_cluster.get(ID,"#708090")]}})
    pie_data=pd.DataFrame({"Cluster":range(1,len(set(clusters))+1),"Nodes":[list(clusters).count(cluster) for cluster in range(len(set(clusters)))]})
    pie_spectral_maj=px.pie(pie_data,values="Nodes",names="Cluster", title="Clusters' Node Distribution",color_discrete_sequence=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(set(clusters)))])
    legend_body_spectral_maj=html.P(["Nodes are colored on the corresponding cluster, check the ",html.A("clustering section", href="#"+prefix+"_clustering")," for more info"])
    #girvan_newman
    # girvan_newman=nx.algorithms.community.girvan_newman(G)
    # communities = []
    # while len(communities) != n_comp:
    #     communities=next(girvan_newman)
    communities=girvan_newman[n_comp]
    d_comm={}
    for n,comm in enumerate(communities):
        d_comm.update({d:n for d in comm})
    name2id=dict(dict(nx.get_node_attributes(G,"ID")))
    cmap=dict(zip(set(d_comm.values()),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))]))
    id2community={name2id[node]:cmap.get(d_comm[node],"#708090") for node in G.nodes()}
    stylesheet_girvan_newman=[]
    for ID in id2community:
        stylesheet_girvan_newman.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2community[ID]}})
    pie_data=pd.DataFrame({"Community":range(1,len(communities)+1),"Nodes":[len(community) for community in communities]})
    pie_girvan_newman=px.pie(pie_data,values="Nodes",names="Community", title="Communities' Node Distribution",color_discrete_sequence=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))])
    legend_body_girvan_newman=html.P(["Nodes are colored on the corresponding community, check the ",html.A("clustering section", href="#"+prefix+"_clustering")," for more info"])
    #girvan_newman_maj
    # girvan_newman_maj=nx.algorithms.community.girvan_newman(maj)
    # communities = []
    # while len(communities) != n_maj:
    #     communities=next(girvan_newman_maj)
    communities=girvan_newman_maj[n_maj]
    d_comm={}
    for i,comm in enumerate(communities):
        d_comm.update({d:i for d in comm})
    name2id=dict(dict(nx.get_node_attributes(maj,"ID")))
    cmap=dict(zip(set(d_comm.values()),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))]))
    id2community={name2id[node]:cmap.get(d_comm[node],"#708090") for node in maj.nodes()}
    stylesheet_girvan_newman_maj=[]
    for ID in id2community:
        stylesheet_girvan_newman_maj.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2community.get(ID,"#708090")}})
    pie_data=pd.DataFrame({"Community":range(1,len(communities)+1),"Nodes":[len(community) for community in communities]})
    pie_girvan_newman_maj=px.pie(pie_data,values="Nodes",names="Community", title="Communities' Node Distribution",color_discrete_sequence=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))])
    legend_body_girvan_newman_maj=html.P(["Nodes are colored on the corresponding community, check the ",html.A("clustering section", href="#"+prefix+"_clustering")," for more info"])
    #greedy_modularity
    communities=nx.algorithms.community.greedy_modularity_communities(G)
    d_comm={}
    for i,comm in enumerate(communities):
        d_comm.update({d:i for d in comm})
    name2id=dict(dict(nx.get_node_attributes(G,"ID")))
    cmap=dict(zip(set(d_comm.values()),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))]))
    id2community={name2id[node]:cmap.get(d_comm[node],"#708090") for node in G.nodes()}
    stylesheet_greedy_modularity=[]
    for ID in id2community:
        stylesheet_greedy_modularity.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2community.get(ID,"#708090")}})
    pie_data=pd.DataFrame({"Community":range(1,len(communities)+1),"Nodes":[len(community) for community in communities]})
    pie_greedy_modularity=px.pie(pie_data,values="Nodes",names="Community", title="Communities' Node Distribution",color_discrete_sequence=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))])
    legend_body_greedy_modularity=html.P(["Nodes are colored on the corresponding community, check the ",html.A("clustering section", href="#"+prefix+"_clustering")," for more info"])
    #greedy_modularity_maj
    communities=nx.algorithms.community.greedy_modularity_communities(maj)
    d_comm={}
    for i,comm in enumerate(communities):
        d_comm.update({d:i for d in comm})
    name2id=dict(dict(nx.get_node_attributes(maj,"ID")))
    cmap=dict(zip(set(d_comm.values()),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))]))
    id2community={name2id[node]:cmap.get(d_comm[node],"#708090") for node in maj.nodes()}
    stylesheet_greedy_modularity_maj=[]
    for ID in id2community:
        stylesheet_greedy_modularity_maj.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2community.get(ID,"#708090")}})
    pie_data=pd.DataFrame({"Community":range(1,len(communities)+1),"Nodes":[len(community) for community in communities]})
    pie_greedy_modularity_maj=px.pie(pie_data,values="Nodes",names="Community", title="Communities' Node Distribution",color_discrete_sequence=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))])
    legend_body_greedy_modularity_maj=html.P(["Nodes are colored on the corresponding community, check the ",html.A("clustering section", href="#"+prefix+"_clustering")," for more info"])

    @app.callback(
        [
            Output(prefix+"_graph","stylesheet"),
            Output(prefix+"_piechart","figure"),
            Output(prefix+"_legend_popover_body","children")
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
            State(prefix+"_legend_popover_body","children")
        ]
    )
    def highlighter(highlighted,coloring,custom_method,custom_component,custom_n, current_stylesheet, current_pie, current_legend_body):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if changed_id != prefix+"_highlighter_dropdown.value":
            if coloring == "categorical":
                stylesheet=stylesheet_base.copy()
                pie_data=pd.DataFrame({"Kind":["Drugs","Targets"],"Nodes":[len([node for node,kind in G.nodes("kind") if kind == "Drug"]),len([node for node,kind in G.nodes("kind") if kind == "Target"])], "Color":["#12EAEA","#FC5F67"]})
                pie=px.pie(pie_data,values="Nodes",names="Kind", title="Drug-Target's Node Distribution",color_discrete_sequence=pie_data["Color"])
                legend_body=dbc.Table(html.Tbody([html.Tr([html.Td("",style={"background-color":"#FC5F67"}),html.Td("Drugs")]),html.Tr([html.Td("",style={"background-color":"#12EAEA"}),html.Td("Targets")])]), borderless=True, size="sm")
            if coloring == "atc":
                all_atc=["A","B","C","D","G","H","J","L","M","N","P","R","S","V"]
                long_atc={"A":"A: Alimentary tract and metabolism","B":"B: Blood and blood forming organs","C":"C: Cardiovascular system","D":"D: Dermatologicals","G":"G: Genito-urinary system and sex hormones","H":"H: Systemic hormonal preparations, excluding sex hormones and insulins","J":"J: Antiinfectives for systemic use","L":"L: Antineoplastic and immunomodulating agents","M":"M: Musculo-skeletal system","N":"N: Nervous system","P":"P: Antiparasitic products, insecticides and repellents","R":"R: Respiratory system","S":"S: Sensory organs","V":"V: Various","Not Available": "Not Available"}
                cmap=dict(zip(all_atc,[rgb2hex(plt.cm.Spectral(n)) for n in np.arange(0,1.1,1/14)]))
                cmap.update({"Not Available":"#708090"})
                atc2num={list(cmap.keys())[num]:str(num+1) for num in range(15)}
                stylesheets=[]
                for node in nodes:
                    stylesheet={"selector":"[ID = '"+node["data"]["ID"]+"']"}
                    style={"pie-size":"100%", "border-color":"#303633","border-width":2}
                    for atc in node["data"]["ATC Code1"]:
                        style.update({"pie-"+atc2num[atc]+"-background-color":cmap[atc],"pie-"+atc2num[atc]+"-background-size":100/len(node["data"]["ATC Code1"])})
                    stylesheet.update({"style":style})
                    stylesheets.append(stylesheet)
                ATC_dict=dict(nx.get_node_attributes(G,"ATC Code1"))
                ATC_count={}
                tot_codes=0
                for drug,atcs in ATC_dict.items():
                    for atc in atcs:
                        try:
                            ATC_count[atc]+=1/len(atcs)
                        except:
                            ATC_count[atc]=11/len(atcs)
                        tot_codes+=1
                stylesheet=stylesheets

                pie_data=pd.DataFrame({"ATC Code":list(ATC_count.keys()),"Value":list(ATC_count.values()), "Color":[cmap[code] for code in ATC_count.keys()], "Label":[long_atc[code] for code in ATC_count.keys()]}).sort_values(by="Value", ascending=False)
                pie=px.pie(pie_data,values="Value",names="Label", title="Drug-Target's Node Distribution",color_discrete_sequence=pie_data["Color"])
                table_body=[]
                for code in cmap:
                    table_body.append(html.Tr([html.Td("",style={"background-color":cmap[code]}),html.Td(long_atc[code])]))
                legend_body=dbc.Table(html.Tbody(table_body), borderless=True, size="sm")
            if coloring == "location":
                all_locations=list(set([node["data"]["Cellular_Location"] for node in nodes]))
                cmap=dict(zip(all_locations,[rgb2hex(plt.cm.Spectral(n)) for n in np.arange(0,1.1,1/len(all_locations))]))
                cmap.update({"Not Available":"#708090"})
                stylesheets=[]
                for node in nodes:
                    stylesheet={"selector":"[ID = '"+node["data"]["ID"]+"']"}
                    style={"background-color":cmap[node["data"]["Cellular_Location"]], "border-color":"#303633","border-width":2}
                    stylesheet.update({"style":style})
                    stylesheets.append(stylesheet)
                Location_dict=dict(nx.get_node_attributes(G,"Cellular Location"))
                Location_count={location:list(Location_dict.values()).count(location) for location in all_locations}
                stylesheet=stylesheets

                pie_data=pd.DataFrame({"Location":all_locations,"Value":list(Location_count.values()), "Color":[cmap[location] for location in all_locations]}).sort_values(by="Value", ascending=False)
                pie=px.pie(pie_data,values="Value",names="Location", title="Target-Target's Node Distribution",color_discrete_sequence=pie_data["Color"])
                table_body=[]
                for location in all_locations:
                    table_body.append(html.Tr([html.Td("",style={"background-color":cmap[location]}),html.Td(location)]))
                legend_body=dbc.Table(html.Tbody(table_body), borderless=True, size="sm")
            elif coloring == "components":
                stylesheet=stylesheet_components.copy()
                pie=pie_components
                legend_body=legend_body_components
            elif coloring == "spectral":
                stylesheet=stylesheet_spectral.copy()
                pie=pie_spectral
                legend_body=legend_body_spectral
            elif coloring == "spectral_maj":
                stylesheet=stylesheet_spectral_maj.copy()
                pie=pie_spectral_maj
                legend_body=legend_body_spectral_maj
            elif coloring == "girvan_newman":
                stylesheet=stylesheet_girvan_newman.copy()
                pie=pie_girvan_newman
                legend_body=legend_body_girvan_newman
            elif coloring == "girvan_newman_maj":
                stylesheet=stylesheet_girvan_newman_maj.copy()
                pie=pie_girvan_newman_maj
                legend_body=legend_body_girvan_newman_maj
            elif coloring == "greedy_modularity":
                stylesheet=stylesheet_greedy_modularity.copy()
                pie=pie_greedy_modularity
                legend_body=legend_body_greedy_modularity
            elif coloring == "greedy_modularity_maj":
                stylesheet=stylesheet_greedy_modularity_maj.copy()
                pie=pie_greedy_modularity_maj
                legend_body=legend_body_greedy_modularity_maj
            elif coloring == "custom":
                if custom_component=="maj":
                    # graph=G.subgraph(max(list(nx.connected_components(G)),key=len))
                    graph=maj.copy()
                    girvan_newman_custom=girvan_newman_maj
                    greedy_modularity_custom_stylesheet=stylesheet_greedy_modularity_maj.copy()
                    greedy_modularity_custom_pie=pie_greedy_modularity_maj
                else:
                    graph=G.copy()
                    girvan_newman_custom=girvan_newman
                    greedy_modularity_custom_stylesheet=stylesheet_greedy_modularity.copy()
                    greedy_modularity_custom_pie=pie_greedy_modularity
                if custom_method == "spectral":
                    L_custom=nx.normalized_laplacian_matrix(graph).toarray()
                    evals_custom,evects_custom=np.linalg.eigh(L_custom)
                    km_custom=KMeans(n_clusters=custom_n)
                    clusters_custom=km_custom.fit_predict(evects_custom[:,:custom_n])
                    cmap_custom=dict(zip(set(clusters_custom),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/custom_n)]))
                    id_cluster_custom=dict(zip(dict(nx.get_node_attributes(graph,"ID")).values(),clusters_custom))
                    stylesheet=[]
                    for ID in id_cluster_custom:
                        stylesheet.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":cmap_custom[id_cluster_custom[ID]]}})
                    pie_data=pd.DataFrame({"Cluster":range(1,len(set(clusters_custom))+1),"Nodes":[list(clusters_custom).count(cluster_custom) for cluster_custom in range(len(set(clusters_custom)))]})
                    pie=px.pie(pie_data,values="Nodes",names="Cluster", title="Clusters' Node Distribution",color_discrete_sequence=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(set(clusters_custom)))])
                elif custom_method == "girvan_newman":
                    # girvan_newman_custom=nx.algorithms.community.girvan_newman(graph)
                    # communities = []
                    # m=0
                    # while len(communities) != custom_n:
                    #     communities=girvan_newman_custom[m]
                    #     print(len(communities))
                    #     m+=1
                    communities=girvan_newman_custom[custom_n]
                    d_comm={}
                    for n,comm in enumerate(communities):
                        d_comm.update({d:n for d in comm})
                    name2id=dict(dict(nx.get_node_attributes(graph,"ID")))
                    cmap=dict(zip(set(d_comm.values()),[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/custom_n)]))
                    id2community={name2id[node]:cmap.get(d_comm[node],"#708090") for node in graph.nodes()}
                    stylesheet=[]
                    for ID in id2community:
                        stylesheet.append({"selector":"[ID = '"+ID+"']", "style":{"border-color":"#303633","border-width":2,"background-color":id2community.get(ID,"#708090")}})
                    pie_data=pd.DataFrame({"Community":range(1,len(communities)+1),"Nodes":[len(community) for community in communities]})
                    pie=px.pie(pie_data,values="Nodes",names="Community", title="Communities' Node Distribution",color_discrete_sequence=[rgb2hex(plt.cm.Spectral(i)) for i in np.arange(0,1.00001,1/len(communities))])
                elif custom_method == "greedy_modularity":
                    stylesheet=greedy_modularity_custom_stylesheet
                    pie=greedy_modularity_custom_pie

                legend_body=html.P(["Nodes are colored on the corresponding cluster/community, check the ",html.A("clustering section", href="#"+prefix+"_clustering")," for more info"])
        else:
            stylesheet=[style for style in current_stylesheet if style["style"].get("border-style") != "double"]
            pie=current_pie
            legend_body=current_legend_body
        if highlighted:
            for val in highlighted:
                stylesheet+=[
                    {
                        "selector":"[ID = '"+val+"']",
                        "style":{
                            # "background-color":"#FFE985",
                            "content":"data(id)",
                            # "font-size":24,
                            "border-style":"double",
                            "border-width":20,
                            "border-color":"#0ddfa6"
                        }
                    }
                ]
        stylesheet+=[{
            "selector":"node:selected",
            "style":{
                "background-color":"#FFE985",
                "border-color":"#FFDD4A",
                "border-width":4
            }
        }]
        return stylesheet, pie, legend_body
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
        Output(prefix+"_legend_popover", "is_open"),
        [Input(prefix+"_legend_open", "n_clicks")],
        [State(prefix+"_legend_popover", "is_open")],
    )
    def toggle_legend(n, is_open):
        if n:
            return not is_open
        return is_open
    return toggle_legend

def get_img_callback(prefix):
    @app.callback(
        Output(prefix+"_graph","generateImage"),
        [Input(prefix+"_download_graph_button","n_clicks")],
        [State(prefix+"_save_graph","value")]
    )
    def get_img(n_clicks,value):
        if value in ["svg", "png", "jpg"]:
            if n_clicks:
                return {"type":value,"action":"download"}
        else:
            return {"action":"store"}
    return get_img

def download_graph_file_callback(prefix,file_prefix):
    @app.callback(
        [
            Output(prefix+"_download_graph_button_href","download"),
            Output(prefix+"_download_graph_button_href","href")
        ],
        [Input(prefix+"_save_graph","value")]
    )
    def download_graph_file(value):
        if value not in ["svg", "png", "jpg"]:
            if value:
                download=file_prefix+"."+value
                # href="https://raw.githubusercontent.com/LucaMenestrina/programming_luca_menestrina/master/execises/align_score.py"
                href="https://raw.githubusercontent.com/LucaMenestrina/SARS-CoV-2_Networker/master/data/graphs/"+download
                return download, href
            else:
                return None,None
        else:
            return None,None
    return download_graph_file

# #### da controllare perchè non funziona
# def download_graph_callback(prefix,file_prefix):
#     @app.callback(
#         Output(prefix+"_download_graph_div","children"),
#         [Input(prefix+"_save_graph","value")]
#     )
#     def download_graph(value):
#         if value:
#             print("ok")
#             if value in ["svg", "png", "jpg"]:
#                 print("img")
#                 div=dbc.Button("Download", id=prefix+"_download_graph_button", className="ml-auto")
#                 get_img_callback(prefix)
#             else:
#                 print("file")
#                 div=html.A(dbc.Button("Download", id=prefix+"_download_graph_button_placeholder", className="ml-auto"), download=file_prefix+"."+value, href="https://drive.google.com/uc?export=view&id=1RMYDzIHpfsqYWMTd4qA2zWEWT0eYCAfd", id=prefix+"_download_graph_button_href")
#                 # download_graph_file_callback(prefix,file_prefix)
#         else:
#             div=dbc.Button("Download", id=prefix+"_download_graph_button", className="ml-auto", active=False)
#         return div
#     return download_graph

def get_range_clusters_callback(prefix,G,maj):
    @app.callback(
        [
            Output(prefix+"_custom_clustering_number_clusters","options"),
            Output(prefix+"_custom_clustering_number_clusters","value"),
            Output(prefix+"_custom_clustering_number_clusters","disabled"),
        ],
        [
            Input(prefix+"_custom_clustering_component","value"),
            Input(prefix+"_custom_clustering_method","value")
        ]
    )
    def get_range_clusters(component,method):
        if component=="maj":
            # graph=G.subgraph(max(list(nx.connected_components(G)), key=len))
            graph=maj.copy()
        else:
            graph=G.copy()
        if method == "greedy_modularity":
            n=len(nx.algorithms.community.greedy_modularity_communities(graph))
            options=[{"label":str(n),"value":n}]
            return options,n,True
        L=nx.normalized_laplacian_matrix(graph).toarray()
        evals,evects=np.linalg.eigh(L)
        n=[n for n,dif in enumerate(np.diff(evals)) if dif > 1.5*np.average([d for d in np.diff([v for v in evals if v<1]) if d>0.00001])][0]+1
        if method == "spectral":
            min_n=2
        elif nx.is_connected(graph):
            min_n=2
        else:
            min_n=nx.number_connected_components(graph)
        options=[{"label":str(n),"value":n} for n in range(min_n,len(evals)-1)]
        return options,n,False
    return get_range_clusters

def custom_clustering_section_callback(prefix,G,girvan_newman,maj,girvan_newman_maj):
    @app.callback(
        [
            Output(prefix+"_custom_clustering_graph","figure"),
            Output(prefix+"_custom_clusters_table_container","children"),
            Output(prefix+"_download_custom_clusters_modal","href")
        ],
        [
            Input(prefix+"_custom_clustering_component","value"),
            Input(prefix+"_custom_clustering_method","value"),
            Input(prefix+"_custom_clustering_number_clusters","value")
        ]
    )
    def custom_clustering_section(component, method, n_clusters):
        if component=="maj":
            # graph=G.subgraph(max(list(nx.connected_components(G)), key=len))
            graph=maj.copy()
            girvan_newman_custom=girvan_newman_maj
        else:
            graph=G.copy()
            girvan_newman_custom=girvan_newman
        L=nx.normalized_laplacian_matrix(graph).toarray()
        evals,evects=np.linalg.eigh(L)
        # n=[n for n,dif in enumerate(np.diff(evals)) if dif > 1.5*np.average(np.diff(evals))][0]+1
        clustering_data=pd.DataFrame({"Eigenvalue Number":range(len(evals)),"Eigenvalue":evals})
        figure=px.scatter(data_frame=clustering_data,x="Eigenvalue Number",y="Eigenvalue", title="Eigenvalues Distribution", height=600, width=800)
        if method == "spectral":
            km=KMeans(n_clusters=n_clusters)
            clusters=km.fit_predict(evects[:,:n_clusters])
            clusters_data={}
            for n,cl in enumerate(clusters):
                try:
                    clusters_data[cl].append(list(dict(graph.nodes("name")).values())[n])
                except:
                    clusters_data[cl]=[list(dict(graph.nodes("name")).values())[n]]
            clusters_data={n:", ".join(clusters_data[n]) for n in range(len(clusters_data))}
            table_header=[html.Thead(html.Tr([html.Th("Cluster"),html.Th("Nodes")]))]
            table_body=[]
            for cluster in clusters_data:
                table_body+=[html.Tr([html.Td(cluster), html.Td(clusters_data[cluster])])]
            table=dbc.Table(table_header+[html.Tbody(table_body)], className="table table-hover", bordered=True, id=prefix+"_custom_clusters_table")
            href="data:text/csv;charset=utf-8,"+quote(pd.DataFrame({"Cluster":list(clusters_data.keys()),"Nodes":list(clusters_data.values())}).to_csv(sep="\t", index=False, encoding="utf-8"))
        elif method == "girvan_newman":
            # girvan_newman=nx.algorithms.community.girvan_newman(graph)
            # communities = []
            # while len(communities) != n_clusters:
            #     communities=next(girvan_newman)
            communities=girvan_newman_custom[n_clusters]
            table_header=[html.Thead(html.Tr([html.Th("Community"),html.Th("Nodes")]))]
            table_body=[]
            for n, community in enumerate(communities):
                table_body+=[html.Tr([html.Td(n), html.Td(", ".join(community))])]
            table=dbc.Table(table_header+[html.Tbody(table_body)], className="table table-hover", bordered=True, id=prefix+"_custom_clusters_table")
            href="data:text/csv;charset=utf-8,"+quote(pd.DataFrame({"Cluster":range(len(communities)),"Nodes":[", ".join(comm) for comm in communities]}).to_csv(sep="\t", index=False, encoding="utf-8"))
        elif method == "greedy_modularity":
            communities=nx.algorithms.community.greedy_modularity_communities(graph)
            table_header=[html.Thead(html.Tr([html.Th("Community"),html.Th("Nodes")]))]
            table_body=[]
            for n, community in enumerate(communities):
                table_body+=[html.Tr([html.Td(n), html.Td(", ".join(community))])]
            table=dbc.Table(table_header+[html.Tbody(table_body)], className="table table-hover", bordered=True, id=prefix+"_custom_clusters_table")
            href="data:text/csv;charset=utf-8,"+quote(pd.DataFrame({"Cluster":range(len(communities)),"Nodes":[", ".join(comm) for comm in communities]}).to_csv(sep="\t", index=False, encoding="utf-8"))
        return figure, table, href
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

def build_callbacks(prefix,G,nodes,graph_properties_df,girvan_newman,maj,girvan_newman_maj,file_prefix):
    displayHoverNodeData_callback(prefix,G)
    selectedTable_callback(prefix)
    propertiesTable_callback(prefix,graph_properties_df)
    highlighter_callback(prefix,G,nodes, girvan_newman,maj,girvan_newman_maj)
    toggle_download_graph_callback(prefix)
    toggle_help_callback(prefix)
    toggle_legend_callback(prefix)
    get_img_callback(prefix)
    download_graph_file_callback(prefix,file_prefix)
    get_range_clusters_callback(prefix,G,maj)
    custom_clustering_section_callback(prefix,G,girvan_newman,maj,girvan_newman_maj)
    toggle_view_clusters_callback(prefix)
