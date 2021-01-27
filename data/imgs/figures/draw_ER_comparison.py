import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import powerlaw

def draw_ER_comparison(file):
    graph=nx.read_gpickle("../../graphs/"+file+"/"+file+".gpickle")
    title=file.replace("_"," ").title()
    K=dict(nx.get_node_attributes(graph,"Degree"))
    # for projection data
    data=np.array(list(K.values()))
    fitted=powerlaw.Fit(data, discrete=True, verbose=False, xmin=1)
    x,y=np.unique(data,return_counts=True)
    y=y/len(data)
    plt.scatter(x=x,y=y, c="Tomato", alpha=0.6, label=title)
    # reducedx=sorted([v for v in data if v >= fitted.xmin])
    # plt.plot(reducedx,fitted.power_law.pdf(reducedx)*len(data[data>=fitted.xmin])/len(data),label=title+" Fitted Power Law", linewidth=0.75, c="Tomato")
    # for Erdős Rényi equivalent
    n=len(graph.nodes())
    p=len(graph.edges())/(n*(n-1)/2)
    ER=nx.fast_gnp_random_graph(n,p)
    ERK=dict(nx.degree(ER))
    ERdata=np.array(list(ERK.values()))
    ERfitted=powerlaw.Fit(ERdata, discrete=True, verbose=False, xmin=1)
    ERx,ERy=np.unique(ERdata,return_counts=True)
    ERy=ERy/len(ERdata)
    plt.scatter(x=ERx,y=ERy, c="DeepSkyBlue", alpha=0.6, label="Erdős Rényi Equivalent")
    # ERreducedx=sorted([v for v in ERdata if v >= ERfitted.xmin])
    # plt.plot(ERreducedx,ERfitted.stretched_exponential.pdf(ERreducedx)*len(ERdata[ERdata>=ERfitted.xmin])/len(ERdata),label="Erdős Rényi Equivalent Fitted Stretched Exponential", linewidth=0.75, c="DeepSkyBlue")
    plt.xlim([0.75, max(list(x)+list(ERx))*1.25])
    plt.ylim([min(list(y)+list(ERy))*0.75, max(list(y)+list(ERy))*1.25])
    plt.xscale("log")
    plt.yscale("log")
    plt.ylabel("Frequency of Nodes with degree k, n(k)")
    plt.xlabel("Degree, k")
    plt.title(title+" Degree Distribution")
    plt.legend(bbox_to_anchor=(0.8, -0.2))
    plt.savefig(file+"_degree_distribution.svg")
    plt.show()

for file in ["drug_projection","target_projection"]:
    draw_ER_comparison(file)
