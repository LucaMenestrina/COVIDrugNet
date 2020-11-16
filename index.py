#Just a log print
import datetime
StartTimePrint=datetime.datetime.now()
print("Starting COVID-19 Drugs Networker")

#adjust cwd if not launched with "python index.py"
import os
path=__file__.split("index.py")[0]
if path != "":
    os.chdir(path)

#import modules
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app
from pages import home,help,about,contacts,drug_target,drug_drug,target_target,error404#, target_disease, target_interactors
from building_blocks import headbar, loading_banner

server = app.server

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    headbar(),
    html.Div(id="loading_message")
])


@app.callback(Output("loading_message", "children"),
            [Input("url", "pathname")])
def temp_loading(pathname):
    if pathname:
        return loading_banner

@app.callback(Output("page_content", "children"),
            [Input("url", "pathname")])
def display_page(pathname):
    if pathname in ["/covid19drugsnetworker", "/covid19drugsnetworker/", "/covid19drugsnetworker/home"]:
        return home.layout
    elif pathname == "/covid19drugsnetworker/help":
        return help.layout
    elif pathname == "/covid19drugsnetworker/contacts":
        return contacts.layout
    elif pathname == "/covid19drugsnetworker/about":
        return about.layout
    elif pathname == "/covid19drugsnetworker/drug_target":
        return drug_target.layout
    elif pathname == "/covid19drugsnetworker/drug_drug":
        return drug_drug.layout
    elif pathname == "/covid19drugsnetworker/target_target":
        return target_target.layout
    # if pathname == "/target_disease":
    #     return target_disease.layout
    # if pathname == "/target_interactors":
    #     return target_interactors.layout
    else:
        return error404.layout


if __name__ == "__main__":
    print("Ready!\t(startup time: %s)\n"%(datetime.datetime.now()-StartTimePrint))
    app.run_server(debug=False)
elif __name__ == "index":
    # custom setting for deploying it with wsgi using from index import server as application (if setting a WSGIScriptAlias to /covid19drugsnetworker/)
    app.config.update({"requests_pathname_prefix":"/covid19drugsnetworker/"})
    print("Ready!\t(startup time: %s)\n"%(datetime.datetime.now()-StartTimePrint))
