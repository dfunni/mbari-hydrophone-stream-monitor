#!/usr/local/bin/python

from dash import Dash, html, dcc, callback, clientside_callback, Output, Input, State, ctx, DiskcacheManager, dash_table
import dash_mantine_components as dmc
import diskcache
import plotly.express as px
import pandas as pd
from datetime import datetime
import json
import os

from utils import MarsClip, pull_data


import warnings
warnings.filterwarnings("ignore")

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

## plot colorscale options
colorscales = px.colors.named_colorscales()
initial_file = os.listdir('assets/data/')[0]
data_dd_options = ['unlabeled', 'whale+', 'whale', 'no_whale']

## Table initialization
stats_totals_cols = [{'name' : 'Label', 'id' : 'Label'}, 
                     {'name' : 'Count', 'id' : 'Count'}]
stats_totals = [{'Label': 'Whale+', 'Count': 0},
                {'Label': 'Whale', 'Count': 0},
                {'Label': 'No Whale', 'Count':  0},
                {'Label': 'Unlabeled', 'Count':  0},
                {'Label': 'Total files', 'Count': 0}]
stats_idx_cols = [{'name' : 'Index', 'id' : 'Index'}, 
                  {'name' : 'current / total', 'id' : 'current / total'}]
stats_idx = [{'Index': 'Whale+ index', 'current / total': "0 / 0"},
             {'Index': 'Whale index', 'current / total': "0 / 0"},
             {'Index': 'No Whale index', 'current / total':  "0 / 0"},
             {'Index': 'No Whale index', 'current / total':  "0 / 0"}]


app = Dash(__name__, external_stylesheets=[dmc.theme.DEFAULT_COLORS])


app.layout = dmc.Container([ 
    dmc.Stack([      
        dmc.Title('MARS Data Tagger', id='title', style={'textAlign':'Left'}),
        dmc.SimpleGrid([    ## Pull functions
            dmc.Group([
                dmc.Button('Pull', id='pull-btn', n_clicks=0, 
                        color="red", 
                        style={'width': "20%"}),
                html.Div(id='status-box', 
                        style={'textAlign': 'left'}),
            ]),
            html.Div(),
            dcc.Input(id='file-input', 
                          type='text', 
                          placeholder='',
                          debounce=True),
            html.Div(id='next', children=''),
        ], cols=4),
        dmc.Group([         ## Graph
            dcc.Graph(id='graph-content', 
                        style={'align': 'left', 'width': "92%"}),
        ]),
        dmc.SimpleGrid([    ## Controls and view options
            dmc.Stack([         ## Audio control
                html.Audio(id='audio-control', controls=True, autoPlay=True),
            ]),
            dmc.Stack([         ## Data tagging UI
                dmc.Group([         ## tag select radios
                    html.B('Tag:'),
                    dcc.RadioItems(id='label-radio', 
                                options=['Next', 'whale+', 'whale', 'no_whale', 'delete'], 
                                value='Next',
                                inline=True,
                                # labelStyle={'margin-right': "20px"},
                                inputStyle={'margin-right': "5px",
                                            'margin-left': "20px"}),
                ]),
                dmc.Group([         ## control buttons
                    dmc.Button('Submit / Next', id='submit-btn', n_clicks=0, color='red'),
                    dmc.Button("Refresh Plot", id='refresh-btn', n_clicks=0, color="red",),
                ]),
            ]),
            dmc.Stack([         ## View by class label
                html.B('Data to view:'),
                dcc.Dropdown(id='label-dd', 
                             options=data_dd_options, 
                             value='unlabeled'),
            ]),
            dmc.Stack([         ## Plot colormap select
                html.B('Plot colormap:'),
                dcc.Dropdown(id='color-dropdown', 
                             options=colorscales, 
                             value='jet'),
            ]),
        ], cols=4),
        dmc.SimpleGrid([    ## Stats, index select, and threshold
            dmc.Stack([         ## Index locations
                dash_table.DataTable(id='stats-index', 
                                 data=stats_idx, 
                                 columns=stats_idx_cols,
                                 style_cell={'textAlign': 'left',
                                             'backgroundColor': "#3a3f44",
                                             'color': "#dee2e6"},
                                 style_header={'fontWeight': 'bold'},
                                 style_data={}),
                dmc.Stack([
                    dmc.Grid([
                        dmc.Col([
                            html.B('Whale+ index:'),
                        ], span=4),
                        dmc.Col([
                            dcc.Input(id="whale+-inpt", type="number", debounce=True, value=0),
                        ], span=1),
                    ]),
                    dmc.Grid([
                        dmc.Col([
                            html.B('Whale index:'),
                        ], span=4),
                        dmc.Col([
                            dcc.Input(id="whale-inpt", type="number", debounce=True, value=0),
                        ], span=1),
                    ]),
                    dmc.Grid([
                        dmc.Col([
                            html.B('No Whale index:'),
                        ], span=4),
                        dmc.Col([
                            dcc.Input(id="nowhale-inpt", type="number", debounce=True, value=0),
                        ], span=1),
                    ]),
                ]),
            ]),
            dmc.Stack([         ## Stats Table
                dash_table.DataTable(id='stats-totals',
                                    data=stats_totals,
                                    columns=stats_totals_cols,
                                    style_cell={'textAlign': 'left',
                                                'backgroundColor': "#3a3f44",
                                                'color': "#dee2e6"},
                                    style_header={'fontWeight': 'bold'}),
            ]),
            dmc.Stack([         ## Stats pie graph
                dcc.Graph(id='stats-pie'),
            ]),
            dmc.Stack([         ## Threshold control
                html.B('Colormap thresholds:'),
                dcc.RangeSlider(id='thresh-slider', min=0, max=60, value=[0, 60]),
            ]),
        ], cols=4),
    ], spacing='md'),

    html.Div([  # storage / hidden
        html.Div(id='filepath', children=initial_file),
        html.Div(id='last-saved'),
        html.Div(id='iter-state', children='{"whale+": 0, "whale": 0, "no_whale": 0, "unlabeled": 0}')
    ], hidden=True),
], fluid=True)


