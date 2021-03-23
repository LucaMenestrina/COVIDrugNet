import pandas as pd
import numpy as np
import networkx as nx
from networkx.algorithms import bipartite
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import scipy as sp
from tqdm import tqdm
import powerlaw
import json
import pickle
import os

import ray
from time import time
from datetime import timedelta



dt=nx.read_gpickle("../data/graphs/drug_target/drug_target.gpickle")
dd=nx.read_gpickle("../data/graphs/drug_projection/drug_projection.gpickle")
tt=nx.read_gpickle("../data/graphs/target_projection/target_projection.gpickle")

dd_degree=nx.get_node_attributes(dd,"Degree")
observed_dd=np.array(list(dd_degree.values()))

tt_degree=nx.get_node_attributes(tt,"Degree")
observed_tt=np.array(list(tt_degree.values()))


try:
    ray.init()
except:
    ray.shutdown()
    ray.init()

@ray.remote
def onesample(data):
    """sample for semi-parametric bootstrap"""
    fitted=powerlaw.Fit(data, discrete=True, verbose=False)
    xmin=getattr(fitted,"power_law").xmin
    lower=[n for n in data if n<xmin]
    lower_sample=np.random.choice(lower, len(lower), replace=True)
    upper_sample=getattr(fitted,"power_law").generate_random(n=len(data)-len(lower))
    sample=np.concatenate((lower_sample,upper_sample))
    result=powerlaw.Fit(sample, discrete=True, verbose=False)#, xmin=xmin
    return {"D":getattr(result,"power_law").D, "xmin":getattr(result,"power_law").xmin, "alpha":getattr(result,"power_law").alpha}

@ray.remote
def naivesample(data):
    """sample for case resampling bootstrap"""
    sample=np.random.choice(data, len(data), replace=True)
    result=powerlaw.Fit(sample, discrete=True, verbose=False)#, xmin=xmin
    return {"D":getattr(result,"power_law").D, "xmin":getattr(result,"power_law").xmin, "alpha":getattr(result,"power_law").alpha}

def minmax(l):
    mean=np.mean(l)
    std=np.std(l)
    l=[n for n in l if (mean-5*std<n<mean+5*std)]
    return min(l),max(l)

def fittings_plot(data, folder=""):
    """plots the degree distribution with the possible functions fitted"""
    fitted=powerlaw.Fit(data, discrete=True, verbose=False)
    x,y=np.unique(data,return_counts=True)
    y=y/len(data)#)/len(data[data>=fitted.xmin])
    plt.scatter(x=x,y=y, c="darkgray", alpha=0.6)
    reducedx=sorted([v for v in data if v >= fitted.xmin])
    # ydata=fitted.pdf(reducedx)#*len(data[data>=fitted.xmin])/len(data)
    xpdf,ypdf=fitted.pdf(original_data=False)
    xpdf=(xpdf[1:]+xpdf[:-1])/2.0
    ypdf=ypdf*len(data[data>=fitted.xmin])/len(data)
    plt.plot(xpdf,ypdf,label="PDF", linewidth=0.75)
    for dist in ["power_law","truncated_power_law","exponential","stretched_exponential","lognormal"]:
        plt.plot(reducedx,getattr(fitted,dist).pdf(reducedx)*len(data[data>=fitted.xmin])/len(data),label=dist.replace("_"," ").title(), linewidth=0.75)
    plt.xlim((0.75,max(x)*1.25))
    plt.ylim((min(y)*0.75,max(y)*1.25))
    plt.xscale("log")
    plt.yscale("log")
    plt.ylabel("Frequency")#("Normalized Probability")
    plt.xlabel("Degree")
    plt.title("Degree Distribution Fittings")
    plt.legend()
    if folder:
        plt.savefig(folder+"/"+folder+"_distribution_fittings.png", dpi=400)
    plt.close()

