import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
import json
import itertools
import networkx as nx
from networkx.algorithms import bipartite


import seaborn as sns

import ray

dt=nx.read_gpickle("../data/graphs/drug_target/drug_target.gpickle")
dd=nx.read_gpickle("../data/graphs/drug_projection/drug_projection.gpickle")
tt=nx.read_gpickle("../data/graphs/target_projection/target_projection.gpickle")



def clustering_coefficient_vs_degree(graph,order,title=""):
    cc=nx.clustering(graph)
    K=dict(nx.degree(graph))
    K_cleaned={node:K for node,K in K.items() if cc[node] != 0}
    cc_cleaned={node:cl for node,cl in dict(cc).items() if node in K_cleaned}
    plot=sns.regplot(x=list(K_cleaned.values()),y=list(cc_cleaned.values()), order=order)
    plot.set_title(title+" Clustering Coefficient VS Degree")
    plot.set_xlabel("Degree")
    plot.set_ylabel("Clustering Coefficient")
    plot.set_ylim(-0.05,1.05)
    if title:
        folder=title.replace(" ","_")
        plot.get_figure().savefig(folder+"/"+folder+"_clustering_coefficient_vs_degree.png",dpi=300)
    plt.clf()



try:
    ray.init()
except:
    ray.shutdown()
    ray.init()

def sort_dict(dictionary):
    d=dict(dictionary)
    l=[]
    for key in d.keys():
        l.append((d[key],key))
    l.sort(reverse=True)
    return l

def targeted_attack(graph):
    G=graph.copy()
    components=list(G.subgraph(component) for component in nx.connected_components(G))
    r={}
    K_s=sort_dict(nx.degree(G))
    n=0
    d=max(nx.diameter(component) for component in components)
    l=len(G.nodes())
    r[n]=(d,"",0)
    rel={0:d}
    # print("%d over %d, diameter: %d"%(n,len(G.nodes()),d),flush=True)
    nodes_removed=[""]
    fractions=[0]
    diameters=[d]
    while len(K_s)>=2:
        n+=1
        G.remove_node(K_s[0][1])
        K_s=sort_dict(nx.degree(G))
        components=list(G.subgraph(component) for component in nx.connected_components(G))
        d=max(nx.diameter(component) for component in components)
        r[n]=(d,K_s[0][1],K_s[0][0])
        print("%d over %d, diameter: %d"%(n,len(G.nodes()),d),flush=True)
        rel[n/l]=d
    df=pd.DataFrame({"Node removed":nodes_removed,"Fraction of nodes removed":fractions,"Diameter":diameters}) # da implementare per rendere più chiari i risultati
    return r,rel

@ray.remote
def random_attack(graph):
    G=graph.copy()
    components=list(G.subgraph(component) for component in nx.connected_components(G))
    r={}
    K_s=sort_dict(nx.degree(G))
    n=0
    d=max(nx.diameter(component) for component in components)
    l=len(G.nodes())
    r[n]=(d,"",0)
    rel={0:d}
    # print("%d over %d, diameter: %d"%(n,len(G.nodes()),d),flush=True)
    while len(K_s)>=2:
        n+=1
        nodes=G.nodes()
        random_node=list(nodes)[np.random.randint(len(nodes))]
        G.remove_node(random_node)
        K_s=sort_dict(nx.degree(G))
        components=list(G.subgraph(component) for component in nx.connected_components(G))
        d=max(nx.diameter(component) for component in components)
        r[n]=(d,random_node)#),K_s[[K_s.index(t) for t in K_s if random_node in t][0]][0])
        print("%d over %d, diameter: %d"%(n,len(G.nodes()),d),flush=True)
        rel[n/l]=d
    return r,rel

def attack_plot(relation_targeted,relation_random,title=""):
    x_t=[key for key in relation_targeted.keys()]
    y_t=list(relation_targeted.values())
    try:
        x_r=[key for key in relation_random.keys()]
        y_r=list(relation_random.values())
    except:
        x_r=[n/len(relation_random) for n in range(len(relation_random))]
        y_r=relation_random
    df=pd.concat([pd.DataFrame({"Fraction of nodes removed":x_t,"Network diameter":y_t,"Attack type":["Targeted" for x in x_t]}),pd.DataFrame({"Fraction of nodes removed":x_r,"Network diameter":y_r,"Attack type":["Random" for x in x_r]})])
    plot=sns.lineplot(x="Fraction of nodes removed", y="Network diameter", data=df, hue="Attack type")
    plt.title(title+" Robustness")
    if title:
        folder=title.replace(" ","_")
        plot.get_figure().savefig(folder+"/"+folder+"_robustness.png", dpi=300)
    plt.close()


def test_robustness(graph,title,iterations=100):
    folder=title.replace(" ","_")
    if not os.path.isdir(folder):
        os.mkdir(folder)
    targeted_diameter,relation_targeted=targeted_attack(graph)
    failures_ids=[]
    failures={}
    failures_ids=[random_attack.remote(graph) for i in range(iterations)]
    failures_list=ray.get(failures_ids)
    for i in range(0,iterations):
        relation=failures_list[i][1]
        failures[i]=relation
    percentages=list(failures[1].keys())
    avg_failure=np.mean(np.array([list(failures[n].values()) for n in failures.keys()]),axis=0)
    attack_plot(relation_targeted,avg_failure,title)
    with open(folder+"/"+folder+"_robustness_backup.pickle","wb") as bkp:
        pickle.dump({"relation_targeted":relation_targeted, "failures":failures, "avg_failure":avg_failure},bkp)




test_robustness(dd,"Drug Projection",100)
clustering_coefficient_vs_degree(dd,2,"Drug Projection")

test_robustness(tt,"Target Projection",100)
clustering_coefficient_vs_degree(tt,2,"Target Projection")






#same analysis removing Artenimol and Resveratrol

proteins_to_remove=[node for node in dt.neighbors("Artenimol") if (list(dt.neighbors(node)) == ["Artenimol"] or list(dt.neighbors(node)) == ["Artenimol","Fostamatinib"])]+[node for node in dt.neighbors("Fostamatinib") if (list(dt.neighbors(node)) == ["Fostamatinib"] or list(dt.neighbors(node)) == ["Artenimol","Fostamatinib"])]
dt_removed=dt.copy()
dt_removed.remove_nodes_from(["Artenimol","Fostamatinib"]+proteins_to_remove)
drugs=[node for node in dt_removed if (dt_removed.nodes()[node]["kind"]=="Drug" and dt_removed.nodes()[node]["Targets"] != [])]
dd_removed=bipartite.weighted_projected_graph(dt_removed,drugs)
targets=[node for node in dt_removed if dt_removed.nodes()[node]["kind"]=="Target"]
tt_removed=bipartite.weighted_projected_graph(dt_removed,targets)

clustering_coefficient_vs_degree(dd_removed,2,"Drug Projection Removed")
test_robustness(dd_removed,"Drug Projection Removed",100)

test_robustness(tt_removed,"Target Projection Removed",100)
clustering_coefficient_vs_degree(tt_removed,2,"Target Projection Removed")
