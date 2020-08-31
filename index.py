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
        return '404' #devo fare una pagina apposita
#{'pos': array([ 0.20631291, -0.02379196]), 'ID': 'DB14761', 'SMILES': 'CCC(CC)COC(=O)[C@H](C)N[P@](=O)(OC[C@@H]1[C@H]([C@H]([C@](O1)(C#N)C2=CC=C3N2N=CN=C3N)O)O)OC4=CC=CC=C4', 'ATC_Code1': ['Not Available'], 'ATC_Code5': ['Not Available'], 'Targets': 'Replicase polyprotein 1ab, RNA-directed RNA polymerase L', 'Enzymes': 'Cytochrome P450 2C8, Cytochrome P450 2D6, Cytochrome P450 3A4', 'Carriers': '', 'Transporters': 'Solute carrier organic anion transporter family member 1B1, P-glycoprotein 1, Solute carrier organic anion transporter family member 1B3, Bile salt export pump, Multidrug resistance-associated protein 4, Sodium/bile acid cotransporter', 'Drug_Interactions': '', 'name': 'Remdesivir', 'structure': 'https://www.drugbank.ca/structures/DB14761/image.svg', 'kind': 'Drug', 'fill_color': '#FC5F67', 'line_color': '#FB3640', 'degree': 2, 'Closeness_Centrality': 0.0066777303619408885, 'Betweenness_Centrality': 2.3545931691111623e-05, 'id': 'Remdesivir'}

if __name__ == '__main__':
    app.run_server(debug=False)
