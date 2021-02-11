import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import numpy as np
import pickle

def draw_ATC_barchart(file):
    graph=nx.read_gpickle("../../graphs/drug_projection/drug_projection.gpickle")
    ATC_dict=dict(nx.get_node_attributes(graph,"ATC Code Level 1"))
    all_atc=["A","B","C","D","G","H","J","L","M","N","P","R","S","V"]
    cmap=dict(zip(all_atc,[rgb2hex(plt.cm.Spectral(n)) for n in np.arange(0,1.1,1/14)])) # not necessary but uses the same colors of the Drug Projection (webtool and other figures)
    cmap.update({"Not Available":"#708090"})
    with open("../../others/atc_description.pickle", "rb") as bkp:
        atc_description=pickle.load(bkp)
    tmp_atc_values=[l for ll in ATC_dict.values() for l in ll]
    ATC_count={atc:tmp_atc_values.count(atc) for atc in cmap.keys()}
    ATC_count={k: v for k, v in sorted(ATC_count.items(), key=lambda item: item[1], reverse=True)}#sort by value
    for code,value in ATC_count.items():
        plt.bar(x=code,height=value, color=cmap[code], label=code, alpha=0.9, align="center")
        plt.text(x=code, y=value+0.5, s=str(value), horizontalalignment="center", fontsize="small")
    title=file.replace("_"," ").title()
    plt.ylabel("Number of Nodes")
    # plt.xlabel("First Level ATC Code")
    plt.xticks(rotation=-45)
    plt.tick_params(axis="x", length=0)
    plt.title(title)
    # plt.legend(bbox_to_anchor=(1.05,1.025))
    plt.savefig(file+".svg", bbox_inches="tight")
    plt.show()

draw_ATC_barchart("first_level_ATC_code_distribution")