@callback(
    Output('iter-state', 'children'),
    Output('filepath', 'children'),
    Output('file-input', 'placeholder'),
    Output("whale+-inpt", "value"),
    Output("whale-inpt", "value"),
    Output("nowhale-inpt", "value"),
    Output('label-dd', 'value'),
    Input('label-dd', 'value'),
    Input('next', 'children'), # dummy signal
    Input("whale+-inpt", "value"),
    Input("whale-inpt", "value"),
    Input("nowhale-inpt", "value"),
    Input('file-input', 'value'),
    State('iter-state', 'children'))
def get_file(label_dd, next, whalep_inpt, whale_inpt, nwhale_inpt, txt_inpt, iter_state):
    """Taking any of the file select inputs, return the file selected, update onscreent 
    text and index state"""

    df = pd.read_json('recordings.json')
    state = json.loads(iter_state)

    def default(df):
        try:        # show first unlabeled file if there is one
            filepath = df[df['label'].isna()].iloc[0]
        except:     # error: show the first whale+
            filepath = df[df['label'] == 'whale+'].iloc[0]
        return filepath

    inpt = ctx.triggered_id
    if inpt == 'whale-inpt' or inpt == 'nowhale-inpt' or inpt == 'whale+-inpt':
        # update the state and change the file if label same as dropdown
        state['whale+'] = max(whalep_inpt, 0)
        state['whale'] = max(whale_inpt, 0)
        state['no_whale'] = max(nwhale_inpt, 0)
        try:
            filepath = df[df['label'] == label_dd].iloc[state[label_dd]]
        except:
            print('failed index update')
            filepath = default(df)

    elif inpt == 'file-input':
        # change the label dropdown and class index and display file
        try:
            filepath = df[df['filename'] == txt_inpt].iloc[0]
            label = filepath['label']
            subdf = df[df['label'] == label].reset_index()
            idx = subdf[subdf['filename'] == txt_inpt].index.item()
            state[label] = idx
            label_dd = label
        except:
            print('failed file input')
            filepath = default(df)
            label_dd = 'unlabeled'

    elif inpt == 'next' and label_dd != 'unlabeled': # relabling file
        # roll back the correct class index in state and get next file in class
        updated = next.split(' ')[-1] # get the label
        if updated != 'Next': # relabeling
            state[label_dd] -= 1 # roll back to the previous index
        else:
            state[label_dd] += 1
        try:
            filepath = df[df['label'] == label_dd].iloc[state[label_dd]]
        except:
            print('failed next button press')
            filepath = default(df)

    elif inpt == 'next' and label_dd == 'unlabeled':
        # not allowed, show same file
        filepath = default(df)

    elif inpt == 'label-dd':
        ## show currently indexed file of the selected class
        try:
            filepath = df[df['label'] == label_dd].iloc[state[label_dd]]
        except:
            print('failed drop-down select')
            filepath = default(df)

    
    else: #initial run
        # display first unalbeled file, if none show first whale+
        filepath = default(df)

    return json.dumps(state), filepath.to_json(), filepath['filename'], state['whale+'], state['whale'], state['no_whale'], label_dd


