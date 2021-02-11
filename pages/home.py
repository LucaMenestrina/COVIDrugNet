import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from data.others.home_background_script import script
import visdcc


from building_blocks import *
from callbacks import *


prefix="home"
print("Loading "+prefix.capitalize()+" ...")

layout=dbc.Col([
            dbc.Col([
                # html.Center(html.H1(html.Strong("COVIDrugNet"))),
                html.Canvas(id="fancy-network-background",style={"position":"absolute", "width":"100%", "height":"60vh", "padding":"0px", "z-index":"0"}),# "background": "linear-gradient(to top, rgba(230,245,249,0), rgba(230,245,249,0.5))"
                html.Center(html.Img(src=app.get_asset_url("imgs/logo_wide.svg"), alt="COVID-19 Drugs Networker", style={"width":"66%", "margin-top":"5vh", "margin-bottom":"5vh","position":"relative","z-index":"1"})),
                visdcc.Run_js(id="fancy_network_background_script", run=script),
                # html.Center(html.H4("Visualize and Analyze Networks about Drugs and Targets Related to COVID-19")),
                dbc.Row([
                    dbc.Col([
                        html.A([
                            html.Center([
                                dbc.Card([
                                    dbc.CardImg(src=app.get_asset_url("imgs/drug_target.png"), top=True, style={"width":"75%", "margin":"auto"}, alt="Drug-Target Network"),
                                    dbc.CardBody(html.H4(html.Strong("Drug-Target Network"), className="card-title")),
                                    dbc.Container([
                                        html.H1(["Drug-Target",html.Br(),"Bipartite Network"], className="fancy-hover-title"),
                                        html.H3("It is the main network and it is built connecting drugs from the COVID-19 Dashboard of DrugBank and their reported targets.", className="fancy-hover-text")
                                    ], className="fancy-hover-bg")
                                ], color="light", style={"box-shadow":"0rem 0rem 0.25rem lightgrey", "border-radius": "2rem"})
                            ])
                        ], href="/covidrugnet/drug_target", style={"text-decoration":"none"}, className="home-card"),
                    ], xs=10, md=3),
                    dbc.Col([
                        html.A([
                            html.Center([
                                dbc.Card([
                                    dbc.CardImg(src=app.get_asset_url("imgs/drug_projection.png"), top=True, style={"width":"75%", "margin":"auto"}, alt="Drug Projection"),
                                    dbc.CardBody(html.H4(html.Strong("Drug Projection"), className="card-title")),
                                    dbc.Container([
                                        html.H1("Drug Projection", className="fancy-hover-title"),
                                        html.H3([
                                            "It is built from the Drug-Target Network and contains only drugs.",
                                            html.Br(),
                                            html.Br(),
                                            "They are connected if they share at least a target in the Drug-Target Network"
                                        ], className="fancy-hover-text")
                                    ], className="fancy-hover-bg")
                                ], color="light", style={"box-shadow":"0rem 0rem 0.25rem lightgrey", "border-radius": "2rem"})
                            ])
                        ], href="/covidrugnet/drug_projection", style={"text-decoration":"none"}, className="home-card"),
                    ], xs=10, md=3),
                    dbc.Col([
                        html.A([
                            html.Center([
                                dbc.Card([
                                    dbc.CardImg(src=app.get_asset_url("imgs/target_projection.png"), top=True, style={"width":"75%", "margin":"auto"}, alt="Target Projection"),
                                    dbc.CardBody(html.H4(html.Strong("Target Projection"), className="card-title")),
                                    dbc.Container([
                                        html.H1("Target Projection", className="fancy-hover-title"),
                                        html.H3([
                                            "It is built from the Drug-Target Network and contains only targets.",
                                            html.Br(),
                                            html.Br(),
                                            "They are connected if they share at least a drug in the Drug-Target Network"
                                        ], className="fancy-hover-text")
                                    ], className="fancy-hover-bg")
                                ], color="light", style={"box-shadow":"0rem 0rem 0.25rem lightgrey", "border-radius": "2rem"})
                            ])
                        ], href="/covidrugnet/target_projection", style={"text-decoration":"none"}, className="home-card"),
                    ], xs=10, md=3)
                ], justify="center", align="center"),
                html.Div(style={"height":"10vh"}),
                dbc.Row([
                    dbc.Col([
                        html.Center([
                            html.P([html.Font("For help browsing the app check the "),html.A("Help", href="/covidrugnet/help"),html.Font(" section")]),
                            html.P([html.Font("Otherwise feel free to "),html.A("reach us out", href="/covidrugnet/contacts")]),
                            html.P([html.Font("Info and Credits about the project can be found in the "),html.A("About", href="/covidrugnet/about"),html.Font(" section")])
                        ])
                    ], width=10)
                ], no_gutters=True, justify="center", align="center"),
                html.Div(style={"height":"10vh"})
            ], style={"padding-left":"0px"}),
            html.Div(style={"height":"10vh"}),
            footer()
        ], style={"padding":"0px", "min-height":"100vh"})
