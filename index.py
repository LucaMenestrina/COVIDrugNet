import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app
from pages import home,help,about,contacts,drug_target,drug_drug,target_target,error404#, target_disease, target_interactors
from building_blocks import headbar, loading_banner

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    headbar(),
    html.Div(id="loading_message")
])
            # @media (min-device-width: 1200px) { body {initial-scale:1;} }
            # @media (min-device-width: 768px) { body {initial-scale:0.8;} }
            # @media (min-device-width: 600px) { body {initial-scale:0.6;} }
            # @media (max-device-width: 600px) { body {initial-scale:0.5;} }
            # @media (min-device-width: 1366px) { body {font-size:1rem;} }
            # @media (min-device-width: 1024px) { body {font-size:0.8rem;} }
            # @media (min-device-width: 720px) { body {font-size:0.6rem;} }
            # @media (max-device-width: 720px) { body {font-size:0.5rem;} }

app.index_string='''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            @media (max-width: 600px) { html {font-size:60%;} }
            @media (min-width: 600px) { html {font-size:65%;} }
            @media (min-width: 768px) { html {font-size:70%;} }
            @media (min-width: 1024px) { html {font-size:72.5%;} }
            @media (min-width: 1280px) { html {font-size:75%;} }
            @media (min-width: 1366px) { html {font-size:80%;} }
            @media (min-width: 1536px) { html {font-size:100%;} }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


@app.callback(Output("loading_message", "children"),
            [Input("url", "pathname")])
def temp_loading(pathname):
    if pathname:
        return loading_banner
        # return html.Div(
        #     html.Center([
        #         html.Div(style={"height":"20vh"}),
        #         dbc.Fade(
        #             dbc.Jumbotron([
        #                 html.H2("Sorry, it's taking some time to load ..."),
        #                 html.Hr(),
        #                 html.H5("Networks are becoming more and more complex,"),
        #                 html.H5("and the browser could take a while to render the page"),
        #                 html.P("If it takes too long (or it doesn't load at all) please let us know"),
        #                 html.Br(),
        #                 html.Img(src=app.get_asset_url("imgs/logo.svg"), style={"height":"10vh"}),
        #                 html.Br(),
        #                 html.Small("Also a small banner could appear on top of your window saing that a calculation is slowing down your browser")
        #             ], style={"width":"40vw"}
        #         ), is_in=True, timeout=250)]
        #     ),id="page_content")

@app.callback(Output("page_content", "children"),
            [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/covid19drugsnetworker" or pathname == "/covid19drugsnetworker/home":
        return home.layout
    if pathname == "/help":
        return help.layout
    if pathname == "/contacts":
        return contacts.layout
    if pathname == "/about":
        return about.layout
    if pathname == "/drug_target":
        return drug_target.layout
    elif pathname == "/drug_drug":
        return drug_drug.layout
    if pathname == "/target_target":
        return target_target.layout
    # if pathname == "/target_disease":
    #     return target_disease.layout
    # if pathname == "/target_interactors":
    #     return target_interactors.layout
    else:
        return error404.layout

if __name__ == "__main__":
    app.run_server(debug=False)
