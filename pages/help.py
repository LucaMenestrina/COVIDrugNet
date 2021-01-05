import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from building_blocks import *
from callbacks import *

# app=dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
# app.title="COVID-19 Networker"

prefix="help"
print("Loading "+prefix.capitalize()+" ...")

layout=dbc.Col([
            dbc.Col([
                html.Br(),
                dbc.Col([
                    html.H3("Help"),
                    html.Br(),
                    html.Center([
                        html.Img(src=app.get_asset_url("imgs/help.svg"), style={"width":"100%"})
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



# if __name__=="__main__":
#     app.run_server(debug=False)
