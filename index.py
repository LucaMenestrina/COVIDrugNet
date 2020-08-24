import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from pages import home,help,about,contacts,drug_target,drug_drug,target_target#, target_disease, target_interactors

app.title="COVID-19 Networker"

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':
        return home.layout
    if pathname == '/help':
        return help.layout
    if pathname == '/contacts':
        return contacts.layout
    if pathname == '/about':
        return about.layout
    if pathname == '/drug_target':
        return drug_target.layout
    elif pathname == '/drug_drug':
        return drug_drug.layout
    if pathname == '/target_target':
        return target_target.layout
    # if pathname == '/target_disease':
    #     return target_disease.layout
    # if pathname == '/target_interactors':
    #     return target_interactors.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=False)
