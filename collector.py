import pandas as pd
import numpy as np
from tqdm import tqdm
import pubchempy as pubchem
from chembl_webresource_client.new_client import new_client as chembl
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import os
import pickle
import json
import itertools
import networkx as nx
from networkx.algorithms import bipartite
from networkx.algorithms.community import modularity

class drug():
    def __init__(self,name,accession_number):
        #set name
        self.name = name
        #set DrugBank accession number as ID
        self.id = accession_number
        self.ID = self.id
    def advanced_init(self, trials, done_proteins):
        """adds useful intel"""
        self.trials = trials["Identifiers"]
        self.trials_phases = trials["Phases"]
        self.trials_hrefs = trials["Identifiers Hrefs"]
        #set compound object
        self.__compound = pubchem.get_compounds(self.name,"name")[0] # if it throws an exception the drug is escluded because it isn't in PubChem compounds database
        self.complexity = self.__compound.complexity
        self.heavy_atoms = self.__compound.heavy_atom_count
        if self.heavy_atoms <=6:
            raise Exception("Less than 6 Heavy Atoms")
        try:
            self.smiles = self.__compound.isomeric_smiles
        except:
            try:#in this case accesses two times the drugbank webpage, it should be otimized
                url = "https://www.drugbank.ca/drugs/"+self.id
                response = requests.get(url)
                page = response.content
                soup = BeautifulSoup(page, "html5lib")
                self.smiles = soup.findAll("div",attrs={"class":"wrap"})[2].get_text()
            except:
                self.smiles="Not Available"
        if self.smiles != "Not Available":
            #set molecule object
            self.molecule=Chem.MolFromSmiles(self.smiles)
            # get Morgan Fingerprints as bit vector
            self.__info_fingerprint={}
            self.fingerprint = AllChem.GetMorganFingerprintAsBitVect(self.molecule,2,nBits=2048,bitInfo=self.__info_fingerprint)
        url="https://www.drugbank.ca/drugs/"+self.id
        response = requests.get(url)
        page = response.content
        soup = BeautifulSoup(page, "html5lib")
        atc_together=[a["href"].split("/")[-1] for dd in soup.findAll("dd", attrs = {"class":"col-xl-10 col-md-9 col-sm-8"}) for a in dd.findAll("a") if "/atc/" in a["href"]][::-1]
        if atc_together != []:
            atc_grouped=[atc_together[i-5:i] for i in range(5,len(atc_together)+1,5)]
            atc_codes={}
            for i in range(len(atc_grouped)):
                for n,code in enumerate(atc_grouped[i]):
                    try:
                        atc_codes[n+1].append(code)
                    except:
                        atc_codes[n+1]=[code]
        else:
            atc_codes={n:["Not Available"] for n in range(6)}
        atc_codes={key:list(set(value)) for key,value in atc_codes.items()}
        self.atc=atc_codes
        self.atc1=atc_codes[1]
        self.atc2=atc_codes[2]
        self.atc3=atc_codes[3]
        self.atc4=atc_codes[4]
        self.atc_identifier=atc_codes[5]
        self.__proteins={}
        added_proteins={}
        for kind in ["targets","enzymes","carriers","transporters"]:
            self.__proteins[kind]={}
            tables = soup.find("div", attrs = {"class":"bond-list-container %s"%kind})
            if tables:
                for tab in tables.findAll("a"):
                    if ("class" not in tab.attrs and "target" not in tab.attrs):
                        if tab.get_text() not in done_proteins:
                            try:
                                prot=protein("https://www.drugbank.ca"+tab["href"])
                                self.__proteins[kind][prot.name]=prot
                                added_proteins[prot.name]=prot
                            except:
                                pass
                        else:
                            self.__proteins[kind][tab.get_text()]=done_proteins[tab.get_text()]
        self.targets=self.__proteins["targets"]
        self.enzymes=self.__proteins["enzymes"]
        self.carriers=self.__proteins["carriers"]
        self.transporters=self.__proteins["transporters"]
        self.target_class=[prot.protein_class for prot in self.targets.values()]
        self.drug_interactions={}
        url="https://www.drugbank.ca/drugs/%s/drug_interactions.json?&start=0&length=100"%self.id
        response = requests.get(url)
        content=response.json()
        total=content["recordsTotal"]
        data=content["data"]
        for d in data:
            try:  # sometimes the a tag is missing
                dd=BeautifulSoup(d[0], "html5lib")
                drug_name=dd.text
                drug_id=dd.a["href"].split("/")[-1]
                self.drug_interactions[drug(drug_name,drug_id)]=d[1]
            except:
                pass
        n=100
        while n < total:
            url="https://www.drugbank.ca/drugs/%s/drug_interactions.json?&start=%d&length=100"%(self.id,n)
            response = requests.get(url)
            content=response.json()
            data=content["data"]
            for d in data:
                try:  # sometimes the a tag is missing
                    dd=BeautifulSoup(d[0], "html5lib")
                    drug_name=dd.text
                    drug_id=dd.a["href"].split("/")[-1]
                    self.drug_interactions[drug(drug_name,drug_id)]=d[1]
                except:
                    pass
            n+=100
        return self,added_proteins
    def update_trials(self, trials):
        self.trials = trials["Identifiers"]
        self.trials_phases = trials["Phases"]
        self.trials_hrefs = trials["Identifiers Hrefs"]
    def __str__(self):
        return "%s (%s)"%(self.name, self.id)
    #more functions shoud be added
    def summary(self):
        return pd.DataFrame({"ID":self.id,"SMILES":self.smiles,"ATC Code Level 1":[self.atc1],"ATC Code Level 2":[self.atc2],"ATC Code Level 3":[self.atc3],"ATC Code Level 4":[self.atc4],"ATC Identifier":[self.atc_identifier],"Targets":[[t.name for t in self.targets.values()]],"Enzymes":[[e.name for e in self.enzymes.values()]],"Carriers":[[c.name for c in self.carriers.values()]],"Transporters":[[t.name for t in self.transporters.values()]],"Target Class":[self.target_class],"Drug Interactions":[[d.name for d in self.drug_interactions]],"Trials":[self.trials],"Trials Phases":[self.trials_phases],"Trials Hrefs":[self.trials_hrefs]},index=[self.name])


