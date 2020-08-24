import pandas as pd
import numpy as np
from tqdm import tqdm
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs
import requests
from bs4 import BeautifulSoup
import seaborn as sns
import matplotlib.pyplot as plt
import os
import pickle
import itertools
import networkx as nx
from networkx.algorithms import bipartite

from bokeh.io import output_file
from bokeh.plotting import figure, from_networkx, save
from bokeh.models import Circle, MultiLine, PanTool, BoxZoomTool, WheelZoomTool, LassoSelectTool, UndoTool, RedoTool, ResetTool, SaveTool, HoverTool, TapTool, Panel, Tabs, Wedge, Legend, Row, Column, ColumnDataSource, Slider#(BoxSelectTool, Circle, EdgesAndLinkedNodes, HoverTool, MultiLine, NodesAndLinkedEdges, Plot, Range1d, TapTool,LassoSelectTool,WheelZoomTool)
from bokeh.models.widgets import DataTable, TableColumn
from math import sqrt,pi
from matplotlib.colors import rgb2hex
from bokeh.transform import cumsum

class drug():
    def __init__(self,name,accession_number):
        #set name
        self.name = name
        #set DrugBank accession number as ID
        self.id = accession_number
        self.ID = self.id
    def advanced_init(self,done_proteins):
        """adds useful intel for drugs related with covid"""
        #set compound object
        self.__compound = pcp.get_compounds(self.name,"name")[0]
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
                soup = BeautifulSoup(page, 'html5lib')
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
        soup = BeautifulSoup(page, 'html5lib')
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
        self.atc5=atc_codes[5]
        self.__proteins={}
        added_proteins={}
        for kind in ["targets","enzymes","carriers","transporters"]:
            self.__proteins[kind]={}
            try:
                tables = soup.find("div", attrs = {"class":"bond-list-container %s"%kind})
                for tab in tables.findAll("a"):
                    if ("class" not in tab.attrs and "target" not in tab.attrs):
                        if tab.get_text() not in done_proteins:
                            prot=protein(tab.get_text(),"https://www.drugbank.ca"+tab["href"])
                            self.__proteins[kind][tab.get_text()]=prot
                            added_proteins[tab.get_text()]=prot
                        else:
                            self.__proteins[kind][tab.get_text()]=done_proteins[tab.get_text()]
            except:
                self.__proteins[kind]={}
        self.targets=self.__proteins["targets"]
        self.enzymes=self.__proteins["enzymes"]
        self.carriers=self.__proteins["carriers"]
        self.transporters=self.__proteins["transporters"]
        #drug interactions
        interactions = soup.find('table', attrs = {'id':'drug-interactions'})
        if interactions != None:
            temp_int_names=[tag.get_text() for tag in interactions.findAll("a")]
            temp_int_ids=[tag["href"].split("/")[-1] for tag in interactions.findAll("a")]
            temp_int_description=[tag.get_text() for tag in interactions.findAll("td") if tag.get_text() not in temp_int_names]
            self.drug_interactions={drug(temp_int_names[i],temp_int_ids[i]):temp_int_description[i] for i in range(len(temp_int_names))}
        else:
            self.drug_interactions={}
        return self,added_proteins
    def __str__(self):
        return "%s (%s)"%(self.name, self.id)
    #aggiungere tutte le funzioni per avere in automatico alcune proprietà delle liste
    def summary(self):
        return pd.DataFrame({"ID":self.id,"SMILES":self.smiles,"ATC_Code1":[self.atc1],"ATC_Code5":[self.atc5],"Targets":", ".join([t.name for t in self.targets.values()]),"Enzymes":", ".join([e.name for e in self.enzymes.values()]),"Carriers":", ".join([c.name for c in self.carriers.values()]),"Transporters":", ".join([t.name for t in self.transporters.values()]),"Drug_Interactions":", ".join([d.name for d in self.drug_interactions])},index=[self.name])


