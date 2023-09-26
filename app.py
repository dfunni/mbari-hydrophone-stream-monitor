from dash import Dash, html, dcc, callback, clientside_callback, Output, Input, State, ctx, DiskcacheManager
import diskcache
from cetacean import MarsClip, pull_data
import plotly.express as px
import pandas as pd
from datetime import datetime
import json

import dash_mantine_components as dmc

import warnings
warnings.filterwarnings("ignore")

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

colorscales = px.colors.named_colorscales()

app = Dash(__name__, external_stylesheets=[dmc.theme.DEFAULT_COLORS])

app.layout = dmc.Container([ 
    dmc.Stack([      
        dmc.Title('MARS Data Tagger', id='title', style={'textAlign':'Left'}),
        dmc.SimpleGrid([
            dmc.Button('Pull', id='pull-btn', n_clicks=0, 
                       color="red", 
                       style={'width': "20%"}),
            html.Div(id='status-box', 
                     style={'textAlign': 'left'}),
            html.Div("Select Label:", 
                     style={'textAlign': 'right'}),
            dcc.Dropdown(id='label-dd', 
                         options=['unlabeled', 'no_whale', 'whale'], 
                         value='unlabeled'),
        ], cols=4),
        dmc.Group([
            dcc.Graph(id='graph-content', 
                      style={'align': 'left', 'width': "92%"}),
            dcc.RangeSlider(id='thresh-slider', min=0, max=60, value=[0, 60], vertical=True),
        ]),
        dmc.SimpleGrid([
            html.Audio(id='audio-control', controls=True),
            dmc.Stack([
                dcc.RadioItems(id='label-radio', options=['Next', 'whale', 'no_whale', 'delete'], value='Next'),
                dmc.Button('Submit / Next', id='submit-btn', n_clicks=0, color='red'),
            ]),
            html.Div("Colormap:", style={'textAlign': 'right'}),
            dcc.Dropdown(id='color-dropdown', options=colorscales, value='jet'),
        ], cols=4),
        dmc.Grid([      # stats
            dmc.Col(dcc.Markdown(id='stats-div'), span=3),
            dmc.Col(dcc.Graph(id='stats-pie'), span=3),
        ]),
    ], spacing='md'),
    html.Div([  # storage / hidden
        html.Div(id='filepath', hidden=True),
        html.Div(id='last-saved', hidden=True),
        html.Div(id='iter-state', children='{"whale": 0, "no_whale": 0}', hidden=True)
    ], hidden=True),
], fluid=True)


@callback(
    Output('filepath', 'children'),
    Output('iter-state', 'children'),
    Input('submit-btn', 'n_clicks'),
    Input('label-dd', 'value'),   
    State('iter-state', 'children'),
    State('label-radio', 'value'),
)
def update_file(n_clicks, label, iter_state, radio):
    df = pd.read_json('recordings.json')
    lbl_state = json.loads(iter_state)
    if label == 'unlabeled':
        try:
            next = df[df['label'].isna()].iloc[0]
        except:
            next = None
    else:
        idx = int(lbl_state[label])
        try:
            next = df[df['label'] == label].iloc[idx]
            lbl_state[label] = idx + 1  # increment location
        except:
            lbl_state[label] = 0        # loop back to the front
    if ctx.triggered_id == 'submit-btn':
        if radio == 'whale':
            df.loc[df['filename'] == next['filename'], 'label'] = 'whale'
        elif radio == 'no_whale':
            df.loc[df['filename'] == next['filename'], 'label'] = 'no_whale'
        elif radio == 'delete':
            print(f"dropping {next['filename']}")
            df.drop(df.loc[df['filename'] == next['filename']].index, inplace=True)
        else: # None
            pass
        df.to_json('recordings.json')
    
    return next.to_json(), json.dumps(lbl_state)


@callback(
    Output('stats-pie', 'figure'),
    Output('stats-div', 'children'),
    Input('filepath', 'children'),
    State('iter-state', 'children'),
    manager=background_callback_manager,
    prevent_initial_call=True,
)
def update_stats(next, iter_state):
    df = pd.read_json('recordings.json')
    iter_state = json.loads(iter_state)
    fig = px.pie(df, names='label')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(paper_bgcolor="#3a3f44",
                      font_color="#dee2e6",
                      autosize=False, 
                      width=350,
                      height=350)
    num_whale = df[df['label'] == 'whale'].__len__()
    num_nowhale = df[df['label'] == 'no_whale'].__len__()

    stats = f'''
        Total files | ........{df.__len__()}
        --- | ---: 
        Whale | {num_whale} 
        No Whale | {num_nowhale} 
        Unlabeled | {df['label'].isna().sum()}
        ___
        Index | current / total
        ---  | ---:
        Whale index | {iter_state['whale']} / {num_whale}
        No Whale index | {iter_state['no_whale']} / {num_nowhale}
        '''

    return fig, stats


@callback(
    Output('graph-content', 'figure'),
    Output('audio-control', 'src'),
    Input('filepath', 'children'),
    Input("color-dropdown", "value"),
    Input('thresh-slider', 'value'),
    manager=background_callback_manager,
    prevent_initial_call=True)
def update_plot(next, scale, thresh):
    next = json.loads(next)
    if ctx.triggered_id != None:
        clip = MarsClip(next['filename'])
        fig_data, f, t = clip.get_spec_img() 
        fig = px.imshow(fig_data, 
                            origin='lower',
                            title=f"{next['filename']} {next['label']}",
                            contrast_rescaling='infer',
                            zmin=thresh[0],
                            zmax=thresh[1],
                            color_continuous_scale=scale)
        fig.update_layout(paper_bgcolor="#3a3f44", font_color="#dee2e6", title_xref='paper', title_yref='paper')
        fpath = clip.get_filepath()
        return fig, fpath
    else:
        print('plot trigger error')
        return None, next


clientside_callback(
    """
    function updateLoadingState(n_clicks) {
        return true
    }
    """,
    Output("pull-btn", "loading", allow_duplicate=True),
    Input("pull-btn", "n_clicks"),
    manager=background_callback_manager,
    prevent_initial_call=True,
)
@callback(
    Output('status-box', 'children'),
    Output('pull-btn', 'loading'),
    Input('pull-btn', 'n_clicks'),
    manager=background_callback_manager,
    prevent_initial_call=True
)
def pull(n_clicks):
    dt = datetime.now()
    dt_string = dt.strftime("%d/%m/%Y %H:%M:%S")
    new_files = pull_data()
    new_dict = {"filename": new_files,
               "label": None}
    df1 = pd.read_json('recordings.json')
    df2 = pd.DataFrame.from_dict(new_dict)
    df = pd.concat([df1, df2], ignore_index=True)
    df = df.sort_values('filename', axis=0, ignore_index=True)
    df.to_json('recordings.json')
    msg = f'Pulled {len(new_files)} at {dt_string}'
    return msg, False


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8050, debug=True)