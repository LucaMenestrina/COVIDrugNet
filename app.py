import dash
import dash_bootstrap_components as dbc

meta=[
    {
        "name": "author",
        "content": "Luca Menestrina"
    },
    {
        "name": "affilitaion",
        "content": "University of Bologna"
    },
    {
        "name": "title",
        "content": "COVIDrugNet"
    },
    {
        "name": "description",
        "content": "Visualize and Analyze Networks about Drugs and Targets Related to COVID-19"
    },
    {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }
]

font_awesome = {
        "href": "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
        "rel": "stylesheet",
        "integrity": "sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf",
        "crossorigin": "anonymous"
    }

app_entry='''
<div id="react-entry-point">
    <div class="_dash-loading">
        <center>
            <div style="height:15vh;"></div>
            <img src="/assets/imgs/logo.svg" alt="COVIDrugNet" style="height:60vh">
            <div style="height:2vh;"></div>
            <h3>
                Loading ...
            </h3>
        </center>
    </div>
</div>
'''

class CustomDash(dash.Dash):
    def interpolate_index(self, **kwargs):
        return '''
        <!DOCTYPE html>
        <html>
            <head>
                {metas}
                <title>COVIDrugNet</title>
                {favicon}
                {css}
                <style>
                    @media (max-width: 600px) {{ html {{font-size:60%;}} }}
                    @media (min-width: 600px) {{ html {{font-size:65%;}} }}
                    @media (min-width: 768px) {{ html {{font-size:70%;}} }}
                    @media (min-width: 1024px) {{ html {{font-size:75%;}} }}
                    @media (min-width: 1280px) {{ html {{font-size:80%;}} }}
                    @media (min-width: 1366px) {{ html {{font-size:90%;}} }}
                    @media (min-width: 1450px) {{ html {{font-size:95%;}} }}
                    @media (min-width: 1536px) {{ html {{font-size:100%;}} }}
                </style>
            </head>
            <body>
                {app_entry}
                <footer>
                    {config}
                    {scripts}
                    {renderer}
                </footer>
            </body>
        </html>
        '''.format(
            metas=kwargs["metas"],
            favicon=kwargs["favicon"],
            css=kwargs["css"],
            app_entry=app_entry,#kwargs["app_entry"],
            config=kwargs["config"],
            scripts=kwargs["scripts"],
            renderer=kwargs["renderer"])

app = CustomDash(__name__, external_stylesheets=[dbc.themes.LUMEN, font_awesome], suppress_callback_exceptions=True, meta_tags=meta, assets_folder="data")
