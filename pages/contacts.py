import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from building_blocks import *
from callbacks import *


prefix="contacts"
print("Loading "+prefix.capitalize()+" ...")

layout=dbc.Col([
            dbc.Col([
                html.Br(),
                dbc.Col([
                    html.H3("Contacts"),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([html.Img(src="https://i1.rgstatic.net/ii/profile.image/753323955191811-1556617835990_Q512/Maurizio_Recanatini.jpg", style={"width":"100%"})], xs=3, md=2, xl=1, align="center"),
                        dbc.Col([
                            html.H5(html.Strong("Maurizio Recanatini")),
                            html.P("Principal Investigator"),
                            html.A("maurizio.recanatini@unibo.it", href="mailto:maurizio.recanatini@unibo.it", style={"color":"black"})
                        ], align="center")
                    ], justify="around", align="center"),
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([html.Img(src="https://phd.unibo.it/biotechnology-biocomputational-pharmaceutics-pharmacology/en/students/chiara-cabrelle/@@images/4d9aadfc-4c16-42ac-b53a-22c3c064769e.jpeg", style={"width":"100%"})], xs=3, md=2, xl=1, align="center"),
                        dbc.Col([
                            html.H5(html.Strong("Chiara Cabrelle")),
                            html.P("PhD Student in Biotechnological, Biocomputational, Pharmaceutical and Pharmacological Science"),
                            html.A("chiara.cabrelle2@unibo.it", href="mailto:chiara.cabrelle2@unibo.it", style={"color":"black"})
                        ], align="center")
                    ], justify="around", align="center"),
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([html.Img(src="https://drive.google.com/uc?export=view&id=1toLB_a0N2PP3thAq13gCr5yHR79WFAFs", style={"width":"100%"})], xs=3, md=2, xl=1, align="center"),
                        dbc.Col([
                            html.H5(html.Strong("Luca Menestrina")),
                            html.P("PhD Student in Data Science and Computation"),
                            html.A("luca.menestrina2@unibo.it", href="mailto:luca.menestrina2@unibo.it", style={"color":"black"}),
                            html.Br(),
                            html.Br(),
                            html.P("Please help me improving this app: if you find any malfunction (sure there are...) or you have suggestions, drop me an email.")
                        ], align="center")
                    ], justify="around", align="center"),
                    html.Br()
                ], style={"padding":"2%", "width":"100%"})
            ], style={"height":"100vh"}),
            footer()
        ], style={"padding":"0px"})
