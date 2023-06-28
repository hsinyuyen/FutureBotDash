import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import plotly.graph_objs as go
import random
import pandas as pd
from collections import deque
import flask
import time
import dash_bootstrap_components as dbc
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask import Flask, request, url_for, redirect

# deque is used to keep a fixed length list.
# When new elements are added to one end of the list, an equal number are removed from the other end.
import pygsheets


gc = pygsheets.authorize(service_file='C:/Users/User/FuturesBotDash/future-bot1-114f3146bb57.json')
sht = gc.open_by_url(
'https://docs.google.com/spreadsheets/d/1m0vDyHCdCSAubRcyD9c1i1fE50AYb0YH4UFtM75toSQ/edit?usp=sharing'
)
wks_list = sht.worksheets()
#選取by順序
wks = sht[0]
 
#讀取成 df

global df
df = pd.DataFrame(wks.get_all_records())[-200:]

def make_fig(attribute):
    df = pd.DataFrame(wks.get_all_records())[-200:]
    time= deque(maxlen=1000)
    attribute_name= deque(maxlen=1000)
    

    time.extend(df.index)
    attribute_name.extend(df[attribute].values)

    data = go.Scatter(
            
            x=list(time),
            y=list(attribute_name),
            name='Scatter',
            mode= 'lines+markers'
    )
    return data, time, attribute_name



app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server=app.server
# Flask-Login user loader callback
app.layout = html.Div([
  dcc.Location(id='url', refresh=False),
  html.Div(id='page-content')
                     ])

index_page = html.Div([
html.Div(
dcc.Input(id="user", type="text", placeholder="Enter Username",className="inputbox1",
style={'margin-left':'35%','width':'450px','height':'45px','padding':'10px','margin-top':'60px',
'font-size':'16px','border-width':'3px','border-color':'#a0a3a2'
}),
),
html.Div(
dcc.Input(id="passw", type="text", placeholder="Enter Password",className="inputbox2",
style={'margin-left':'35%','width':'450px','height':'45px','padding':'10px','margin-top':'10px',
'font-size':'16px','border-width':'3px','border-color':'#a0a3a2',
}),
),
html.Div(
html.Button('Verify', id='verify', n_clicks=0, style={'border-width':'3px','font-size':'14px'}),
style={'margin-left':'45%','padding-top':'30px'}),
html.Div(id='output1')
])

@app.callback(
    dash.dependencies.Output('output1', 'children'),
   [dash.dependencies.Input('verify', 'n_clicks')],
    [State('user', 'value'),
    State('passw', 'value')])
def update_output(n_clicks, uname, passw):
    li={'123':'123'}
    if uname =='' or uname == None or passw =='' or passw == None:
        return html.Div(children='',style={'padding-left':'550px','padding-top':'10px'})
    if uname not in li:
        return html.Div(children='Incorrect Username',style={'padding-left':'550px','padding-top':'40px','font-size':'16px'})
    if li[uname]==passw:
        return html.Div(dcc.Link('Access Granted!', href='/next_page',style={'color':'#183d22','font-family': 'serif', 'font-weight': 'bold', "text-decoration": "none",'font-size':'20px'}),style={'padding-left':'605px','padding-top':'40px'})
    else:
        return html.Div(children='Incorrect Password',style={'padding-left':'550px','padding-top':'40px','font-size':'16px'})


next_page = html.Div(
    [   
    html.Div(dcc.Link('Log out', href='/',style={'color':'#bed4c4','font-family': 'serif', 'font-weight': 'bold', "text-decoration": "none",'font-size':'20px'}),style={'padding-left':'80%','padding-top':'10px'}),
        html.H1(children="This is the Next Page, the main Page",className="ap",style={
 'color':'#89b394','text-align':'center','justify':'center','padding-top':'170px','font-weight':'bold',
 'font-family':'courier',
 'padding-left':'1px'  }),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='live-micro_Price', animate=True),
                #html.Div(id='display-value')
            ],width=4),
            dbc.Col([
                dcc.Graph(id='live-interval', animate=True),
            ],width=4),
            dbc.Col([
                dcc.Graph(id='live-short_ema', animate=True),
            ],width=4)
            
        ]),



        dbc.Row([
            
            dbc.Col([
                dcc.Graph(id='live-signal_std', animate=True),             
            ],width=4),
            dbc.Col([
                dcc.Graph(id='live-long_ema_2trend', animate=True),             
            ],width=4),
             dbc.Col([
                dcc.Graph(id='live-preMove', animate=True),             
            ],width=4)

        ]),

        dbc.Row([
            
            dbc.Col([
                dcc.Graph(id='live-overStd', animate=True),             
            ],width=4),
            dbc.Col([
                dcc.Graph(id='live-pressure', animate=True),             
            ],width=4),
             dbc.Col([
                dcc.Graph(id='live-fluctionRate', animate=True),             
            ],width=4)

        ]),

        dbc.Row([
            
            
            dbc.Col([
                dcc.Graph(id='live-stopLoss', animate=True),             
            ],width=4),
             dbc.Col([
                dcc.Graph(id='live-ratio', animate=True),             
            ],width=4),
             dbc.Col([
                dcc.Graph(id='live-coverPositionFlag', animate=True),             
            ],width=4),
             

        ]),

        

        dbc.Row([
            
            
            dbc.Col([
                dcc.Graph(id='live-resetflag', animate=True),             
            ],width=4),
             dbc.Col([
                dcc.Graph(id='live-isSettlement', animate=True),             
            ],width=4),
            dbc.Col([
                dcc.Graph(id='live-preMoveFlag', animate=True),             
            ],width=4),

        ]),
        
                
        dcc.Interval(
            id='interval-component',
            interval=300*1000,  # in milliseconds
            n_intervals=0
        )
    ]
)