class protein():
    def __init__(self,name,url):
        self.name = name
        self.drugbank_url=url
        self.id = url.split("/")[-1]
        response = requests.get(url)
        page = response.content
        soup = BeautifulSoup(page, 'html5lib')
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
                params = {"identifiers" : self.gene, "species" : 9606, "required_score": 950, "caller_identity" : "COVID-19_Networker"} #il caller_identity cambierà
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
                soup = BeautifulSoup(page, 'html5lib')
                lines=soup.find("body").get_text().split("\n")
                index=lines[0].split("\t").index("disease_name")
                self.diseases=[line.split("\t")[index] for line in lines[1:-1]]
            except:
                self.diseases=[]
        try:
            url="https://swissmodel.expasy.org/repository/uniprot/"+self.id
            response = requests.get(url)
            page = response.content
            soup = BeautifulSoup(page, 'html5lib')
            table=soup.find("table",attrs={"class":"table table-condensed table-striped table-hover tablesorter allStructuresList"})
            pdbid=table.findAll("a")[0]["href"].split("/")[-1]
            if "template" in pdbid:
                pdbid=pdbid.split("=")[-1][:-1]
            self.pdbid=pdbid.upper()
        except:
            self.pdbid="Not Available"
    def summary(self):
        return pd.DataFrame({"Gene":self.gene,"ID":self.id,"PDBID":self.pdbid,"Organism":self.organism,"Cellular_Location":self.location,"String_Interaction_Partners":", ".join(self.string_interaction_partners.keys()),"Diseases":", ".join(self.diseases),"Drugs":", ".join([d.name for d in self.drugs]),"drugbank_url":self.drugbank_url},index=[self.name])

def jaccard_index(list1,list2):
    union=set(list1+list2)
    if len(union)==0:
        return 0
    intersection=[el for el in list1 if el in list2]
    return len(intersection)/len(union)

def get_frequency(list):
  d={}
  for el in list:
    try:
      d[el]+=1
    except:
      d[el]=1
  return d

