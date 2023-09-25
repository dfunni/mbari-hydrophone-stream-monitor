from dash import Dash, html, dcc, callback, Output, Input, State, ctx
from cetacean import DataDir, MarsClip, pull_data
import logging
import warnings
warnings.filterwarnings("ignore")

app = Dash(__name__)


## Setup
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
    html.Div(id='filepath', hidden=True),
    html.Div(id='whale-update', n_clicks=0, hidden=True),
    html.Div(id='no_whale-update', n_clicks=0, hidden=True),
    html.Div(id='next', n_clicks=0, hidden=True),
])



@callback(
    Output('filepath', 'children'),
    Output('graph-content', 'src'),
    Output('audio-control', 'src'),
    Input('next', 'n_clicks'),
    prevent_initial_call=True)
def update_clip(click):
    trigger = ctx.triggered_id
    if trigger == 'next':
        print(trigger)
        clip = MarsClip(next(datafile_iter))
        fpath = clip.get_filepath()
        del clip
        print(f'updated - {fpath}')
        return fpath, '', ''
    else:
        pass


@callback(
    Output('graph-content', 'src', allow_duplicate=True),
    Output('title', 'children'),
    Output('audio-control', 'src', allow_duplicate=True),
    Input('filepath', 'children'),
    prevent_initial_call=True)
def plot(filepath):
    if ctx.triggered_id == 'filepath':
        print(f'plotting - {filepath}')
        clip = MarsClip(filepath)
        fig_data = clip.get_spec_img_data()
        fpath = clip.get_filepath()
        del clip
        title = f'MARS labler\n{fpath}'
        fig_plt = f'data:image/png;base64,{fig_data}' 
        return fig_plt, title, fpath


@callback(
    Output('whale-update', 'n_clicks'),
    Input('whale-val', 'n_clicks'),
    State('filepath', 'children'),
    prevent_initial_call=True)
def whale(n_clicks, filepath):
    clip = MarsClip(filepath)
    clip.mv_whale()
    del clip
    print(f'marking - whale')
    return n_clicks


@callback(
    Output('no_whale-update', 'n_clicks'),
    Input('no_whale-val', 'n_clicks'),
    State('filepath', 'children'),
    prevent_initial_call=True)
def no_whale(n_clicks, filepath):
    clip = MarsClip(filepath)
    clip.mv_nowhale()
    del clip
    print(f'marking - nowhale')
    return n_clicks


@callback(
    Output('next', 'n_clicks', allow_duplicate=True),
    Input('whale-update', 'n_clicks'),
    Input('no_whale-update', 'n_clicks'),
    prevent_initial_call=True)
def clear(whale_clicks, nowhale_clicks):
    print('clearing')
    n_clicks = whale_clicks + nowhale_clicks
    return n_clicks





if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8050, debug=True)