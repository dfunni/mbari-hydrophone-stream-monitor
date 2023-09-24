from dash import Dash, html, dcc, callback, Output, Input, State
# import plotly.express as px
from cetacean import DataDir, MarsClip, pull_data

import warnings
warnings.filterwarnings("ignore")

app = Dash(__name__)

data = DataDir("assets/data/new_data/")
datafile_iter = iter(data)


app.layout = html.Div([
    html.Div([
        html.H1(id='title', children='MARS labler ', style={'textAlign':'center'}),
        html.Img(id='graph-content'),
    ]),
    html.Div([
        html.Audio(id='audio-control', controls=True) ## FIXME
    ]),
    html.Div([
        html.Button('Whale', id='whale-val', n_clicks=0),
        html.Button('No Whale', id='no_whale-val', n_clicks=0)
    ]),
    html.Div(id='whale-update', n_clicks=0, style={'display': 'none'}),
    html.Div(id='no_whale-update', n_clicks=0, style={'display': 'none'}),
    html.Div(id='filepath', style={'display': 'none'}),
])


@callback(
    Output('graph-content', 'src'),
    Output('title', 'children'),
    Output('audio-control', 'src'),
    Output('filepath', 'children'),
    Input('whale-update', 'n_clicks'),
    Input('no_whale-update', 'n_clicks')
)
def update_clip(whale_clicks, no_whale_clicks):
    my_clip = MarsClip(next(datafile_iter))
    fig_data = my_clip.get_spec_img_data()
    # fname = my_clip.get_filename()
    fpath = my_clip.get_filepath()
    title = f'MARS labler\n{fpath}'
    fig_plt = f'data:image/png;base64,{fig_data}' 
    return fig_plt, title, fpath, fpath


@callback(
    Output('whale-update', 'n_clicks'),
    Input('whale-val', 'n_clicks'),
    State('filepath', 'children')
)
def whale(n_clicks, filepath):
    n_clicks += 1
    return n_clicks


@callback(
    Output('no_whale-update', 'n_clicks'),
    Input('no_whale-val', 'n_clicks'),
    State('filepath', 'children')
)
def no_whale(n_clicks, filepath):
    n_clicks += 1
    return n_clicks


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8050, debug=True)