def estimate(data, parms, percentile, samples, title):
    """evaluate the fitting computing the p-value of D, xmin and alpha"""
    fig, axs = plt.subplots(nrows=3,ncols=4, figsize=(20,15))
    fig.suptitle(title.title())
    results_collection={}
    null_distributions={}
    for func in [onesample.remote, naivesample.remote]:
        if func == naivesample.remote:
            parm_to_bootstrap=["alpha", "xmin"]
        else:
            parm_to_bootstrap=["D"]
        replicates_ids=[func(data) for i in range(int(samples))]
        replicates_collection=ray.get(replicates_ids)
        replicates_collection={parm:[l[parm] for l in replicates_collection] for parm in parm_to_bootstrap}
        for parm in parm_to_bootstrap:
            pos=["alpha", "xmin", "D"].index(parm)
            replicates=replicates_collection[parm]
            std=np.std(replicates)
            estimated=np.mean(replicates)
            p=len([n for n in replicates if n >= parms[parm]])/len(replicates)
            CI=np.percentile(np.sort(replicates), [((1-percentile)/2)*100,(percentile+(1-percentile)/2)*100]).tolist()
            axs[pos,0].plot([n/(i+1) for i,n in enumerate(np.cumsum(replicates))])
            # axs[pos,0].set_xscale("log")
            axs[pos,0].set_title("Cumulative Mean of "+parm)
            axs[pos,0].set_xlabel("Iterations")
            axs[pos,0].set_ylabel("Mean")

            axs[pos,1].plot([np.std(replicates[:i+2]) for i in range(len(replicates))])
            # axs[pos,1].set_xscale("log")
            axs[pos,1].set_title("Cumulative Standard Deviation of "+parm)
            axs[pos,1].set_xlabel("Iterations")
            axs[pos,1].set_ylabel("Standard Deviation")

            axs[pos,2].plot([n/(i+1) for i,n in enumerate(np.cumsum([len([n for n in replicates[:ind] if n >= parms[parm]])/len(replicates[:ind]) for ind in range(1,len(replicates))]))])
            # axs[pos,2].set_xscale("log")
            axs[pos,2].set_title("Cumulative Mean of the p-value relative to "+parm)
            axs[pos,2].set_xlabel("Iterations")
            axs[pos,2].set_ylabel("p-value")

            significant_figures=int(-np.floor(np.log10(abs(np.mean(data)/10**3))))
            axs[pos,3].hist(replicates, bins=int(len(set([round(n,significant_figures) for n in replicates]))), density=True)
            sns.kdeplot(replicates, ax=axs[pos,3], color="lightblue", label="KDE")
            axs[pos,3].axvspan(0,np.percentile(np.sort(replicates),90), alpha=0.15, color="green", label="Acceptable Values")
            axs[pos,3].axvline(parms[parm], color="red", label="Observed value")
            axs[pos,3].axvline(np.percentile(np.sort(replicates),90), color="green", linestyle="--")#, label="0.10 p value acceptance threshold"
            axs[pos,3].legend()#loc="upper center", bbox_to_anchor=(0.5, 0)
            axs[pos,3].set_title("Replicates distribution (%s)"%parm)
            axs[pos,3].set_xlabel(parm)
            axs[pos,3].set_ylabel("Frequency")
            axs[pos,3].set_xlim(minmax(replicates))#CI[0]-3*std, CI[1]+3*std #[min(replicates),max(replicates)]
            results_collection[parm]={"estimated":estimated,"CI":CI,"pvalue":p}
            null_distributions[parm]=replicates
        folder=title.replace(" ","_")
        fig.savefig(folder+"/"+folder+"_fitting_multiplot.png", dpi=400)
        # fig.show()
        plt.close()

    return results_collection, null_distributions

def test_distribution(data,title,percentile=0.90, samples=1E5):
    """main function to fit some functions on the distribution and evaluate the fittings"""
    start=time()
    folder=title.replace(" ","_")
    if not os.path.isdir(folder):
        os.mkdir(folder)
    results=powerlaw.Fit(data, discrete=True, verbose=False)
    alpha=getattr(results,"power_law").alpha
    xmin=getattr(results,"power_law").xmin
    fitted_D=getattr(results,"power_law").D

    parms={"xmin":xmin, "alpha": alpha, "D":fitted_D}
    percentage=round(len([n for n in data if n >= xmin])/len(data)*100,2)
    observed={"alpha":alpha, "xmin":xmin, "D":fitted_D, "percentage":percentage}
    comparisons={alternative:dict(zip(["likelihood-ratio","pvalue"],results.distribution_compare("power_law", alternative))) for alternative in ["truncated_power_law","exponential","stretched_exponential","lognormal"]}
    # comparisons={}
    if percentile>=1:
        percentile/=100
    bootstrapped, null_distributions=estimate(data, parms, percentile, samples, title)
    fitting_analysis={"observed":observed, "comparisons":comparisons, "bootstrap":bootstrapped}
    with open(folder+"/"+folder+"_fitting_analysis.json","w") as outfile:
        outfile.write(json.dumps(fitting_analysis, indent=4))
    with open(folder+"/"+folder+"_null_distributions.pickle","wb") as outfile:
        pickle.dump(fitting_analysis, outfile)
    fittings_plot(data,folder)
    print("Test runtime %sh %sm %ss"%tuple(str(timedelta(seconds=(time()-start))).split(":")))
    #return fitting_analysis