class collector():
    def __init__(self):
        self.drugs=[]
        self.excluded=[]
        self.__proteins={}
        url = "https://www.drugbank.ca/covid-19"
        response = requests.get(url)
        page = response.content
        soup = BeautifulSoup(page, 'html5lib')
        tables = soup.findAll('table', attrs = {'class':'table table-sm datatable dt-responsive'})
        experimental_unapproved_treatments=pd.read_html(str(tables[0]))[0]
        #potential_drug_targets=pd.read_html(str(tables[1]))[0]
        clinical_trials=pd.read_html(str(tables[2]))[0]
        #clinical_trials_num=pd.read_html(str(tables[3]))[0]
        drug_tags=set([h for h in tables[0].findAll("a")+tables[2].findAll("a") if "/drugs/" in h["href"]])
        if os.path.isfile("SARS-CoV-2_drug_database.pkl"):
            with open("SARS-CoV-2_drug_database.pkl","rb") as bkp:
                bkp_class=pickle.load(bkp)
            self.drugs=bkp_class.drugs
            self.excluded=bkp_class.excluded
            self.__proteins=bkp_class._collector__proteins #da modificare quando cambierò il nome della classe
            for d in tqdm(drug_tags):
                if d.get_text() not in [drug.name for drug in self.drugs]+self.excluded:
                    try:
                        temp_drug,added_proteins=drug(d.get_text(),(d["href"].split("/")[-1])).advanced_init(self.__proteins)
                        self.drugs.append(temp_drug)
                        self.__proteins.update(added_proteins)
                    except:
                        self.excluded.append(d.get_text())
        else:
            for d in tqdm(drug_tags):
                if d.get_text() not in [drug.name for drug in self.drugs]:
                    try:
                        temp_drug,added_proteins=drug(d.get_text(),(d["href"].split("/")[-1])).advanced_init(self.__proteins)
                        self.drugs.append(temp_drug)
                        self.__proteins.update(added_proteins)
                    except:
                        self.excluded.append(d.get_text())
        with open("SARS-CoV-2_drug_database.pkl","wb") as bkp:
            pickle.dump(self,bkp)
    def summary(self,group):
        if group in ["drugs","targets"]:
            if group == "drugs":
                return pd.concat([drug.summary() for drug in self.drugs])
            elif group == "targets":
                return pd.concat([target.summary() for target in self.drugs])
    def similarity(self,sparse=True,save=True):
        self.similarities={drug1.name:{drug2.name:DataStructs.FingerprintSimilarity(drug1.fingerprint,drug2.fingerprint) for drug2 in self.drugs if drug2.fingerprint} for drug1 in self.drugs if drug1.fingerprint}
        df=pd.DataFrame(self.similarities)
        if sparse:
            df=pd.DataFrame([(drug1,drug2,df[drug1][drug2]) for drug1,drug2 in itertools.combinations(list(df),2) if df[drug1][drug2] != 0], columns=["Source","Target","Weight"])
            if filename:
                df.to_csv("data/similarity.tsv",sep="\t")
        elif save:
            df.to_csv("data/similarity.tsv",sep="\t")
        return df
    def chemicalspace(self,tab=False):
        self.similarities={drug1.name:{drug2.name:DataStructs.FingerprintSimilarity(drug1.fingerprint,drug2.fingerprint) for drug2 in self.drugs if drug2.fingerprint} for drug1 in self.drugs if drug1.fingerprint}
        df=pd.DataFrame(self.similarities)
        threshold=0.4
        df=pd.DataFrame([(drug1,drug2,df[drug1][drug2]) for drug1,drug2 in itertools.combinations(list(df),2) if df[drug1][drug2] > threshold], columns=["Source","Target","Weight"])
        drug_attributes={drug.name:(drug.summary().T.to_dict()[drug.name]) for drug in self.drugs}
        structures={mol.name:"https://www.drugbank.ca/structures/%s/image.svg"%mol.id for mol in self.drugs} # direttamente da drugbank

        G=nx.from_pandas_edgelist(df,source="Source",target="Target",edge_attr="Weight")
        nx.set_node_attributes(G,drug_attributes)
        nx.set_node_attributes(G,{node:node for node in G.nodes},"name")
        nx.set_node_attributes(G,structures,"structure")
        nx.set_node_attributes(G,{node:"#FC5F67" for node in G.nodes()},"fill_color")
        nx.set_node_attributes(G,{node:"#CC6540" for node in G.nodes()},"line_color") #idem
        K=dict(nx.degree(G))
        nx.set_node_attributes(G,K,"degree")
        df.to_csv("data/chemicalspace.tsv",sep="\t")
        nx.write_gpickle(G,"data/chemicalspace.pickle")
    def drugtarget(self,tab=False):
        drugtarget=[{"Drug":drug.name,"Target":target.name} for drug in self.drugs for target in drug.targets.values()]
        df=pd.DataFrame(drugtarget)
        drug_attributes={drug.name:(drug.summary().T.to_dict()[drug.name]) for drug in self.drugs}
        protein_attributes={target.name:(target.summary().T.to_dict()[target.name]) for target in self.__proteins.values() if target.name in set(df["Target"])}
        structures={mol.name:"https://www.drugbank.ca/structures/%s/image.svg"%mol.id for mol in self.drugs} # direttamente da drugbank
        structures.update({prot.name:"https://cdn.rcsb.org/images/structures/%s/%s/%s_assembly-1.jpeg"%(prot.pdbid[1:3],prot.pdbid,prot.pdbid) for prot in self.__proteins.values() if prot.name in set(df["Target"])})

        G=nx.from_pandas_edgelist(df,source="Drug",target="Target")
        nx.set_node_attributes(G,drug_attributes)
        nx.set_node_attributes(G,protein_attributes)
        nx.set_node_attributes(G,{node:node for node in G.nodes},"name")
        nx.set_node_attributes(G,structures,"structure")
        nx.set_node_attributes(G,{node:("Drug" if node in set(df["Drug"]) else "Target") for node in G.nodes()},"kind")
        #cosmetics
        nx.set_node_attributes(G,{node:("#FC5F67" if G.nodes[node]["kind"] == "Drug" else "#12EAEA") for node in G.nodes()},"fill_color")
        nx.set_node_attributes(G,{node:("#FB3640" if G.nodes[node]["kind"] == "Drug" else "#0EBEBE") for node in G.nodes()},"line_color")
        df.to_csv("data/drugtarget.tsv",sep="\t")
        nx.write_gpickle(G,"data/drug_target.pickle")
    def drugdrug(self,tab=False):
        drug_attributes={drug.name:(drug.summary().T.to_dict()[drug.name]) for drug in self.drugs}
        structures={mol.name:"https://www.drugbank.ca/structures/%s/image.svg"%mol.id for mol in self.drugs} # direttamente da drugbank
        nodes=[d.name for d in self.drugs if d.targets != {}]
        G=bipartite.weighted_projected_graph(self.__drugtarget,nodes)
        df=nx.to_pandas_edgelist(G)
        df.to_csv("data/drugdrug.tsv",sep="\t")
        nx.write_gpickle(G,"data/drug_drug.pickle")
    def targettarget(self,tab=False):
        nodes=[t for d in self.drugs for t in d.targets]
        G=bipartite.weighted_projected_graph(self.__drugtarget,nodes)
        df=nx.to_pandas_edgelist(G)
        df.to_csv("data/targettarget.tsv",sep="\t")
        nx.write_gpickle(G,"data/target_target.pickle")
    def targetinteractors(self,tab=False):
        targets_list=set([target for drug in self.drugs for target in drug.targets.values()])
        targetinteractors=[{"Source":source.gene,"Target":target,"Score":source.string_interaction_partners[target]["score"]} for source in targets_list for target in source.string_interaction_partners]
        df=pd.DataFrame(targetinteractors)
        protein_attributes={target.name:(target.summary().T.to_dict()[target.name]) for target in targets_list}

        G=nx.from_pandas_edgelist(df,source="Source",target="Target", edge_attr="Score")
        nx.set_node_attributes(G,protein_attributes)
        nx.set_node_attributes(G,{node:node for node in G.nodes},"gene")
        df.to_csv("data/targetinteractors.tsv",sep="\t")
        nx.write_gpickle(G,"data/target_interactors.pickle")
    def targetdiseases(self,tab=False):
        proteins_list=set([target for drug in self.drugs for target in drug.targets.values()])
        targetdiseases=[{"Source":protein.name,"Target":disease} for protein in proteins_list for disease in protein.diseases]
        df=pd.DataFrame(targetdiseases)
        protein_attributes={protein.name:(protein.summary().T.to_dict()[protein.name]) for protein in proteins_list}
        G=nx.from_pandas_edgelist(df,source="Source",target="Target")
        nx.set_node_attributes(G,protein_attributes)
        nx.set_node_attributes(G,{node:node for node in G.nodes},"name")
        nx.set_node_attributes(G,{node:("protein" if node in set(df["Source"]) else "disease") for node in G.nodes()},"kind")
        df.to_csv("data/targetdiseases.tsv",sep="\t")
        nx.write_gpickle(G,"data/drug_disease.pickle")


COVID_drugs=collector()

# for debugging
# rem=drug("Remdesivir","DB14761").advanced_init([])


COVID_drugs.chemicalspace()
COVID_drugs.drugtarget()
COVID_drugs.drugdrug()
COVID_drugs.targettarget()
COVID_drugs.targetinteractors()
COVID_drugs.targetdiseases()