class protein():
    def __init__(self,url):
        self.drugbank_url=url
        self.id = url.split("/")[-1]
        response = requests.get(url)
        page = response.content
        soup = BeautifulSoup(page, "html5lib")
        self.name = soup.find("h1").get_text()
        relations = soup.find('table', attrs = {'id':'target-relations'})
        self.gene=soup.findAll("dd",attrs={"class":"col-xl-10 col-md-9 col-sm-8"})[2].get_text()
        self.organism=soup.findAll("dd",attrs={"class":"col-xl-10 col-md-9 col-sm-8"})[3].get_text()
        self.location=soup.findAll("dd",attrs={"class":"col-xl-10 col-md-9 col-sm-8"})[13].get_text()
        self.drugs={}
        relations_dict=pd.read_html(str(relations))[0][["Name","DrugBank ID","Actions"]].set_index("Name").to_dict()
        for name in relations_dict["DrugBank ID"].keys():
            self.drugs[drug(name,relations_dict["DrugBank ID"][name])]=relations_dict["Actions"][name]
        #string interaction partners
        self.string_interaction_partners={}
        if self.organism == "Humans":
            try:
                string_url = "https://string-db.org/api/tsv-no-header/interaction_partners"
                params = {"identifiers" : self.gene, "species" : 9606, "required_score": 950, "caller_identity" : "COVID-19_Drugs_Networker"}
                response = requests.post(string_url, data=params)
                for line in response.text.strip().split("\n"):
                    line = line.strip().split("\t")
                    self.string_interaction_partners[line[3]]={"score":line[5],"string_id":line[1]}
            except:
                self.string_interaction_partners={}
        #get diseases
        self.diseases=[]
        if self.organism != "Humans":
            self.diseases.append(self.organism)
        else:
            try:
                disgenet_url="https://www.disgenet.org/api/gda/gene/%s?min_ei=1&type=group&format=tsv"%self.gene #min evidence index 1 (EI = 1 indicates that all the publications support the GDA)
                response=requests.get(disgenet_url)
                page=response.content
                soup = BeautifulSoup(page, "html5lib")
                lines=soup.find("body").get_text().split("\n")
                index=lines[0].split("\t").index("disease_name")
                self.diseases=[line.split("\t")[index] for line in lines[1:-1]]
            except:
                self.diseases=[]
        try:
            url="https://swissmodel.expasy.org/repository/uniprot/"+self.id
            response = requests.get(url)
            page = response.content
            soup = BeautifulSoup(page, "html5lib")
            table=soup.find("div", attrs={"id":"allmodelsDiv"}).find("table")
            pdbid=table.findAll("a")[0]["href"].split("/")[-1]
            if "template" in pdbid:#es check with https://swissmodel.expasy.org/repository/uniprot/K9N7C7
                pdbid=pdbid.split("=")[1][:-1]
            if "." in pdbid:#es check with https://swissmodel.expasy.org/repository/uniprot/Q02641
                pdbid=pdbid.split(".")[0]
            self.pdbid=pdbid.upper()
        except:
            self.pdbid="Not Available"
        try:
            self.__protein_classification=chembl.protein_class.get(chembl.target_component.get(accession=self.id)[0]["protein_classifications"][0]["protein_classification_id"])
        except:
            self.__protein_classification={'l1': None, 'l2': None, 'l3': None, 'l4': None, 'l5': None, 'l6': None, 'l7': None, 'l8': None, 'protein_class_id': 1}
        self.protein_class=self.__protein_classification["l1"] if (self.__protein_classification["l1"] and self.__protein_classification["l1"] != "Unclassified protein") else "Not Available"
        self.family=self.__protein_classification["l2"] if self.__protein_classification["l2"] else "Not Available"
    def summary(self):
        return pd.DataFrame({"Gene":self.gene,"ID":self.id,"PDBID":self.pdbid,"Organism":self.organism,"Protein Class":self.protein_class,"Protein Family":self.family,"Cellular Location":self.location,"STRING Interaction Partners":[list(self.string_interaction_partners.keys())],"Diseases":[self.diseases],"Drugs":[[d.name for d in self.drugs]],"drugbank_url":self.drugbank_url},index=[self.name])