def ER_equivalent(graph, title, samples=1E5):
    """builds and test an equivalent (same number of nodes and probability of edge creation) Erdős Rényi (random) graph"""
    if not os.path.isdir("ER_equivalents"):
        os.mkdir("ER_equivalents")
    os.chdir("ER_equivalents")
    n=len(graph.nodes())
    p=len(graph.edges())/(n*(n-1)/2)
    ER=nx.fast_gnp_random_graph(n,p)
    ERK=dict(nx.degree(ER))
    # observed_K=np.array(list(ERK.values()))
    observed_K=np.array([n for n in ERK.values() if n > 0])
    test_distribution(observed_K,samples=samples, title=title+" ER equivalent")
    os.chdir("../")

test_distribution(observed_dd, samples=1E5, title="Drug Projection")
# fittings_plot(observed_dd,"Drug_Projection")
# ER_equivalent(dd,"Drug Projection")

test_distribution(observed_tt,samples=1E5, title="Target Projection")
# fittings_plot(observed_tt,"Target_Projection")
# ER_equivalent(tt,"Target Projection")




#same analysis removing Artenimol and Resveratrol and their exclusive direct neighbors

proteins_to_remove=[node for node in dt.neighbors("Artenimol") if (list(dt.neighbors(node)) == ["Artenimol"] or list(dt.neighbors(node)) == ["Artenimol","Fostamatinib"])]+[node for node in dt.neighbors("Fostamatinib") if (list(dt.neighbors(node)) == ["Fostamatinib"] or list(dt.neighbors(node)) == ["Artenimol","Fostamatinib"])]
dt_removed=dt.copy()
dt_removed.remove_nodes_from(["Artenimol","Fostamatinib"]+proteins_to_remove)
drugs=[node for node in dt_removed if (dt_removed.nodes()[node]["kind"]=="Drug" and dt_removed.nodes()[node]["Targets"] != [])]
dd_removed=bipartite.weighted_projected_graph(dt_removed,drugs)
targets=[node for node in dt_removed if dt_removed.nodes()[node]["kind"]=="Target"]
tt_removed=bipartite.weighted_projected_graph(dt_removed,targets)
dd_removed_degree=nx.get_node_attributes(dd_removed,"Degree")
observed_dd_removed=np.array(list(dd_removed_degree.values()))
tt_removed_degree=nx.get_node_attributes(tt_removed,"Degree")
observed_tt_removed=np.array(list(tt_removed_degree.values()))

test_distribution(observed_dd_removed, samples=1E5, title="Drug Projection Removed")
# fittings_plot(observed_dd_removed,"Drug_Projection_Removed")
# ER_equivalent(dd_removed,"Drug Projection Removed")

test_distribution(observed_tt_removed,samples=1E5, title="Target Projection Removed")
# fittings_plot(observed_tt_removed,"Target_Projection_Removed")
# ER_equivalent(tt_removed,"Target Projection Removed")



# #for method validation
#
# def barabasi_albert(title="Barabasi Albert", samples=1E5, nedges=2):
#     """builds and tests a set of Barabasi Albert networks (with 1000 nodes)"""
#     BA=nx.barabasi_albert_graph(n=1000,m=nedges,seed=1).to_undirected()
#     BAK=dict(nx.degree(BA))
#     # observed_K=np.array(list(ERK.values()))
#     observed_K=np.array([n for n in BAK.values() if n > 0])
#     test_distribution(observed_K,samples=samples, title=title+" m "+str(nedges))
#
# if not os.path.isdir("method_validation"):
#     os.mkdir("method_validation")
# os.chdir("method_validation")
# files = os.listdir('.')
# for file in ["words.txt","worm.txt","blackouts.txt"]:
#     if file not in files:
#         import urllib.request
#         urllib.request.urlretrieve("https://raw.github.com/jeffalstott/powerlaw/master/manuscript/"+file, file)
#     test_distribution(np.genfromtxt(file), samples=1E5, title=file.split(".")[0]) #for method validation
# if not os.path.isdir("Barabasi_Albert"):
#     os.mkdir("Barabasi_Albert")
# os.chdir("Barabasi_Albert")
# for nedges in [1,2,3,4,5,7,10,15]:
#     barabasi_albert(nedges=nedges)

ray.shutdown()
