import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from building_blocks import *
from callbacks import *


prefix="help"
print("Loading "+prefix.capitalize()+" ...")

layout=dbc.Col([
            dbc.Col([
                html.Br(),
                dbc.Col([
                    html.H2("Help"),
                    html.Br(),
                    html.Center([
                        html.Img(src=app.get_asset_url("imgs/help.svg"), style={"width":"100%"})
                    ]),
                    html.Hr(),
                    html.Br(),
                    html.H4("In the pages relative to the projections, there are some small differences:"),
                    html.Br(),
                    html.H5("In the Charts and Plots Section the degree distribution is displayed"),
                    html.Center([
                        html.Img(src=app.get_asset_url("imgs/help_charts&plots.svg"), style={"width":"100%"})
                    ]),
                    html.Br(),
                    html.Br(),
                    html.H5("In the Advanced Tools Section the Degree Distribution can be inspected more thoroughly"),
                    html.Center([
                        html.Img(src=app.get_asset_url("imgs/help_advDD.svg"), style={"width":"100%"})
                    ]),
                    # html.Br(),
                    # html.Br(),
                    # dbc.Row([
                    #     dbc.Col([
                    #         html.Center(html.H5([html.Font("If there still is something unclear feel free to "),html.A("reach us out", href="/contacts")], style={"margin":"0px"}))
                    #     ], className="card border-primary", width=5, align="center", style={"padding":"2%"})
                    # ], no_gutters=True, justify="center", align="center"),
                    ], style={"padding":"2%", "width":"100%"}),
            ]),
            html.Div(style={"height":"10vh"}),
            footer()
        ], style={"padding":"0px"})
