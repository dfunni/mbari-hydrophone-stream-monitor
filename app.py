from dash import Dash, html, dcc, callback, Output, Input, State, ctx
from cetacean import DataDir, MarsClip, pull_data
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime

import dash_mantine_components as dmc

import warnings
warnings.filterwarnings("ignore")

init_df = pd.read_json("recordings.json")
colorscales = px.colors.named_colorscales()
colors = {
    'background': '#3a3f44',

}

app = Dash(__name__, external_stylesheets=[dmc.theme.DEFAULT_COLORS])

app.layout = dmc.Container([
    
    dmc.Stack([      
        dmc.Title('MARS Data Tagger', id='title', style={'textAlign':'Left'}),
        html.Div('xx unlabled files', id='remaining', style={'textAlign':'Left'}),
        dmc.Grid([
            dmc.Col([
                dmc.Button('Pull', id='pull-btn', n_clicks=0, color="red"),
                dcc.Loading(id='loading-pull',
                        type="default",
                        children=html.Div(id='status-box'),
                ),
            ], span=2),
        ]),
        dcc.Graph(id='graph-content', 
            figure={'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],}
            }
        ),
        dcc.Dropdown(id='dropdown', options=colorscales, value='jet'), 
        html.Audio(id='audio-control', controls=True),
        dmc.Group([  # buttons
            dmc.Button('Whale', id='whale-btn', n_clicks=0, color="red"),
            dmc.Button('No Whale', id='nowhale-btn', n_clicks=0, color="red"),
            dmc.Button('Ignore', id='ignore-btn', n_clicks=0, color="red"),
        ]),
        dmc.Grid([      # stats
            dmc.Col(dcc.Markdown(id='stats-div'), span=6),
            dmc.Col(dcc.Graph(id='stats-pie'), span=6),
        ]),
    ], spacing='md'),
    
    
    html.Div([  # storage / hidden
        dcc.Store(id='tmp-data', data=init_df.to_json()),
        html.Div(id='filepath', hidden=True),
        html.Div(id='last-saved', hidden=True),
    ], hidden=True),
], fluid=True)


@callback(
    Output('filepath', 'children'),
    Output('remaining', 'children'),
    Output('stats-pie', 'figure'),
    Output('stats-div', 'children'),
    Output('tmp-data', 'data'),
    Input('whale-btn', 'n_clicks'),
    Input('nowhale-btn', 'n_clicks'),
    Input('ignore-btn', 'n_clicks'),
    State('tmp-data', 'data'),
    State('filepath', 'children'),
    
)
def update(w_clicks, n_clicks, i_clicks, data, old_file):
    btn_id = ctx.triggered_id
    df = pd.read_json("recordings.json")
    if btn_id == 'whale-btn':
        df.loc[df['filename'] == old_file, 'label'] = 'whale'
        df.to_json('recordings.json')
    elif btn_id == 'nowhale-btn':
        df.loc[df['filename'] == old_file, 'label'] = 'no_whale'
        df.to_json('recordings.json')
    elif btn_id == 'ignore-btn':
        print(f'dropping {old_file}')
        df.drop(df.loc[df['filename'] == old_file].index, inplace=True)
        df.to_json('recordings.json')
    else: # refresh
        pass
    num_remaining = df['label'].isna().sum()
    remaining_list = df[df['label'].isna()]['filename'].to_list()
    fig = px.pie(df, names='label', title='Stats:')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    stats = f'''
        Total files: | {df.__len__()}
        --- | ---: 
        Whale: | {df[df['label'] == 'whale'].__len__()} 
        No Whale: | {df[df['label'] == 'no_whale'].__len__()} 
        Unlabeled: | {num_remaining}'''
    return remaining_list[0], f'{num_remaining} unlabled files', fig, stats, df.to_json()
    

@callback(
    # Output('graph-content', 'src', allow_duplicate=True),
    Output('graph-content', 'figure'),
    Output('audio-control', 'src', allow_duplicate=True),
    Input('filepath', 'children'),
    Input("dropdown", "value"),
    prevent_initial_call=True)
def plot(filepath, scale):
    if ctx.triggered_id == 'filepath':
        print(f'plotting - {filepath}')
        clip = MarsClip(filepath)
        # fig_data = clip.get_spec_img_data()   ## for html.Img 
        # fig_plt = f'data:image/png;base64,{fig_data}'  ## for html.Img 
        fig_data, f, t = clip.get_spec_img() 
        fig_plt = px.imshow(fig_data, 
                            origin='lower',
                            title=filepath,
                            color_continuous_scale=scale)
        fpath = clip.get_filepath()
        
        return fig_plt, fpath
    
@callback(
    Output('status-box', 'children'),
    Input('pull-btn', 'n_clicks'),
    State('tmp-data', 'data'),
    prevent_initial_call=True
)
def pull(n_clicks, data):
    dt = datetime.now()
    dt_string = dt.strftime("%d/%m/%Y %H:%M:%S")
    new_files = pull_data()
    new_dict = {"filename": new_files,
               "label": None}
    df1 = pd.read_json(data)
    df2 = pd.DataFrame.from_dict(new_dict)
    df = pd.concat([df1, df2], ignore_index=True)
    df = df.sort_values('filename', axis=0, ignore_index=True)
    df.to_json('recordings.json')
    return f'Pulled {len(new_files)} at {dt_string}'


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8050, debug=True)