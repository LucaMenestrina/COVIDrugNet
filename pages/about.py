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
                    html.H2("About the Project"),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(
                            html.A(
                                dbc.Row([
                                    dbc.Col([html.Img(src=app.get_asset_url("imgs/wordcloud.png"), style={"width":"100%"})], align="center", sm=5, lg=4),
                                    dbc.Col([
                                        html.Br(),
                                        html.H4(html.Strong("COVIDrugNet: a network-based web tool to investigate the drugs currently in clinical trial to contrast COVID-19"), style={"margin-bottom":"1rem"}),
                                        html.H5("Luca Menestrina, Chiara Cabrelle and Maurizio Recanatini"),
                                        html.P(html.Em("Department of Pharmacy and Biotechnology, Alma Mater Studiorum - University of Bologna 40126 Bologna, Italy"), style={"margin-bottom":"1rem"}),
                                        html.Br(),
                                        html.H5("Preprint at bioRxiv"),
                                        # html.H5("Jurnal, Pages, Issue, Year ..."),
                                        # html.Br(),
                                        # dbc.Row([
                                        #     dbc.Col([
                                        #         html.P("Received", style={"margin-bottom":"0.5rem"}),
                                        #         html.P(html.Time("Not Yet",dateTime="1900-01-01")),
                                        #     ], align="center"),
                                        #     # dbc.Col([
                                        #     #     html.P("Hopefully Accepted", style={"margin-bottom":"0.5rem","color":"grey"}),
                                        #     #     html.P(html.Time("Not Yet",dateTime="1900-01-01"), style={"color":"grey"}),
                                        #     # ], align="center"),
                                        #     # dbc.Col([
                                        #     #     html.P("Hopefully Published", style={"margin-bottom":"0.5rem","color":"grey"}),
                                        #     #     html.P(html.Time("Not Yet",dateTime="1900-01-01"), style={"color":"grey"}),
                                        #     # ], align="center")
                                        # ], justify="around", align="center"),
                                        html.Br(),
                                        html.H5("DOI:"),
                                        html.A("https://doi.org/10.1101/2021.03.05.433897", href="https://doi.org/10.1101/2021.03.05.433897", target="_blank"),
                                    ], align="center", sm=7, lg=8)
                                ], justify="center", align="center", id="paper"),
                            href="https://www.biorxiv.org/content/10.1101/2021.03.05.433897v1", target="_blank", style={"color":"black", "text-decoration":"none"}),
                        align="center", sm=10, lg=7, style={"padding-right":"2vw"}),
                        html.Br(),
                        dbc.Col([
                            html.Br(),
                            html.H4(html.Strong("Abstract")),
                            html.P("The COVID-19 pandemic poses a huge problem of public health that requires the implementation of all available means to contrast it, and drugs are one of them. In this context, we observed an unmet need of depicting the continuously evolving scenario of the ongoing drug clinical trials through an easy-to-use, freely accessible online tool. Starting from this consideration, we developed COVIDrugNet, a web application that allows users to capture a holistic view and keep up to date on how the clinical drug research is responding to the SARS-CoV-2 infection.", style={"margin-bottom":0}),
                            html.P([
                                html.A("In the paper", href="https://www.biorxiv.org/content/10.1101/2021.03.05.433897v1", target="_blank", style={"color":"black", "text-decoration":"none"}),
                                " we describe the web app and show through some examples how one can explore the whole landscape of medicines in clinical trial for the treatment of COVID-19 and try to probe the consistency of the current approaches with the available biological and pharmacological evidence. We conclude that careful analyses of the COVID-19 drug-target system based on COVIDrugNet can help to understand the biological implications of the proposed drug options, and eventually improve the search for more effective therapies."
                            ]),
                        ], align="center", sm=10, lg=5, style={"text-align":"justify", "font-size":"large", "padding-right":"1vw"})
                    ], justify="around", align="center"),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.H4("Reference"),
                    html.Br(),
                    html.H5(["If you are using data from ", html.Em("COVIDrugNet"), " please cite ", html.A("our article", href="https://www.biorxiv.org/content/10.1101/2021.03.05.433897v1", target="_blank", style={"color":"black"}),":"]),
                    html.Br(),
                    html.Pre([
                        "@article {Menestrina2021.03.05.433897,",html.Br(),
                        "\t title = {COVIDrugNet: a network-based web tool to investigate the drugs currently in clinical trial to contrast COVID-19},",html.Br(),
                        "\t author = {Menestrina, Luca and Cabrelle, Chiara and Recanatini, Maurizio},",html.Br(),
                        "\t journal = {bioRxiv}",html.Br(),
                        "\t year = {2021},",html.Br(),
                        "\t doi = {10.1101/2021.03.05.433897},",html.Br(),
                        "\t URL = {https://www.biorxiv.org/content/early/2021/03/09/2021.03.05.433897},",html.Br(),
                        "\t publisher = {Cold Spring Harbor Laboratory},",html.Br(),
                        "}"
                    ], style={"background-color":"rgba(211,211,211,0.15)", "border-radius": "0.6rem"}),
                    # html.P("bib string for easy citing, come per gli altri sotto"),
                    html.Br(),
                    html.Hr(),
                    html.Br(),
                    html.H4(["Last Database Update: ",html.Time(["2",html.Sup("nd")," August 2021"], dateTime="2021-08-02"), " (No changes since 8",html.Sup("th")," June 2021)"]),
                    html.Br(),
                    html.H5(["Data and Code Available at: ",html.A("https://github.com/LucaMenestrina/COVIDrugNet", href="https://github.com/LucaMenestrina/COVIDrugNet", target="_blank", style={"color":"black"})]),
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
                            html.A(html.Strong("DisGeNET"), href="https://www.disgenet.org/", target="_blank", style={"color":"black"}),
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
                    html.H3("COVIDrugNet would not be possible without the following packages:"),
                    html.Br(),
                    html.Ul([
                        html.Li([
                            html.A("Python 3", href="https://www.python.org/", target="_blank", style={"color":"black"}),
                            html.Ul([
                                html.Li(html.A("datetime", href="https://docs.python.org/3/library/datetime.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("itertools", href="https://docs.python.org/3/library/itertools.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("json", href="https://docs.python.org/3/library/json.html", target="_blank", style={"color":"black"})),
                                html.Li([
                                    html.A("matplotlib pyplot", href="https://matplotlib.org/", target="_blank", style={"color":"black"}),
                                    #https://ieeexplore.ieee.org/document/4160265
                                ]),
                                html.Li(html.A("numpy", href="https://numpy.org/", target="_blank", style={"color":"black"})),
                                html.Li(html.A("os", href="https://docs.python.org/3/library/os.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("pandas", href="https://pandas.pydata.org/", target="_blank", style={"color":"black"})),
                                html.Li(html.A("pickle", href="https://docs.python.org/3/library/pickle.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("requests", href="https://requests.readthedocs.io/en/master/", target="_blank", style={"color":"black"})),
                                html.Li(html.A("threading", href="https://docs.python.org/3/library/threading.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("time", href="https://docs.python.org/3/library/time.html", target="_blank", style={"color":"black"})),
                                html.Li(html.A("webbrowser", href="https://docs.python.org/3/library/webbrowser.html", target="_blank", style={"color":"black"})),
                            ])
                        ]),
                        html.Li(html.A("beautiful soup", href="https://www.crummy.com/software/BeautifulSoup/", target="_blank", style={"color":"black"})),
                        html.Li([
                            html.A("chembl webresource client", href="https://github.com/chembl/chembl_webresource_client", target="_blank", style={"color":"black"}),
                            #https://github.com/chembl/chembl_webresource_client
                        ]),
                        html.Li([
                            html.A("dash", href="https://plotly.com/dash/", target="_blank", style={"color":"black"}),
                            html.Ul([
                                html.Li(html.A("dash bootstrap components", href="https://dash-bootstrap-components.opensource.faculty.ai/", target="_blank", style={"color":"black"})),
                                html.Li(html.A("dash core components", href="https://dash.plotly.com/dash-core-components", target="_blank", style={"color":"black"})),
                                html.Li(html.A("dash cytoscape", href="https://dash.plotly.com/cytoscape", target="_blank", style={"color":"black"})),
                                html.Li(html.A("dash daq", href="https://dash.plotly.com/dash-daq", target="_blank", style={"color":"black"})),
                                html.Li(html.A("dash html components", href="https://dash.plotly.com/dash-html-components", target="_blank", style={"color":"black"})),
                                html.Li(html.A("dash table", href="https://github.com/plotly/dash-table", target="_blank", style={"color":"black"})),
                            ])
                        ]),
                        html.Li([
                            html.A("networkx", href="https://networkx.org/", target="_blank", style={"color":"black"}),
                            #http://conference.scipy.org/proceedings/SciPy2008/paper_2/
                        ]),
                        html.Li([
                            html.A("plotly", href="https://plotly.com/", target="_blank", style={"color":"black"}),
                            #https://plotly.com/chart-studio-help/citations/
                        ]),

                        html.Li(html.A("powerlaw", href="https://github.com/jeffalstott/powerlaw", target="_blank", style={"color":"black"})),
                        html.Li(html.A("PubChemPy", href="https://pubchempy.readthedocs.io/", target="_blank", style={"color":"black"})),
                        html.Li(html.A("pygraphviz", href="https://pygraphviz.github.io/", target="_blank", style={"color":"black"})),
                        html.Li([
                            html.A("rdkit", href="https://www.rdkit.org/", target="_blank", style={"color":"black"}),
                            #https://rdkit-discuss.narkive.com/9QGX4Vxh/is-there-a-way-to-cite-rdkit-in-a-paper
                        ]),
                        html.Li([
                            html.A("scikit-learn", href="https://scikit-learn.org/", target="_blank", style={"color":"black"}),
                            #https://scikit-learn.org/stable/about.html#citing-scikit-learn
                        ]),
                        html.Li(html.A("scipy", href="https://www.scipy.org/", target="_blank", style={"color":"black"})),
                        html.Li(html.A("tqdm", href="https://github.com/tqdm/tqdm", target="_blank", style={"color":"black"})),

                        html.Li(html.A("visdcc", href="https://github.com/jimmybow/visdcc", target="_blank", style={"color":"black"})),
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
                        ], style={"background":"url(https://fontawesome.com//images/favicon/icon.svg)", "background-size":"1rem", "background-repeat":"no-repeat","background-position":"left", "padding-left":"1.5rem"}),
                        html.Li([
                            html.A("Particles Random Animation in Canvas by Nokey", href="https://codepen.io/jkiss/pen/OVEeqK", target="_blank", style={"color":"black"})
                        ], style={"background":"url(https://cpwebassets.codepen.io/assets/favicon/favicon-touch-de50acbf5d634ec6791894eba4ba9cf490f709b3d742597c6fc4b734e6492a5a.png)", "background-size":"1rem", "background-repeat":"no-repeat","background-position":"left", "padding-left":"1.5rem"}),
                    ], style={"list-style-type":"none"}),
                    # html.Br(),
                    # html.Hr(),
                    # html.Br(),
                    # html.H3("Terms of Use"),
                    # html.Br(),
                    # html.P("Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")
                ], style={"padding":"2%", "width":"100%"})
            ]),
            html.Div(style={"height":"10vh"}),
            footer()
        ], style={"padding":"0px"})