def get_frequency(list):
  d={}
  for el in list:
    try:
      d[el]+=1
    except:
      d[el]=1
  return d

def stringify_list_attributes(graph):
    #converts all attributes of type list to string, in order to be able to save le graph also in gexf, gml and graphml formats
    graph=graph.copy()
    for node in graph.nodes():
        for attribute, val in graph.nodes[node].items():
            if isinstance(val,list) or isinstance(val,tuple):
                try:
                    val=", ".join(val)
                except:
                    val=", ".join([str(v) for v in val])
                graph.nodes[node][attribute]=val
    for edge in graph.edges():
        for attribute, val in graph.edges[edge].items():
            if isinstance(val,list) or isinstance(val,tuple):
                try:
                    val=", ".join(val)
                except:
                    val=", ".join([str(v) for v in val])
                graph.edges[edge][attribute]=val
    return graph

class collector():
    def __init__(self):
        self.drugs=[]
        self.excluded=[]
        self.__proteins={}
        self.added_new_drugs=False
        url = "https://www.drugbank.ca/covid-19"
        response = requests.get(url)
        page = response.content
        soup = BeautifulSoup(page, "html5lib")
        tables = soup.findAll('table', attrs = {'class':'table table-sm datatable dt-responsive'})
        experimental_unapproved_treatments=pd.read_html(str(tables[0]))[0]
        #potential_drug_targets=pd.read_html(str(tables[1]))[0]
        clinical_trials=pd.read_html(str(tables[2]))[0][["Drug", "Phase", "Identifier"]]
        clinical_trials.insert(len(clinical_trials.columns), "Identifier Href", [row.find_all("td")[-1].a["href"] for row in tables[2].find_all("tr")[1:]]) # retrieves and adds a columns with the clinical trials hrefs
        grouped_trials = clinical_trials.groupby(by=["Drug"])
        trials_info = {}
        for d in set(clinical_trials["Drug"]):
            group = grouped_trials.get_group(d)
            phase = list(group["Phase"])#{phase for phases in group["Phase"] for phase in phases.split(", ")}
            identifiers = list(group["Identifier"])
            hrefs = list(group["Identifier Href"])
            trials_info[d] = {"Phases":phase, "Identifiers":identifiers, "Identifiers Hrefs":hrefs}
        #clinical_trials_num=pd.read_html(str(tables[3]))[0]
        drug_tags=set([h for h in tables[0].findAll("a")+tables[2].findAll("a") if "/drugs/" in h["href"]])
        drug_ids = {d["href"].split("/")[-1] for d in drug_tags}
        if os.path.isfile("data/SARS-CoV-2_drug_database.pickle"):
            with open("data/SARS-CoV-2_drug_database.pickle","rb") as bkp:
                bkp_class=pickle.load(bkp)
            #self.drugs=bkp_class.drugs
            self.drugs=[]
            for d in bkp_class.drugs: # checks if drugs have been removed
                if d.id in drug_ids:
                    d.update_trials(trials_info.get(d.name, {"Phases":["Not Available"], "Identifiers":["Not Available"], "Identifiers Hrefs":["Not Available"]}))
                    self.drugs.append(d)
                else:
                    self.added_new_drugs=True #actually no, but this triggers the recalculation of the graph properties
            self.excluded=bkp_class.excluded
            self.__proteins=bkp_class._collector__proteins #do not change class name! (sure there is a more elegant way...)
            for d in tqdm(drug_tags):
                if d.get_text() not in [drug.name for drug in self.drugs]+self.excluded:
                    try:
                        temp_drug,added_proteins=drug(d.get_text(),(d["href"].split("/")[-1])).advanced_init(trials_info.get(d.get_text(), {"Phases":["Not Available"], "Identifiers":["Not Available"], "Identifiers Hrefs":["Not Available"]}), self.__proteins)
                        self.drugs.append(temp_drug)
                        self.__proteins.update(added_proteins)
                        if len(temp_drug.targets):
                            self.added_new_drugs=True
                    except:
                        self.excluded.append(d.get_text())
        else:
            self.added_new_drugs=True
            for d in tqdm(drug_tags):
                if d.get_text() not in [drug.name for drug in self.drugs]+self.excluded:
                    try:
                        temp_drug,added_proteins=drug(d.get_text(),(d["href"].split("/")[-1])).advanced_init(trials_info.get(d.get_text(), {"Phases":["Not Available"], "Identifiers":["Not Available"], "Identifiers Hrefs":["Not Available"]}), self.__proteins)
                        self.drugs.append(temp_drug)
                        self.__proteins.update(added_proteins)
                    except:
                        self.excluded.append(d.get_text())
        self.save()
    def save(self):
        with open("data/SARS-CoV-2_drug_database.pickle","wb") as bkp:
            pickle.dump(self,bkp)
    def summary(self,group):
        if group in ["drugs","targets"]:
            if group == "drugs":
                return pd.concat([drug.summary() for drug in self.drugs])
            elif group == "targets":
                return pd.concat([target.summary() for target in self.drugs])
    def graph_properties(self,graph):
        K=dict(nx.degree(graph))
        CC=dict(nx.closeness_centrality(graph))
        BC=dict(nx.betweenness_centrality(graph))
        EBC=dict(nx.edge_betweenness_centrality(graph))
        EC=dict(nx.eigenvector_centrality(graph,max_iter=1000))
        C=dict(nx.clustering(graph))
        VR=nx.voterank(graph)
        VRS={} #voterank score
        for node in graph.nodes():
            try:
                VRS[node]=len(VR)-VR.index(node)
            except:
                VRS[node]=0
        nx.set_node_attributes(graph,K,"Degree")
        nx.set_node_attributes(graph,CC,"Closeness Centrality")
        nx.set_node_attributes(graph,BC,"Betweenness Centrality")
        nx.set_node_attributes(graph,EBC,"Edge Betweenness Centrality")
        nx.set_node_attributes(graph,EC,"Eigenvector Centrality")
        nx.set_node_attributes(graph,C,"Clustering Coefficient")
        nx.set_node_attributes(graph,VRS,"VoteRank Score")
        return graph
    def save_graph(self,is_needed,df,graph,name):
        if is_needed:
            if not os.path.isdir("data/graphs/"+name):
                os.mkdir("data/graphs/"+name)
            df.to_csv("data/graphs/%s/%s.tsv"%(name,name),sep="\t")
            nx.write_gpickle(graph,"data/graphs/%s/%s.gpickle"%(name,name))
            nx.write_adjlist(graph,"data/graphs/%s/%s.adjlist"%(name,name),delimiter="\t")
            nx.write_multiline_adjlist(graph,"data/graphs/%s/%s.multiline_adjlist"%(name,name),delimiter="\t")
            nx.write_edgelist(graph,"data/graphs/%s/%s.edgelist"%(name,name),delimiter="\t")
            with open("data/graphs/%s/%s.cyjs"%(name,name),"w") as outfile:
                outfile.write(json.dumps(nx.cytoscape_data(graph), indent=2))
            graph=stringify_list_attributes(graph)
            nx.write_gexf(graph,"data/graphs/%s/%s.gexf"%(name,name))
            nx.write_graphml(graph,"data/graphs/%s/%s.graphml"%(name,name))
    def communities(self):
        print("Precomputing Girvan Newman Communities...")
        import ray
        try:
            ray.init()
        except:
            ray.shutdown()
            ray.init()

        @ray.remote
        def collect_GN_communities(graph,name):
            maj=graph.subgraph(max(list(nx.connected_components(graph)), key=len))
            nested_ids=[compute_GN_communities.remote(g) for g in [graph,maj]]
            results, maj_results=ray.get(nested_ids)
            print("\tGirvan Newman Communities Computed for %s"%name.replace("_"," ").title())
            return name, [r[i] for i in range(len(results)) for r in [results,maj_results]]

        @ray.remote
        def compute_GN_communities(graph):
            girvan_newman={len(comm):comm for comm in nx.algorithms.community.girvan_newman(graph)}
            communities_modularity={modularity(graph,community):n for n,community in girvan_newman.items()}
            n_comm=communities_modularity[max(communities_modularity)]
            return girvan_newman,communities_modularity,n_comm

        ids=[collect_GN_communities.remote(graph,name) for graph, name in [(self.__drugtarget,"drug_target"),(self.__drugdrug,"drug_projection"),(self.__targettarget,"target_projection")]]
        communities=ray.get(ids)
        print("\tCommunities Computed! Saving...")
        for name, data in communities:
            name="data/groups/"+name+"_communities.pickle"
            with open(name,"wb") as bkp:
                pickle.dump(data,bkp)
            if os.path.isfile(name+".bkp"):
                os.remove(name+".bkp")
        ray.shutdown()
    def spectral_clustering(self):
        print("\tSpectral Clustering Data Precomputing ...")
        from sklearn.cluster import KMeans
        from scipy.stats import halfnorm
        for graph, prefix in [(self.__drugtarget,"drug_target"),(self.__drugdrug,"drug_projection"),(self.__targettarget,"target_projection")]:
            maj=graph.subgraph(max(list(nx.connected_components(graph)), key=len))
            L=nx.normalized_laplacian_matrix(graph).toarray()
            evals,evects=np.linalg.eigh(L)
            relevant=[n for n,dif in enumerate(np.diff(evals)) if dif > halfnorm.ppf(0.99,*halfnorm.fit(np.diff(evals)))]
            relevant=[relevant[n] for n in range(len(relevant)-1) if relevant[n]+1 != relevant[n+1]]+[relevant[-1]] #keeps only the highest value if there are consecutive ones
            n_clusters=relevant[0]+1 if (relevant[0] > 1 and relevant[0]+1 != nx.number_connected_components(graph)) else relevant[1]+1
            km=KMeans(n_clusters=n_clusters, n_init=100)
            clusters=km.fit_predict(evects[:,:n_clusters])
            L_maj=nx.normalized_laplacian_matrix(maj).toarray()
            evals_maj,evects_maj=np.linalg.eigh(L_maj)
            relevant_maj=[n for n,dif in enumerate(np.diff(evals_maj)) if dif > halfnorm.ppf(0.99,*halfnorm.fit(np.diff(evals_maj)))]
            relevant_maj=[relevant_maj[n] for n in range(len(relevant_maj)-1) if relevant_maj[n]+1 != relevant_maj[n+1]]+[relevant_maj[-1]] #keeps only the highest value if there are consecutive ones
            n_clusters_maj=relevant_maj[0]+1 if (relevant_maj[0] > 1 and relevant_maj[0]+1 != nx.number_connected_components(maj)) else relevant_maj[1]+1
            km_maj=KMeans(n_clusters=n_clusters_maj, n_init=100)
            clusters_maj=km_maj.fit_predict(evects_maj[:,:n_clusters_maj])
            name="data/groups/"+prefix+"_spectral.pickle"
            with open(name,"wb") as bkp:
                pickle.dump([L,evals,evects,n_clusters,clusters,L_maj,evals_maj,evects_maj,n_clusters_maj,clusters_maj],bkp)
            if os.path.isfile(name+".bkp"):
                os.remove(name+".bkp")
    def similarity(self,sparse=True,save=True):
        self.similarities={drug1.name:{drug2.name:DataStructs.FingerprintSimilarity(drug1.fingerprint,drug2.fingerprint) for drug2 in self.drugs if drug2.fingerprint} for drug1 in self.drugs if drug1.fingerprint}
        df=pd.DataFrame(self.similarities)
        if sparse:
            df=pd.DataFrame([(drug1,drug2,df[drug1][drug2]) for drug1,drug2 in itertools.combinations(list(df),2) if df[drug1][drug2] != 0], columns=["Source","Target","Weight"])
            if filename:
                df.to_csv("data/graphs/similarity/similarity.tsv",sep="\t")
        elif save:
            df.to_csv("data/graphs/similarity/similarity.tsv",sep="\t")
        return df
    def chemicalspace(self,tab=False):
        self.similarities={drug1.name:{drug2.name:DataStructs.FingerprintSimilarity(drug1.fingerprint,drug2.fingerprint) for drug2 in self.drugs if drug2.fingerprint} for drug1 in self.drugs if drug1.fingerprint}
        df=pd.DataFrame(self.similarities)
        threshold=0.4
        df=pd.DataFrame([(drug1,drug2,df[drug1][drug2]) for drug1,drug2 in itertools.combinations(list(df),2) if df[drug1][drug2] > threshold], columns=["Source","Target","Weight"])
        drug_attributes={drug.name:(drug.summary().T.to_dict()[drug.name]) for drug in self.drugs}
        structures={mol.name:"https://www.drugbank.ca/structures/%s/image.svg"%mol.id for mol in self.drugs} # straight from drugbank

        G=nx.from_pandas_edgelist(df,source="Source",target="Target",edge_attr="Weight")
        nx.set_node_attributes(G,drug_attributes)
        nx.set_node_attributes(G,{node:node for node in G.nodes},"Name")
        nx.set_node_attributes(G,structures,"structure")
        nx.set_node_attributes(G,{node:"#FC5F67" for node in G.nodes()},"fill_color")
        nx.set_node_attributes(G,{node:"#CC6540" for node in G.nodes()},"line_color")
        self.graph_properties(G)
        self.__chemicalspace=G
        df.to_csv("data/graphs/chemicalspace/.tsv",sep="\t")
        nx.write_gpickle(G,"data/graphs/chemicalspace/chemicalspace.pickle")
    def drugtarget(self,tab=False):
        print("Building Drug-Target Network ...")
        drugtarget=[{"Drug":drug.name,"Target":target.name} for drug in self.drugs for target in drug.targets.values()]
        df=pd.DataFrame(drugtarget)
        drug_attributes={drug.name:(drug.summary().T.to_dict()[drug.name]) for drug in self.drugs}
        protein_attributes={target.name:(target.summary().T.to_dict()[target.name]) for target in self.__proteins.values() if target.name in set(df["Target"])}
        structures={mol.name:"https://www.drugbank.ca/structures/%s/image.svg"%mol.id for mol in self.drugs} # direttamente da drugbank
        for prot in tqdm(self.__proteins.values()):
            if prot.name in set(df["Target"]):
                url="https://cdn.rcsb.org/images/structures/%s/%s/%s_%s-1.jpeg"%(prot.pdbid[1:3].lower(),prot.pdbid.lower(),prot.pdbid.lower(),"assembly")
                if requests.head(url).status_code == 200:
                    structures.update({prot.name:url})
                else:
                    structures.update({prot.name:"https://cdn.rcsb.org/images/structures/%s/%s/%s_model-1.jpeg"%(prot.pdbid[1:3].lower(),prot.pdbid.lower(),prot.pdbid.lower())})

        G=nx.from_pandas_edgelist(df,source="Drug",target="Target")
        nx.set_node_attributes(G,drug_attributes)
        nx.set_node_attributes(G,protein_attributes)
        nx.set_node_attributes(G,{node:node for node in G.nodes},"Name")
        nx.set_node_attributes(G,structures,"structure")
        nx.set_node_attributes(G,{node:("Drug" if node in set(df["Drug"]) else "Target") for node in G.nodes()},"kind")
        self.graph_properties(G)
        #cosmetics
        nx.set_node_attributes(G,{node:("#FC5F67" if G.nodes[node]["kind"] == "Drug" else "#12EAEA") for node in G.nodes()},"fill_color")
        nx.set_node_attributes(G,{node:("#FB3640" if G.nodes[node]["kind"] == "Drug" else "#0EBEBE") for node in G.nodes()},"line_color")
        self.__drugtarget=G
        self.save_graph(self.added_new_drugs,df,G,"drug_target")
        self.save()
    def drugdrug(self,tab=False):
        print("Building Drug Projection ...")
        drug_attributes={drug.name:(drug.summary().T.to_dict()[drug.name]) for drug in self.drugs}
        structures={mol.name:"https://www.drugbank.ca/structures/%s/image.svg"%mol.id for mol in self.drugs} # direttamente da drugbank
        nodes=[d.name for d in self.drugs if d.targets != {}]
        G=bipartite.weighted_projected_graph(self.__drugtarget,nodes)
        self.graph_properties(G)
        self.__drugdrug=G
        df=nx.to_pandas_edgelist(G)
        self.save_graph(self.added_new_drugs,df,G,"drug_projection")
        self.save()
    def targettarget(self,tab=False):
        print("Building Target Projection ...")
        nodes=[t for d in self.drugs for t in d.targets]
        G=bipartite.weighted_projected_graph(self.__drugtarget,nodes)
        self.graph_properties(G)
        self.__targettarget=G
        df=nx.to_pandas_edgelist(G)
        self.save_graph(self.added_new_drugs,df,G,"target_projection")
        self.save()
    def targetinteractors(self,tab=False):
        targets_list=set([target for drug in self.drugs for target in drug.targets.values()])
        targetinteractors=[{"Source":source.gene,"Target":target,"Score":source.string_interaction_partners[target]["score"]} for source in targets_list for target in source.string_interaction_partners]
        df=pd.DataFrame(targetinteractors)
        protein_attributes={target.name:(target.summary().T.to_dict()[target.name]) for target in targets_list}
        G=nx.from_pandas_edgelist(df,source="Source",target="Target", edge_attr="Score")
        nx.set_node_attributes(G,protein_attributes)
        nx.set_node_attributes(G,{node:node for node in G.nodes},"gene")
        self.graph_properties(G)
        self.__targetinteractors=G
        self.save_graph(self.added_new_drugs,df,G,"target_interactors")
    def targetdiseases(self,tab=False):
        proteins_list=set([target for drug in self.drugs for target in drug.targets.values()])
        targetdiseases=[{"Source":protein.name,"Target":disease} for protein in proteins_list for disease in protein.diseases]
        df=pd.DataFrame(targetdiseases)
        protein_attributes={protein.name:(protein.summary().T.to_dict()[protein.name]) for protein in proteins_list}
        G=nx.from_pandas_edgelist(df,source="Source",target="Target")
        nx.set_node_attributes(G,protein_attributes)
        nx.set_node_attributes(G,{node:node for node in G.nodes},"name")
        nx.set_node_attributes(G,{node:("protein" if node in set(df["Source"]) else "disease") for node in G.nodes()},"kind")
        self.graph_properties(G)
        self.__targetdiseases=G
        self.save_graph(self.added_new_drugs,df,G,"target_diseases")
    def virus_host_interactome(self):
        print("Building Virus Host Interactome ...")
        from networkx.drawing.nx_agraph import graphviz_layout
        def replace_minor_components(graph, pos, scalefactor=1.25):
            components=list(nx.connected_components(graph))
            maj=max(components,key=len)
            #get viral proteins not in major component
            vnodes=[n for n in viral if n not in maj]
            vedges=[]
            # if more than one viral protein, create an edge between them
            for comp in components:
                if len([n for n in comp if n in vnodes])>1:
                    from itertools import product
                    tmp_edge=list(product([n for n in comp if n in vnodes]))
                    vedges.append((tmp_edge[0][0],tmp_edge[1][0]))
            V=nx.Graph()
            V.add_edges_from(vedges)
            V.add_nodes_from(vnodes)
            # spread viral proteins in a circle
            pvir=nx.circular_layout(V)
            # nx.draw(V, pos=nx.rescale_layout_dict(pvir,1.25), with_labels=True,alpha=0.5)
            for comp in components:
                if comp != maj:
                    centers=[v for v in V.nodes() if v in comp]
                    if len(centers)>1:
                        pcenter=(np.average([pvir[n][0] for n in centers]),np.average([pvir[n][1] for n in centers]))
                    else:
                        center=centers[0]
                        pcenter=pvir[center]
                    # compute layout for every single component
                    pcomp=nx.rescale_layout_dict(nx.kamada_kawai_layout(graph.subgraph(comp)),len(centers)**2/len(components))
                    for node in comp:
                        # reset position for every node in minor compoents on the basis of the circle created above
                        pos[node]=((pcomp[node][0]+pcenter[0])*scalefactor,(pcomp[node][1]+pcenter[1])*scalefactor)
                else:
                    #rescale positions also for major component
                    pcenter=(np.average([pos[n][0] for n in viral]),np.average([pos[n][1] for n in viral]))
                    # pcomp=nx.kamada_kawai_layout(graph.subgraph(comp))
                    pcomp=nx.rescale_layout_dict(graphviz_layout(graph.subgraph(comp), prog="neato", args="-Goverlap=scalexy"),1)
                    for node in comp:
                        pos[node]=(pcomp[node][0]+pcenter[0],pcomp[node][1]+pcenter[1])
            return pos
        chen_SFB_TAP=pd.read_excel("data/others/Chen_Interactions.xlsx",sheet_name=0, usecols=["Bait","Prey"], engine="openpyxl")
        chen_BioID2=pd.read_excel("data/others/Chen_Interactions.xlsx",sheet_name=1, usecols=["Bait","Prey"], engine="openpyxl")
        chen_SFB_TAP={(row[0],row[1]) for _,row in chen_SFB_TAP.iterrows()}
        chen_BioID2={(row[0],row[1]) for _,row in chen_BioID2.iterrows()}
        chen=chen_SFB_TAP.union(chen_BioID2)
        gordon=pd.read_excel("data/others/Gordon_Interactions.xlsx", header=1, usecols=["Bait","Preys","PreyGene"], engine="openpyxl")
        gordon={(row[0].replace("SARS-CoV2 ","").replace("orf","ORF").replace("nsp","NSP").replace("Spike","S").replace("NSP5_C145A","NSP5"),row[2]) for _,row in gordon.iterrows()}
        edges=chen.union(gordon)
        viral={e[0] for e in edges}
        human={e[1] for e in edges}
        targeted_genes=human.intersection(set(dict(nx.get_node_attributes(self.__targettarget,"Gene")).values()))
        drugs={}
        for name,node in self.__drugtarget.nodes(data=True):
            if node["kind"] == "Target":
                if node["Gene"] in human and name not in ["HCG20471, isoform CRA_c", "Glutathione peroxidase"]: #because they share the same gene name (SIGMAR1 and GPX1) with Sigma non-opioid intracellular receptor 1 and Glutathione Peroxidase 1 ## manually curation needed
                    drugs[node["Gene"]]=list(self.__drugtarget.neighbors(name))
        networker_edges={(source,target) for source,targets in drugs.items() for target in targets}
        edges=edges.union(networker_edges)
        drugs=[t for ts in drugs.values() for t in ts]
        G=nx.from_edgelist(edges)
        pos=nx.rescale_layout_dict(graphviz_layout(G, prog="neato", args="-Goverlap=scalexy"),1.1)
        pos=replace_minor_components(G,pos)
        nx.set_node_attributes(G,{node:node for node in G.nodes()},"Gene")
        nx.set_node_attributes(G,{node:True if node in viral else False for node in G.nodes()},"Viral")
        nx.set_node_attributes(G,{node:True if node in human else False for node in G.nodes()},"Human")
        nx.set_node_attributes(G,{node:True if node in targeted_genes else False for node in G.nodes()},"Targeted")
        nx.set_node_attributes(G,{node:True if node in drugs else False for node in G.nodes()},"Drug")
        nx.set_node_attributes(G,{node:pos[node] for node in G.nodes()},"pos")
        edge_source={}
        for edge in edges:
            source=[]
            for name,s in {"Chen_SFB_TAP":chen_SFB_TAP,"Chen_BioID2":chen_BioID2, "Gordon":gordon, "COVIDrugNet":networker_edges}.items():
                if edge in s:
                    source.append(name)
            edge_source[edge]=source
        nx.set_edge_attributes(G,edge_source,"Source")
        self.__virusHostInteractome=G
        self.save_graph(self.added_new_drugs,pd.DataFrame({"Source":e[0],"Target":e[1]} for e in edges),G,"virus_host_interactome")

