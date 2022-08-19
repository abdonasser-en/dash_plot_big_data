from dash import html, dcc
import pandas as pd
import dash_uploader as du
from pathlib import Pathgit
import uuid
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Output, Input, State, ALL, MATCH, ServersideOutput, html, dcc, \
    ServersideOutputTransform
import plotly.io as pio
from lenspy import DynamicPlot

app = DashProxy(__name__, transforms=[ServersideOutputTransform()])

UPLOAD_FOLDER_ROOT = r"C:\tmp\Uploads"
du.configure_upload(app, UPLOAD_FOLDER_ROOT)


def get_upload_component(id):
    return du.Upload(
        id=id,
        max_file_size=1800,  # 1800 Mb
        filetypes=['csv'],
        upload_id=uuid.uuid1(),  # Unique session id
    )


app.layout = html.Div(
    [
        html.H1('Demo'),
        html.Div(
            [
                get_upload_component(id='dash-uploader'),
                html.Div(id='callback-output'),
            ],
            style={  # wrapper div style
                'textAlign': 'center',
                'width': '600px',
                'padding': '10px',
                'display': 'inline-block'
            }),
        html.Div("Reloc", id="path_brute", style={'display': 'none'}),
        dcc.Store(id="données"),
        html.Div(dcc.Graph(), id="graphe")
    ],
    style={
        'textAlign': 'center',
    },
)


@du.callback(
    output=Output("callback-output", "children"),
    id="dash-uploader",
)
def callback_on_completion(status: du.UploadStatus):
    return html.Ul([html.Li(str(x)) for x in status.uploaded_files])


@app.callback(
    Output('path_brute', 'children'),
    Input('callback-output', 'children')
)
def get_a_list(children):
    if children is None:
        raise PreventUpdate
    else:
        return f'{children["props"]["children"][0]["props"]["children"]}'


@app.callback(
    ServersideOutput('données', 'data'),
    Input('path_brute', 'children'), prevent_initial_call=True
)
def store_data(children):
    meteo = pd.read_csv(children, sep=";")

    return meteo


@app.callback(Output("graphe", "children"), Input("données", "data"))
def trace(data):
    if data is None:
        raise PreventUpdate
    fig = go.Figure()
    figure_test = fig
    figure_test.add_trace(go.Scattergl(
        y=data['LATITUDE'], x=data['LONGITUDE'], mode='markers', name="Tournée brute"))
    pio.write_image(figure_test, "Graphe.pdf")
    plot = DynamicPlot(fig)
    graph_cc = dcc.Graph(id="my_plot",
                         figure=plot.fig,
                         style={"height": "1000px", "width": "100%"})

    return graph_cc


if __name__ == '__main__':
    app.run_server(debug=True)