@app.callback(Output('live-micro_Price', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_micro_Price(n):
    df = pd.DataFrame(wks.get_all_records())[-200:]
    time= deque(maxlen=1000)
    micro_Price= deque(maxlen=1000)
    limitAskPrice= deque(maxlen=1000)
    limitBidPrice= deque(maxlen=1000)

    

    time.extend(df.index)
    micro_Price.extend(df.micro_Price.values)
    limitAskPrice.extend(df.limitAskPrice.values)
    limitBidPrice.extend(df.limitBidPrice.values)

    data0 = go.Scatter(
            x=list(time),
            y=list(micro_Price),
            name='micro_Price',
            mode= 'lines'
    )

    data1 = go.Scatter(
            x=list(time),
            y=list(limitAskPrice),
            name='limitAskPrice',
            mode= 'lines'
    )

    data2 = go.Scatter(
            x=list(df.index),
            y=list(limitBidPrice),
            name='limitBidPrice',
            mode= 'lines'
    )


    return {'data': [data0, data1, data2],
            'layout' : go.Layout(xaxis=dict(range=[min(df.index),max(df.index)]),
                                  yaxis=dict( tickformat=".0f"),
                                                width=640
                                  )}



@app.callback(Output('live-short_ema', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_short_ema(n):
    df = pd.DataFrame(wks.get_all_records())[-200:]
    time= deque(maxlen=1000)
    signal_ma= deque(maxlen=1000)
    short_ema= deque(maxlen=1000)
    long_ema= deque(maxlen=1000)
    long_ema2= deque(maxlen=1000)
    

    time.extend(df.index)
    signal_ma.extend(df.signal_ma.values)
    short_ema.extend(df.short_ema.values)
    long_ema.extend(df.long_ema.values)
    long_ema2.extend(df.long_ema2.values)

    data0 = go.Scatter(
            x=list(time),
            y=list(signal_ma),
            name='signal_ma',
            mode= 'lines'
    )

    data1 = go.Scatter(
            x=list(time),
            y=list(short_ema),
            name='short_ema',
            mode= 'lines'
    )

    data2 = go.Scatter(
            x=list(df.index),
            y=list(long_ema),
            name='long_ema',
            mode= 'lines'
    )

    data3 = go.Scatter(
            x=list(df.index),
            y=list(long_ema2),
            name='long_ema2',
            mode= 'lines'
    )
    return {'data': [data0, data1, data2, data3],
            'layout' : go.Layout(xaxis=dict(range=[min(df.index),max(df.index)]),
                                  yaxis=dict( tickformat=".0f"),
                                                width=640
                                  )}

@app.callback(Output('live-signal_std', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_short_ema(n):
    df = pd.DataFrame(wks.get_all_records())[-200:]
    time= deque(maxlen=1000)
    signal_std= deque(maxlen=1000)
    short_ema_std= deque(maxlen=1000)
    short_std= deque(maxlen=1000)
    long_ema_std= deque(maxlen=1000)
    

    time.extend(df.index)
    signal_std.extend(df.signal_std.values)
    short_ema_std.extend(df.short_ema_std.values)
    short_std.extend(df.short_std.values)
    long_ema_std.extend(df.long_ema_std.values)

    data0 = go.Scatter(
            x=list(time),
            y=list(signal_std),
            name='signal_std',
            mode= 'lines'
    )

    data1 = go.Scatter(
            x=list(time),
            y=list(short_ema_std),
            name='short_ema_std',
            mode= 'lines'
    )

    data2 = go.Scatter(
            x=list(df.index),
            y=list(short_std),
            name='short_std',
            mode= 'lines'
    )

    data3 = go.Scatter(
            x=list(df.index),
            y=list(long_ema_std),
            name='long_ema_std',
            mode= 'lines'
    )
    return {'data': [data0, data1, data2, data3],
            'layout' : go.Layout(xaxis=dict(range=[min(df.index),max(df.index)]),
                                  yaxis=dict( tickformat=".0f"),
                                                width=640
                                  )}


@app.callback(Output('live-long_ema_2trend', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_long_ema_2trend(n):
    df = pd.DataFrame(wks.get_all_records())[-200:]
    time= deque(maxlen=1000)
    signal_ma= deque(maxlen=1000)
    long_ema_2trend= deque(maxlen=1000)
    time.extend(df.index)
    signal_ma.extend(df.signal_ma.values)
    long_ema_2trend.extend(df.long_ema_2trend.values)

    data0 = go.Scatter(
            x=list(time),
            y=list(signal_ma),
            name='signal_ma',
            mode= 'lines'
    )
    data1 = go.Scatter(
            x=list(time),
            y=list(long_ema_2trend),
            name='long_ema_2trend',
            mode= 'lines'
    )
    return {'data': [data0, data1],
            'layout' : go.Layout(xaxis=dict(range=[min(df.index),max(df.index)]),
                                  yaxis=dict( tickformat=".0f"),
                                                width=640
                                  )}
    


@app.callback(Output('live-preMove', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_preMove(n):
    df = pd.DataFrame(wks.get_all_records())[-200:]
    time= deque(maxlen=1000)
    preMove= deque(maxlen=1000)
    preMove2= deque(maxlen=1000)
    

    time.extend(df.index)
    preMove.extend(df.preMove.values)
    preMove2.extend(df.preMove2.values)

    data0 = go.Scatter(
            x=list(time),
            y=list(preMove),
            name='preMove',
            mode= 'lines'
    )

    data1 = go.Scatter(
            x=list(time),
            y=list(preMove2),
            name='preMove2',
            mode= 'lines'
    )

    return {'data': [data0, data1],
            'layout' : go.Layout(xaxis=dict(range=[min(df.index),max(df.index)]),
                                  yaxis=dict( tickformat=".0f"),
                                                width=640
                                  )}

@app.callback(Output('live-overStd', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_overStd(n):
    data, time, overStd=make_fig("overStd")
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(time),max(time)],tickformat=".0f"),
                                                yaxis=dict(tickformat=".0f"),
                                                title='overStd',
                                                width=640
                                                )}

@app.callback(Output('live-pressure', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_pressure(n):
    data, time, pressure=make_fig("pressure")
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(time),max(time)],tickformat=".0f"),
                                                yaxis=dict(tickformat=".0f"),
                                                title='pressure',
                                                width=640
                                                )}   


@app.callback(Output('live-fluctionRate', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_fluctionRate(n):
    data, time, fluctionRate=make_fig("fluctionRate")
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(time),max(time)],tickformat=".0f"),
                                                yaxis=dict(tickformat=".0f"),
                                                title='fluctionRate',
                                                width=640
                                                )}   



@app.callback(Output('live-stopLoss', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_stopLoss(n):
    data, time, stopLoss=make_fig("stopLoss")
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(time),max(time)],tickformat=".0f"),
                                                yaxis=dict(tickformat=".0f"),
                                                title='stopLoss',
                                                width=640
                                                )} 

@app.callback(Output('live-ratio', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_ratio(n):
    data, time, ratio=make_fig("ratio")
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(time),max(time)],tickformat=".0f"),
                                                yaxis=dict(tickformat=".0f"),
                                                title='ratio',
                                                width=640
                                                )}  

