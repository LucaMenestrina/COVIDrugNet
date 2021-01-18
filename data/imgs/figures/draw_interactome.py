import networkx as nx
import matplotlib.pyplot as plt

def draw_interactome_drugs():
    graph=nx.read_gpickle("../graphs/virus_host_interactome/virus_host_interactome.gpickle")
    pos=nx.get_node_attributes(graph,"pos")
    data={
        "Viral Genes":{
            "labels":[],
            "color":"#e74c3c",
            "shape":"D",
            "size":3
        },
        "Human Genes":{
            "labels":[],
            "color":"#3498db",
            "shape":"o",
            "size":2
        },
        "Targeted Genes":{
            "labels":[],
            "color":"#f5b041",
            "shape":"o",
            "size":1.5
        },
        "Drugs":{
            "labels":[],
            "color":"#28b463",
            "shape":"s",
            "size":2
        },
    }
    for node,node_data in graph.nodes(data=True):
        if node_data["Viral"]:
            data["Viral Genes"]["labels"].append(node_data["Gene"])
        elif node_data["Drug"]:
            data["Drugs"]["labels"].append(node_data["Gene"])
        elif node_data["Targeted"]:
            data["Targeted Genes"]["labels"].append(node_data["Gene"])
        else:
            data["Human Genes"]["labels"].append(node_data["Gene"])
    nx.draw_networkx_edges(graph, pos=pos, width=0.05)
    for kind in data.values():
        nx.draw_networkx_nodes(graph, pos=pos, nodelist=kind["labels"], node_shape=kind["shape"], node_size=kind["size"], node_color=kind["color"])
        nx.draw_networkx_labels(graph, pos=pos, labels={n:n for n in kind["labels"]}, font_size=0.1)
    plt.savefig("interactome_drugs.svg",bbox_inches="tight",pad_inches=0, transparent=True)
    plt.show()

draw_interactome_drugs()