@callback(
    Output('graph-content', 'figure'),
    Output('audio-control', 'src'),
    Input('filepath', 'children'),
    Input("color-dropdown", "value"),
    Input('thresh-slider', 'value'),
    Input('refresh-btn', 'n_clicks'),
    manager=background_callback_manager,
    )
def update_plot(filepath, scale, thresh, refresh):
    filepath = json.loads(filepath)
    if ctx.triggered_id != None:
        clip = MarsClip(filepath['filename'])
        fig_data, _, _ = clip.get_spec_img() 
        fig = px.imshow(fig_data, 
                        origin='lower',
                        title=f"{filepath['filename']} {filepath['label']}",
                        contrast_rescaling='infer',
                        zmin=thresh[0],
                        zmax=thresh[1],
                        color_continuous_scale=scale)
        fig.update_layout(paper_bgcolor="#3a3f44", font_color="#dee2e6", title_xref='paper', title_yref='paper', title_x=1)
        fpath = clip.get_filepath()
        return fig, fpath
    else:
        print('plot trigger error')
        return None, filepath


@callback(
    Output('next', 'children'),
    Input('submit-btn', 'n_clicks'),
    State('label-radio', 'value'),
    State('filepath', 'children'),
    prevent_initial_call=True,)
def submit(click, radio, filepath):
    df = pd.read_json('recordings.json')
    filepath = json.loads(filepath)
    if ctx.triggered_id == 'submit-btn':
        if radio == 'whale+':
            df.loc[df['filename'] == filepath['filename'], 'label'] = 'whale+'
        elif radio == 'whale':
            df.loc[df['filename'] == filepath['filename'], 'label'] = 'whale'
        elif radio == 'no_whale':
            df.loc[df['filename'] == filepath['filename'], 'label'] = 'no_whale' 
        elif radio == 'delete':
            print(f"dropping {filepath['filename']}")
            df.drop(df.loc[df['filename'] == filepath['filename']].index, inplace=True)
        else: # Next
            pass
        df.to_json('recordings.json')
    return f"{filepath['filename']} marked {radio}"


@callback(
    Output('stats-pie', 'figure'),
    Output('stats-totals', 'data'),
    Output('stats-index', 'data'),
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
    num_whalep = df[df['label'] == 'whale+'].__len__()
    num_whale = df[df['label'] == 'whale'].__len__()
    num_nowhale = df[df['label'] == 'no_whale'].__len__()

    stats_totals = [{'Label': 'Whale+', 'Count': num_whalep},
                    {'Label': 'Whale', 'Count': num_whale},
                    {'Label': 'No Whale', 'Count': num_nowhale},
                    {'Label': 'Unlabeled', 'Count':  df['label'].isna().sum()},
                    {'Label': 'Total files', 'Count': df.__len__()}]
    stats_index = [{'Index': 'Whale+ index', 'current / total': f"{iter_state['whale+']} / {num_whalep}"},
                   {'Index': 'Whale index', 'current / total': f"{iter_state['whale']} / {num_whale}"},
                   {'Index': 'No Whale index', 'current / total':  f"{iter_state['no_whale']} / {num_nowhale}"}]
    return fig, stats_totals, stats_index


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