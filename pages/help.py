import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from building_blocks import *
from callbacks import *


prefix="help"
print("Loading "+prefix.capitalize()+" ...")

#TABLES
nodes_header=[
    html.Thead(html.Tr([
        html.Th("Property"),
        html.Th("Description"),
        html.Th("Source")
    ]))
]
drugs_body=[
    html.Tbody([
        html.Tr([
            html.Td("ID"),
            html.Td("DrugBank unique identification code"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("SMILES"),
            html.Td("The chemical structure string notation for drugs. SMILES were recovered from PubChem if available, otherwise from Drugbank"),
            html.Td([html.A("Pubchem", href="https://pubchem.ncbi.nlm.nih.gov/", target="_blank"),", ",html.A("DrugBank", href="https://go.drugbank.com/", target="_blank")])
        ]),
        html.Tr([
            html.Td("ATC code level 1"),
            html.Td("The broad-based level of the ATC classification system identifying the fourteen anatomical/pharmacological groups"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("ATC identifier"),
            html.Td("ATC code"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("Targets"),
            html.Td("Entities to which the drug binds or interacts with, resulting in an alteration of their normal function and thus in desirable therapeutic effects or unwanted adverse effects"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("Enzymes"),
            html.Td("Proteins that facilitate a metabolic reaction that transforms the drug into one or more metabolites"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("Carriers"),
            html.Td("Proteins that bind to the drug and modify its pharmacokinetics, e.g., facilitating its transport in the blood stream or across cell membranes"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("Transporters"),
            html.Td("Proteins that move the drug across the cell membrane"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("Drug Interactions"),
            html.Td("Drugs that are known to interact, interfere or cause adverse reactions when taken with this drug"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("Trials"),
            html.Td("Identifiers of clinical trials with the respective phase"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
    ])
]
targets_body=[
    html.Tbody([
        html.Tr([
            html.Td("Gene"),
            html.Td("Short identifier of the unique gene name"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("Organism"),
            html.Td("Organism where the protein comes from"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("Cellular Location"),
            html.Td("The protein cellular location"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("Drugs"),
            html.Td("List of known drugs related with the protein (e.g., agonists, antagonists, inhibitors...)"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("ID"),
            html.Td("UniProt unique identification code"),
            html.Td(html.A("DrugBank", href="https://go.drugbank.com/", target="_blank"))
        ]),
        html.Tr([
            html.Td("STRING Interaction Partners"),
            html.Td("Known and predicted protein-protein interactions (both physical and functional) only in Homo Sapiens and with a minimum score of 0.95"),
            html.Td(html.A("STRING", href="https://string-db.org/", target="_blank"))
        ]),
        html.Tr([
            html.Td("Diseases"),
            html.Td(["Disease groups with an Evidence Index of 1 (see ",html.A("https://www.disgenet.org/dbinfo#section44", href="https://www.disgenet.org/dbinfo#section44", target="_blank")," for more information)"]),
            html.Td(html.A("DisGeNET", href="https://www.disgenet.org/", target="_blank"))
        ]),
        html.Tr([
            html.Td("PDBID"),
            html.Td("Protein Data Bank identification code (the structure with the best resolution)"),
            html.Td(html.A("SWISS-MODEL", href="https://swissmodel.expasy.org/", target="_blank"))
        ]),
        html.Tr([
            html.Td("Protein Classification"),
            html.Td("The first and the second level of Protein Target Classification are named Protein Class and Protein Family respectively"),
            html.Td(html.A("ChEMBL", href="https://www.ebi.ac.uk/chembl/", target="_blank"))
        ]),
    ])
]
graph_header=[
    html.Thead(html.Tr([
        html.Th("Property"),
        html.Th("Description")
    ]))
]
graph_body=[
    html.Tbody([
        html.Tr([
            html.Td("Degree"),
            html.Td("Number of edges of a node")
        ]),
        html.Tr([
            html.Td("Closeness Centrality"),
            html.Td("How close a node is to other nodes along the shortest path")
        ]),
        html.Tr([
            html.Td("Betweenness Centrality"),
            html.Td("Number of shortest paths passing through a node")
        ]),
        html.Tr([
            html.Td("Eigenvector Centrality"),
            html.Td("Measure of the node importance taking into account the importance of its neighbors")
        ]),
        html.Tr([
            html.Td("Clustering Coefficient"),
            html.Td("Measure of how close the neighbors of a node are to be fully connected")
        ]),
        html.Tr([
            html.Td("VoteRank Score"),
            html.Td([
                "Voterank is an iterative method to identify influential nodes in a network drawing up a ranking. ",
                "We translated this ranking into a score for each node on the basis of its position and the total number of nodes in the network with the following method:",
                html.Br(),
                html.Br(),
                html.Pre(["IF node in rank",html.Br(),"\tscore = length(rank) - index_in_rank(node)",html.Br(),"ELSE",html.Br(),"\tscore = 0"])
            ])
        ])
    ])
]

layout=dbc.Col([
            dbc.Row([
                dbc.Col(sidebar(prefix), width=1, className="bg-light"),
                dbc.Col([
                    html.Br(),
                    dbc.Col([
                        html.H2("Help"),
                        html.Br(),
                        html.Center([
                            html.Img(src=app.get_asset_url("imgs/help.svg"), style={"width":"100%"}, id=prefix+"_main")
                        ]),
                        html.Hr(),
                        html.Br(),
                        html.H4("In the pages relative to the projections, there are some small differences:"),
                        html.Br(),
                        html.H5("In the Charts and Plots Section the degree distribution is displayed", id=prefix+"_charts_and_plots"),
                        html.Center([
                            html.Img(src=app.get_asset_url("imgs/help_charts&plots.svg"), style={"width":"100%"})
                        ]),
                        html.Br(),
                        html.Br(),
                        html.H5("In the Advanced Tools Section the Degree Distribution can be inspected more thoroughly", id=prefix+"_advanced_degree_distribution"),
                        html.Center([
                            html.Img(src=app.get_asset_url("imgs/help_advDD.svg"), style={"width":"100%"})
                        ]),
                        html.Br(),
                        html.Hr(),
                        html.Br(),
                        html.H4("Glossary", id=prefix+"_glossary"),
                        html.Br(),
                        html.H5("Drugs Properties"),
                        html.Center(
                            dbc.Table(nodes_header+drugs_body, className="table table-hover", bordered=True, style={"width":"90%"}),
                        ),
                        html.Br(),
                        html.H5("Targets Properties"),
                        html.Center(
                            dbc.Table(nodes_header+targets_body, className="table table-hover", bordered=True, style={"width":"90%"}),
                        ),
                        html.Br(),
                        html.H5("Graph Properties"),
                        html.P(["All these properties are computed taking advantage of the Python package ",html.A("NetworkX", href="https://networkx.org/", target="_blank")]),
                        html.Center(
                            dbc.Table(graph_header+graph_body, className="table table-hover", bordered=True, style={"width":"66%"}),
                        ),
                        # table_header=[html.Thead(html.Tr([html.Th(attribute, style={"white-space": "nowrap"}) for attribute in ["Name","ID","ATC Level 1", "ATC Identifier", "SMILES","Targets","Enzymes","Carriers","Transporters","Drug Interactions"]]))]
                        # table_body=[]
                        # for drug in drugs_data:
                        #     row=[]
                        #     for attribute in attributes:
                        #         if attribute == "Name":
                        #             row.append(html.Td(drug["Name"]))
                        #         elif attribute == "ID":
                        #             row.append(html.Td(html.A(drug["ID"],href="https://www.drugbank.ca/drugs/"+drug["ID"], target="_blank")))
                        #         elif attribute == "SMILES":
                        #             row.append(html.Td(dbc.Container(drug["SMILES"], style={"max-height":"20vh","overflow-y":"auto", "padding":"0px"}, fluid=True), style={"min-width":"12vw","max-width":"20vw","word-break": "break-word","padding-right":"0px"}))
                        #         elif "ATC" in attribute:
                        #             row.append(html.Td(dbc.Container(", ".join(drug[attribute]), style={"max-height":"20vh","overflow-y":"auto","word-break": "break-word", "padding":"0px"}, fluid=True), style={"min-width":"7vw","max-width":"15vw","padding-right":"0px"}))
                        #         else:
                        #             row.append(html.Td(dbc.Container(", ".join(drug[attribute]), style={"max-height":"20vh","overflow-y":"auto","word-break": "break-word", "padding":"0px"}, fluid=True), style={"min-width":"10vw","max-width":"20vw","padding-right":"0px"}))
                        #     table_body.append(html.Tr(row))
                        # table_body=[html.Tbody(table_body)]
                        # drugs_table=dbc.Table(table_header+table_body, className="table table-hover", bordered=True)

                        # html.Br(),
                        # html.Br(),
                        # dbc.Row([
                        #     dbc.Col([
                        #         html.Center(html.H5([html.Font("If there still is something unclear feel free to "),html.A("reach us out", href="/contacts")], style={"margin":"0px"}))
                        #     ], className="card border-primary", width=5, align="center", style={"padding":"2%"})
                        # ], no_gutters=True, justify="center", align="center"),
                        ], style={"padding":"2%", "width":"100%"}),
                ]),
            ], no_gutters=True),
            html.Div(style={"height":"10vh"}),
            footer()
        ], style={"padding":"0px"})
