from dash import Dash, html, dcc, callback, clientside_callback, Output, Input, State, ctx, DiskcacheManager, dash_table
import diskcache
from cetacean import MarsClip, pull_data
import plotly.express as px
import pandas as pd
from datetime import datetime
import json
import os

import dash_mantine_components as dmc

import warnings
warnings.filterwarnings("ignore")

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

## plot colorscale options
colorscales = px.colors.named_colorscales()
initial_file = os.listdir('assets/data/')[0]

## Table initialization
stats_totals_cols = [{'name' : 'Label', 'id' : 'Label'}, 
                     {'name' : 'Count', 'id' : 'Count'}]
stats_totals = [{'Label': 'Whale index', 'Count': 0},
                {'Label': 'No Whale index', 'Count':  0},
                {'Label': 'Unlabeled', 'Count':  0},
                {'Label': 'Total files', 'Count': 0}]
stats_idx_cols = [{'name' : 'Index', 'id' : 'Index'}, 
                  {'name' : 'current / total', 'id' : 'current / total'}]
stats_idx = [{'Index': 'Whale index', 'current / total': "0 / 0"},
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
            html.Div(),
            html.Div(),
        ], cols=4),
        dmc.Group([         ## Graph
            dcc.Graph(id='graph-content', 
                      style={'align': 'left', 'width': "92%"}),
            dcc.RangeSlider(id='thresh-slider', min=0, max=60, value=[0, 60], vertical=True),
        ]),
        dmc.SimpleGrid([    ## Controls and options
            dmc.Stack([
                html.Audio(id='audio-control', controls=True),
            ]),
            dmc.Stack([
                dmc.Group([
                    html.B('Tag:'),
                    dcc.RadioItems(id='label-radio', 
                                options=['Next', 'whale', 'no_whale', 'delete'], 
                                value='Next',
                                inline=True,
                                # labelStyle={'margin-right': "20px"},
                                inputStyle={'margin-right': "5px",
                                            'margin-left': "20px"}),
                ]),
                dmc.Button('Submit / Next', id='submit-btn', n_clicks=0, color='red'),
            ]),
            dmc.Stack([     ## statistics
                html.B('Plot colormap:'),
                dcc.Dropdown(id='color-dropdown', 
                             options=colorscales, 
                             value='jet'),
            ]),
            dmc.Stack([
                html.B('Data to view:'),
                dcc.Dropdown(id='label-dd', 
                             options=['unlabeled', 'no_whale', 'whale'], 
                             value='unlabeled'),
            ]),
        ], cols=4),
        dmc.SimpleGrid([    ## Stats
            dmc.Stack([
                dash_table.DataTable(id='stats-index', 
                                 data=stats_idx, 
                                 columns=stats_idx_cols,
                                 style_cell={'textAlign': 'left',
                                             'backgroundColor': "#3a3f44",
                                             'color': "#dee2e6"},
                                 style_header={'fontWeight': 'bold'},
                                 style_data={}),
                dmc.Group([
                    dcc.Input(id="whale-inpt", type="number", debounce=True, value=0),
                    dcc.Input(id="nowhale-inpt", type="number", debounce=True, value=0),
                ]),
            ]),
            dash_table.DataTable(id='stats-totals',
                                 data=stats_totals,
                                 columns=stats_totals_cols,
                                 style_cell={'textAlign': 'left',
                                             'backgroundColor': "#3a3f44",
                                             'color': "#dee2e6"},
                                 style_header={'fontWeight': 'bold'}),
            dcc.Graph(id='stats-pie'),
            html.Div(),
        ], cols=4),
    ], spacing='md'),

    html.Div([  # storage / hidden
        html.Div(id='filepath', children=initial_file, hidden=True),
        html.Div(id='next', hidden=True),
        html.Div(id='last-saved', hidden=True),
        html.Div(id='iter-state', children='{"whale": 0, "no_whale": 0}', hidden=True)
    ], hidden=True),
], fluid=True)


@callback(
    Output('iter-state', 'children'),
    Output('filepath', 'children'),
    Output("whale-inpt", "value"),
    Output("nowhale-inpt", "value"),
    Input('label-dd', 'value'),
    Input('next', 'children'), # dummy signal
    Input("whale-inpt", "value"),
    Input("nowhale-inpt", "value"),
    State('iter-state', 'children'))
def get_file(label, next, whale_inpt, nwhale_inpt, iter_state):
    df = pd.read_json('recordings.json')
    state = json.loads(iter_state)
    
    if ctx.triggered_id == 'whale-inpt' or ctx.triggered_id == 'nowhale-inpt':
        state['whale'] = max(whale_inpt - 1, 0)
        state['no_whale'] = max(nwhale_inpt - 1, 0)
    
    if label == 'unlabeled':
        try:
            filepath = df[df['label'].isna()].iloc[0]
        except:     # error: show the first whale
            filepath = df[df['label'] == 'whale'].iloc[0]
    else:
        idx = int(state[label])
        try:
            filepath = df[df['label'] == label].iloc[idx]
            state[label] = idx + 1
        except:     # loop back to the front
            filepath = df[df['label'] == label].iloc[0]
            state[label] = 0
        whale_inpt = state['whale']
        nwhale_inpt = state['no_whale']
    return json.dumps(state), filepath.to_json(), whale_inpt, nwhale_inpt


@callback(
    Output('graph-content', 'figure'),
    Output('audio-control', 'src'),
    Input('filepath', 'children'),
    Input("color-dropdown", "value"),
    Input('thresh-slider', 'value'),
    manager=background_callback_manager,
    )
def update_plot(filepath, scale, thresh):
    filepath = json.loads(filepath)
    if ctx.triggered_id != None:
        clip = MarsClip(filepath['filename'])
        fig_data, f, t = clip.get_spec_img() 
        fig = px.imshow(fig_data, 
                        origin='lower',
                        title=f"{filepath['filename']} {filepath['label']}",
                        contrast_rescaling='infer',
                        zmin=thresh[0],
                        zmax=thresh[1],
                        color_continuous_scale=scale)
        fig.update_layout(paper_bgcolor="#3a3f44", font_color="#dee2e6", title_xref='paper', title_yref='paper')
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
        if radio == 'whale':
            df.loc[df['filename'] == filepath['filename'], 'label'] = 'whale'
        elif radio == 'no_whale':
            df.loc[df['filename'] == filepath['filename'], 'label'] = 'no_whale' 
        elif radio == 'delete':
            print(f"dropping {filepath['filename']}")
            df.drop(df.loc[df['filename'] == filepath['filename']].index, inplace=True)
        else: # None
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
    num_whale = df[df['label'] == 'whale'].__len__()
    num_nowhale = df[df['label'] == 'no_whale'].__len__()

    stats_totals = [{'Label': 'Whale index', 'Count': num_whale},
                    {'Label': 'No Whale index', 'Count': num_nowhale},
                    {'Label': 'Unlabeled', 'Count':  df['label'].isna().sum()},
                    {'Label': 'Total files', 'Count': df.__len__()}]
    stats_index = [{'Index': 'Whale index', 'current / total': f"{iter_state['whale']} / {num_whale}"},
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