@app.callback(Output('live-interval', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_interval(n):
    data, time, ratio=make_fig("interval")
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(time),max(time)],tickformat=".0f"),
                                                yaxis=dict(tickformat=".0f"),
                                                title='interval',
                                                width=640
                                                )}  



@app.callback(Output('live-resetflag', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_limitBidPrice(n):
    data, time, ratio=make_fig("resetflag")
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(time),max(time)],tickformat=".0f"),
                                                yaxis=dict(tickformat=".0f"),
                                                title='resetflag',
                                                width=640
                                                )}  

@app.callback(Output('live-isSettlement', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_limitBidPrice(n):
    data, time, ratio=make_fig("isSettlement")
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(time),max(time)],tickformat=".0f"),
                                                yaxis=dict(tickformat=".0f"),
                                                title='isSettlement',
                                                width=640
                                                )}  

@app.callback(Output('live-preMoveFlag', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_limitBidPrice(n):
    data, time, ratio=make_fig("preMoveFlag")
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(time),max(time)],tickformat=".0f"),
                                                yaxis=dict(tickformat=".0f"),
                                                title='preMoveFlag',
                                                width=640
                                                )}  
@app.callback(Output('live-coverPositionFlag', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_coverPositionFlag(n):
    data, time, ratio=make_fig("coverPositionFlag")
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(time),max(time)],tickformat=".0f"),
                                                yaxis=dict(tickformat=".0f"),
                                                title='coverPositionFlag',
                                                width=640
                                                )}  

@app.callback(dash.dependencies.Output('page-content', 'children'),
[dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/next_page':
        return next_page
    else:
       return index_page

if __name__ == '__main__':
    app.run_server(debug=True)
