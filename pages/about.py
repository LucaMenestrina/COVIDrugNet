import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from building_blocks import *
from callbacks import *


prefix="about"
print("Loading "+prefix.capitalize()+" ...")

layout=dbc.Col([
            dbc.Col([
                html.Br(),
                dbc.Col([
                    html.H3("About the Project"),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(
                            html.A(
                                dbc.Row([
                                    #da controllare se abbiamo i diritti per farlo e soprattutto va aggiornata a quella del mese corretto
                                    dbc.Col([html.Img(src="https://onlinelibrary.wiley.com/cms/asset/16546dbe-aa48-47b1-8aa1-217fa352966f/minf202081001-toc-0001-m.jpg", style={"width":"100%"})], align="center", sm=5, lg=4 ,xl=3),
                                    dbc.Col([
                                        html.H4(html.Strong("Titolo")),
                                        html.H5("Autori"),
                                        html.Br(),
                                        html.P("Info, Jurnal, Pages, ...."),
                                        html.P("Ovviamente è solo un concept temporaneo e poi andrà tutto adattato in base a preprint, giornale, diritti d'immagine e bla bla bla..."),
                                        html.A("doi", href=""),
                                    ], align="start", sm=7, lg=8 ,xl=9)
                                ], justify="around", align="center"),
                            href="", target="_blank", style={"color":"black"}),
                        align="center", sm=12, md=6),
                        dbc.Col([
                            html.P([html.Font("TEMPORANEO",style={"color":"red"})," The outbreak of the COVID-19 pandemic caused by SARS-CoV-2 at the beginning of 2020 has shocked the population worldwide. The scientific community has promptly put in place a great effort to help countering the spread of the virus. Here, we present a web application, the COVID-19 Drugs Networker (http://compmedchem.unibo.it/covidrugnet), that allows a network-based analysis of the DrugBank dataset of potential repurposed drugs currently in clinical trial. The freely accessible application automatically collects the data, builds the drug-target bipartite network as well as the two monopartite projections. The web interface allows a holistic view of the current drug repurposing status for COVID-19 to practitioners who are less familiar with the network mathematical framework, still offering the opportunity to explore the data, by taking advantage of some more specialized graph analysis tools, to more experienced users.By using this tool, we aim to recapitulate the initial system pharmacology of this plague, and by allowing free access to it to, eventually, maximize the open science philosophy. RESULTS"])
                        ], align="center", sm=12, md=6)
                    ], justify="around", align="center"),
                    html.Br(),
                    html.Br(),
                    html.H4("Citing COVID-19 Drugs Networker:"),
                    html.Br(),
                    html.H5(["If you are using data from the ", html.Em("COVID-19 Drugs Networker"), " please cite the corresponding article:"]),
                    html.P("bib string for easy citing, come per gli altri sotto"),
                    html.Br(),
                    html.Hr(),
                    html.Br(),
                    html.H4(["Last Database Update: 14",html.Sup("th")," January 2021"]),
                    html.Br(),
                    html.Hr(),
                    html.Br(),
                    html.H3("Data Sources:"),
                    html.Br(),
                    html.Ul([
                        html.Li([
                            html.A(html.Strong("DrugBank"), href="https://go.drugbank.com/", target="_blank", style={"color":"black"}),
                            html.A(html.P(["Wishart, David S et al. “DrugBank 5.0: a major update to the DrugBank database for 2018.” ",html.Em("Nucleic acids research")," vol. 46,D1 (2018): D1074-D1082"]), href="https://doi.org/10.1093/nar/gkx1037", target="_blank", style={"color":"black"})
                        ], style={"background":"url(https://go.drugbank.com/favicons/favicon-96x96.png)", "background-size":"2rem", "background-repeat":"no-repeat","background-position":"left", "padding-left":"4rem"}),
                        html.Li([
                            html.A(html.Strong("STRING"), href="https://string-db.org/", target="_blank", style={"color":"black"}),
                            html.A(html.P(["Szklarczyk, Damian et al. “STRING v11: protein-protein association networks with increased coverage, supporting functional discovery in genome-wide experimental datasets.” ",html.Em("Nucleic acids research")," vol. 47,D1 (2019): D607-D613"]), href="https://doi.org/10.1093/nar/gky1131", target="_blank", style={"color":"black"})
                        ], style={"background":"url(https://string-db.org/images/favicon.png", "background-size":"2rem", "background-repeat":"no-repeat","background-position":"left", "padding-left":"4rem"}),
                        html.Li([
                            html.A(html.Strong("DisGeNet"), href="https://www.disgenet.org/", target="_blank", style={"color":"black"}),
                            html.A(html.P(["Piñero, Janet et al. “The DisGeNET knowledge platform for disease genomics: 2019 update.” ",html.Em("Nucleic acids research")," vol. 48,D1 (2020): D845-D855"]), href="https://doi.org/10.1093/nar/gkz1021", target="_blank", style={"color":"black"})
                        ], style={"background":"url(https://www.disgenet.org/static/disgenet_ap1/images/logo_disgenet.png)", "background-size":"3rem", "background-repeat":"no-repeat","background-position":"left", "padding-left":"4rem"}),
                        html.Li([
                            html.A(html.Strong("SWISS-MODEL"), href="https://swissmodel.expasy.org/", target="_blank", style={"color":"black"}),
                            html.A(html.P(["Waterhouse, Andrew et al. “SWISS-MODEL: homology modelling of protein structures and complexes.” ",html.Em("Nucleic acids research")," vol. 46,W1 (2018): W296-W303"], style={"margin-bottom":"0.25em"}), href="https://doi.org/10.1093/nar/gky427", target="_blank", style={"color":"black"}),
                            html.A(html.P(["Guex, Nicolas et al. “Automated comparative protein structure modeling with SWISS-MODEL and Swiss-PdbViewer: a historical perspective.” ",html.Em("Electrophoresis")," vol. 30 Suppl 1 (2009): S162-73"], style={"margin-bottom":"0.25em"}), href="https://doi.org/10.1002/elps.200900140", target="_blank", style={"color":"black"}),
                            html.A(html.P(["Bienert, Stefan et al. “The SWISS-MODEL Repository-new features and functionality.” ",html.Em("Nucleic acids research")," vol. 45,D1 (2017): D313-D319"]), href="https://doi.org/10.1093/nar/gkw1132", target="_blank", style={"color":"black"})
                        ], style={"background":"url(https://swissmodel.expasy.org/static/images/favicon.png)", "background-size":"2rem", "background-repeat":"no-repeat","background-position":"left", "padding-left":"4rem"}),
                        html.Li([
                            html.A(html.Strong("RCSB PDB"), href="https://www.rcsb.org/", target="_blank", style={"color":"black"}),
                            html.A(html.P(["Berman, H M et al. “The Protein Data Bank.” ",html.Em("Nucleic acids research")," vol. 28,1 (2000): 235-42"]), href="https://doi.org/10.1093/nar/28.1.235", target="_blank", style={"color":"black"})
                        ], style={"background":"url(https://cdn.rcsb.org/rcsb-pdb/v2/common/images/rcsb_logo.png)", "background-size":"2rem", "background-repeat":"no-repeat","background-position":"left", "padding-left":"4rem"}),
                        html.Li([
                            html.A(html.Strong("UniProt"), href="https://www.uniprot.org/", target="_blank", style={"color":"black"}),
                            html.A(html.P(["UniProt Consortium. “UniProt: a worldwide hub of protein knowledge.” ",html.Em("Nucleic acids research")," vol. 47,D1 (2019): D506-D515"]), href="https://doi.org/10.1093/nar/gky1049", target="_blank", style={"color":"black"})
                        ], style={"background":"url(https://www.uniprot.org/favicon.ico)", "background-size":"2rem", "background-repeat":"no-repeat","background-position":"left", "padding-left":"4rem"}),
                        html.Li([
                            html.A(html.Strong("ChEMBL"), href="https://www.ebi.ac.uk/chembl/", target="_blank", style={"color":"black"}),
                            html.A(html.P(["Gaulton, Anna et al. “The ChEMBL database in 2017.” ",html.Em("Nucleic acids research")," vol. 45,D1 (2017): D945-D954"], style={"margin-bottom":"0.25em"}), href="https://doi.org/10.1093/nar/gkw1074", target="_blank", style={"color":"black"}),
                            html.A(html.P(["Davies, Mark et al. “ChEMBL web services: streamlining access to drug discovery data and utilities.” ",html.Em("Nucleic acids research")," vol. 43,W1 (2015): W612-20"]), href="https://doi.org/10.1093/nar/gkv352", target="_blank", style={"color":"black"})
                        ], style={"background":"url(https://www.ebi.ac.uk/chembl/k8s/static/chembl/favicon.png)", "background-size":"2rem", "background-repeat":"no-repeat","background-position":"left", "padding-left":"4rem"}),
                        html.Li([
                            html.Strong("Virus-Host Interactomes"),
                            html.A(html.P(["Gordon, David S et al. “A SARS-CoV-2 protein interaction map reveals targets for drug repurposing.” ",html.Em("Nature")," vol. 583,7816 (2020): 459-468"], style={"margin-bottom":"0.25em"}), href="https://doi.org/10.1038/s41586-020-2286-9", target="_blank", style={"color":"black"}),
                            html.A(html.P(["Chen, Zhen et al. “Comprehensive analysis of the host-virus interactome of SARS-CoV-2.” ",html.Em("bioRxiv")," (2021)"]), href="10.1101/2020.12.31.424961", target="_blank", style={"color":"black"})
                        ], style={"background-image":"url("+app.get_asset_url("others/lungs-virus-solid.svg")+")", "background-size":"2rem", "background-repeat":"no-repeat","background-position":"left", "padding-left":"4rem"}),
                    ], style={"list-style-type":"none"}),
                    html.Br(),
                    html.Hr(),
                    html.Br(),
                    html.H3("COVID-19 Drugs Networker would not be possible without the following packages:"),
                    html.Br(),
                    html.Ul([
                        html.Li([
                            html.A("Python 3", href="https://www.python.org/", target="_blank", style={"color":"black"}),
                            html.Ul([
                                html.Li(html.A("Pandas", href="https://pandas.pydata.org/", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Numpy", href="https://numpy.org/", target="_blank", style={"color":"black"})),
                                html.Li(html.A("os", href="https://docs.python.org/3/library/os.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Pickle", href="https://docs.python.org/3/library/pickle.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Json", href="https://docs.python.org/3/library/json.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Itertools", href="https://docs.python.org/3/library/itertools.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Requests", href="https://requests.readthedocs.io/en/master/", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Time", href="https://docs.python.org/3/library/time.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Datetime", href="https://docs.python.org/3/library/datetime.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Webbrowser", href="https://docs.python.org/3/library/webbrowser.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Threading", href="https://docs.python.org/3/library/threading.html", target="_blank", style={"color":"black"})),
                                html.Li([
                                    html.A("Matplotlib Pyplot", href="https://matplotlib.org/", target="_blank", style={"color":"black"}),
                                    #https://ieeexplore.ieee.org/document/4160265
                                ]),
                            ])
                        ]),
                        html.Li([
                            html.A("NetworkX", href="https://networkx.org/", target="_blank", style={"color":"black"}),
                            #http://conference.scipy.org/proceedings/SciPy2008/paper_2/
                        ]),
                        html.Li([
                            html.A("Plotly", href="https://plotly.com/", target="_blank", style={"color":"black"}),
                            #https://plotly.com/chart-studio-help/citations/
                        ]),
                        html.Li([
                            html.A("Dash", href="https://plotly.com/dash/", target="_blank", style={"color":"black"}),
                            html.Ul([
                                html.Li(html.A("Dash Core Components", href="https://dash.plotly.com/dash-core-components", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Dash HTML Components", href="https://dash.plotly.com/dash-html-components", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Dash Bootstrap Components", href="https://dash-bootstrap-components.opensource.faculty.ai/", target="_blank", style={"color":"black"})),
                                html.Li(html.A("Dash Cytoscape", href="https://dash.plotly.com/cytoscape", target="_blank", style={"color":"black"})),
                            ])
                        ]),
                        html.Li(html.A("PubChemPy", href="https://pubchempy.readthedocs.io/", target="_blank", style={"color":"black"})),
                        html.Li([
                            html.A("ChEMBL Webresource Client", href="https://github.com/chembl/chembl_webresource_client", target="_blank", style={"color":"black"}),
                            #https://github.com/chembl/chembl_webresource_client
                        ]),
                        html.Li(html.A("Beautiful Soup", href="https://www.crummy.com/software/BeautifulSoup/", target="_blank", style={"color":"black"})),
                        html.Li([
                            html.A("Rdkit", href="https://www.rdkit.org/", target="_blank", style={"color":"black"}),
                            #https://rdkit-discuss.narkive.com/9QGX4Vxh/is-there-a-way-to-cite-rdkit-in-a-paper
                        ]),
                        html.Li([
                            html.A("Scikit-learn", href="https://scikit-learn.org/", target="_blank", style={"color":"black"}),
                            #https://scikit-learn.org/stable/about.html#citing-scikit-learn
                        ]),
                        html.Li(html.A("Tqdm", href="https://github.com/tqdm/tqdm", target="_blank", style={"color":"black"})),
                    ]),

                    html.Br(),
                    html.Hr(),
                    html.Br(),
                    html.H3("Other Credits:"),
                    html.Br(),
                    html.Ul([
                        html.Li([
                            # html.I(className="fa fa-flag", style={"margin-right":"0.5rem"}),#fa-font-awesome-flag
                            html.A("Font Awesome", href="https://fontawesome.com/", target="_blank", style={"color":"black"})
                        ], style={"background":"url(https://fontawesome.com/images/favicons/favicon-96x96.png)", "background-size":"1rem", "background-repeat":"no-repeat","background-position":"left", "padding-left":"1.5rem"}),
                    ], style={"list-style-type":"none"}),
                    html.Br(),
                    html.Hr(),
                    html.Br(),
                    html.H3("Terms of Use"),
                    html.Br(),
                    html.P("Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")
                ], style={"padding":"2%", "width":"100%"})
            ]),
            html.Div(style={"height":"10vh"}),
            footer()
        ], style={"padding":"0px"})
