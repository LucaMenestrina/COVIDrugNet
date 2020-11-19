import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from building_blocks import *
from callbacks import *

# app=dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
# app.title="COVID-19 Drugs Networker"

prefix="home"
print("Loading "+prefix.capitalize()+" ...")

layout=dbc.Col([
            dbc.Col([
                # html.Center(html.H1(html.Strong("COVID-19 Drugs Networker"))),
                html.Center(html.Img(src=app.get_asset_url("imgs/logo_wide.svg"), alt="COVID-19 Drugs Networker", style={"width":"75%"})),
                # html.Center(html.H4("Visualize and Analyze Networks about Drugs and Targets Related to COVID-19")),
                dbc.Row([
                    dbc.Col([
                        html.A([
                            html.Center([
                                html.Img(src=app.get_asset_url("imgs/drug_target.jpg"), style={"width":"95%"}, alt="Drug Target Graph"),
                                html.H5(html.Strong("Drug-Target Network"), className="card-header")
                            ], style={"box-shadow":"0rem 0rem 0.25rem darkgrey"})
                        ], href="/covid19drugsnetworker/drug_target", className="card"),
                    ], xs=12, md=3),
                    dbc.Col([
                        html.A([
                            html.Center([
                                html.Img(src=app.get_asset_url("imgs/drug_drug.jpg"), style={"width":"95%"}, alt="Drug Drug Graph"),
                                html.H5(html.Strong("Drug-Drug Projection"), className="card-header")
                            ], style={"box-shadow":"0rem 0rem 0.25rem darkgrey"})
                        ], href="/covid19drugsnetworker/drug_drug", className="card"),
                    ], xs=12, md=3),
                    dbc.Col([
                        html.A([
                            html.Center([
                                html.Img(src=app.get_asset_url("imgs/target_target.jpg"), style={"width":"95%"}, alt="Target Target Graph"),
                                html.H5(html.Strong("Target-Target Projection"), className="card-header")
                            ], style={"box-shadow":"0rem 0rem 0.25rem darkgrey"})
                        ], href="/covid19drugsnetworker/target_target", className="card"),
                    ], xs=12, md=3)
                ], justify="center", align="center"),
                html.Div(style={"height":"10vh"}),
                dbc.Row([
                    dbc.Col([
                        html.Center([
                            html.P([html.Font("For help browsing the app check the "),html.A("Help", href="/covid19drugsnetworker/help"),html.Font(" section")]),
                            html.P([html.Font("Otherwise feel free to "),html.A("reach us out", href="/covid19drugsnetworker/contacts")]),
                            html.P([html.Font("Info and Credits about the project can be found in the "),html.A("About", href="/covid19drugsnetworker/about"),html.Font(" section")])
                        ])
                    ], width=10)
                ], no_gutters=True, justify="center", align="center"),
                html.Div(style={"height":"10vh"})
            ]),
            html.Div(style={"height":"10vh"}),
            footer()
        ], style={"padding":"0px", "min-height":"100vh"})


##  ----------  CALLBACKS   ------------

collapse_headbar_callback(prefix)

# if __name__=="__main__":
#     app.run_server(debug=False)