if __name__ == "__main__":
    COVID_drugs=collector()

    # for debugging
    # url = "https://www.drugbank.ca/covid-19"
    # response = requests.get(url)
    # page = response.content
    # soup = BeautifulSoup(page, "html5lib")
    # tables = soup.findAll('table', attrs = {'class':'table table-sm datatable dt-responsive'})
    # clinical_trials=pd.read_html(str(tables[2]))[0][["Drug", "Phase", "Identifier"]]
    # clinical_trials.insert(len(clinical_trials.columns), "Identifier Href", [row.find_all("td")[-1].a["href"] for row in tables[2].find_all("tr")[1:]]) # retrieves and adds a columns with the clinical trials hrefs
    # grouped_trials = clinical_trials.groupby(by=["Drug"])
    # group = grouped_trials.get_group("Remdesivir")
    # phase = list(group["Phase"])#{phase for phases in group["Phase"] for phase in phases.split(", ")}
    # identifiers = list(group["Identifier"])
    # hrefs = list(group["Identifier Href"])
    # trials_info = {"Phases":phase, "Identifiers":identifiers, "Identifiers Hrefs":hrefs}
    # rem, pr=drug("Remdesivir","DB14761").advanced_init(trials_info,[])
    # print(COVID_drugs.excluded)

    # COVID_drugs.drugtarget()
    # COVID_drugs.drugdrug()
    # COVID_drugs.targettarget()

    if COVID_drugs.added_new_drugs:
        print("New drugs have been added, analyses should be re-runned.")
        # COVID_drugs.chemicalspace()
        COVID_drugs.drugtarget()
        COVID_drugs.drugdrug()
        COVID_drugs.targettarget()
        # COVID_drugs.targetinteractors()
        # COVID_drugs.targetdiseases()
        COVID_drugs.virus_host_interactome()
        for prefix in ["drug_target","drug_projection","target_projection"]:
            for group in ["communities","spectral"]:
                name="data/groups/"+prefix+"_"+group+".pickle"
                if os.path.isfile(name):
                    os.rename(name,name+".bkp")
        COVID_drugs.spectral_clustering()
        COVID_drugs.communities()
    print("Done!")
