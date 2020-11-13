import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from building_blocks import *
from callbacks import *

# app=dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
# app.title="COVID-19 Drugs Networker"

prefix="error404"
print("Loading "+prefix.capitalize()+" ...")

layout=dbc.Col([
            dbc.Col([
                html.Br(),
                dbc.Col([
                    html.Center([
                        dbc.Jumbotron([
                            html.H1("404 Page Not Found"),
                            html.H3("Sorry, we can't find that page ..."),
                            html.H5("Please check the URL and try again ..."),
                            html.Br(),
                            html.Hr(),
                            html.Br(),
                            html.P([html.Font("Try to go back to our "),html.A("homepage", href="/covid19drugsnetworker/home")]),
                            html.P([html.Font("If the problem persists, please "),html.A("let us know", href="mailto:luca.menestrina2@unibo.it")])
                        ], style={"width":"50vw"})
                    ])
                ], style={"padding":"2%", "width":"100%"})
            ], style={"height":"100vh"}),
            footer()
        ], style={"padding":"0px"})


##  ----------  CALLBACKS   ------------

collapse_headbar_callback(prefix)

# if __name__=="__main__":
#     app.run_server(debug=False)
