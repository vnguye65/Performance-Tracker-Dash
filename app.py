#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 13:01:34 2020

@author: ving2000
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 12:53:30 2020

@author: ving2000
"""

import pandas as pd
import numpy as np
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
from datetime import date

import dash  # (version 1.12.0) pip install dash
from plotly.subplots import make_subplots
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,  external_stylesheets=external_stylesheets)
server = app.server

app.config.suppress_callback_exceptions = True

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)
df = pd.read_csv("average_Updated_360.csv")
products = pd.read_csv('Intern_products.csv')

df['slider'] = df['Month'].replace(['2020-05-17', '2020-05-31', '2020-06-14'], [1, 2, 3])

df['Month'] = pd.to_datetime(df['Month'])

df_prod = df.merge(products, how = 'outer', on = ['First name'])


## Change the dates to numeric

## Define functions
def Format_Dash (df, column):
    options = []
    for i in df[column].unique():
        options.append(dict(label=str(i), value = i))
    return options


def highlight_table(df):
    
     pos_dict = [
        {
            'if': {
                'filter_query': '{{{}}} > 0'.format(pos_col),
                'column_id': pos_col 
            },
            'backgroundColor': '#6AB187',
            'color': 'white'
        } for pos_col in df[df['changes'] > 0]['criteria']]
     
     
     neg_dict = [
         {
            'if': {
                'filter_query': '{{{}}} < 0'.format(neg_col),
                'column_id': neg_col
            },
            'backgroundColor': '#D32D41',
            'color': 'white'
        } for neg_col in df[df['changes'] < 0]['criteria']]
     
     return pos_dict + neg_dict

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("360-REVIEWS DASHBOARD", style={'text-align': 'center', 
                                            'font-family': 'Times New Roman, serif',
                                            'fontWeight': 'bold'},),
    html.H3('----------------------', style = {'text-align': 'center'}),
    
    html.Div([
    html.Label('Select View: '),
    html.Button('Team Performance', id = 'team_button', n_clicks = 1,
                style = {'backgroundColor': 'black', 'color': 'white'}),
    html.Button('Individual Perfomance', id = 'ind_button',
                style = {'backgroundColor': 'black', 'color': 'white'})
    ], style = {'text-align': 'center'}),
    
    html.Br(), 
    
    html.Div([
        
    html.Div([
    html.Label('Select Product'),
    dcc.Dropdown(id="slct_prod",
                  options=Format_Dash(df_prod, 'Product'),
                  multi=False,
                  value='gigkoala.com',
                  style={'width': "70%"}
                )
    ], style = {'width': '50%', 'display': 'inline-block'}),
    
    html.Div([    
    html.Label('OR Select Intern(s) - Preselected from Product Selection'),
    dcc.Dropdown(id="slct_intern",
                 options=Format_Dash(df, 'First name'),
                 multi=True,
                 style={'width': "70%"}
                 )
      ], style = {'width': '50%', 'display': 'inline-block',
                  'align': 'right'})
                  ], className = 'row', style = {'margin': 20}),
    
    
    html.Div(id = 'team_content'),
    
    
    html.H3('-------------------------------------------------------------------------------------------------------', style = {'text-align': 'center'}),
    
    html.H3('Select Intern to View Details', style = {'text-align': 'center', 'fontWeight': 'bold'}),
    html.Label('Only displays interns selected from previous drop-down menu', style = {'margin': 20}),
    dcc.RadioItems(id = 'radio_single',
                    style={'width': "50%", 'padding-bottom': '1em', 'margin': 20},
                    labelStyle={'display': 'inline-block'}),
    
    html.Br(),
    
    html.Div([
        
        html.Div([
           dcc.Markdown("360-Reviews Assignment Submissions", style={'text-align': 'center'}),
           dcc.Graph(id = 'submission', figure = {}),
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            dcc.Markdown("Changes From Last Period", style={'text-align': 'center'}),
             dash_table.DataTable(id = 'change_table', data = [],
                                style_header={'backgroundColor': 'wheat',
                                                'border': '4px black solid',
                                                'font-family': 'Old Standard TT, serif',
                                                'font_size': '20px',
                                                'fontWeight': 'bold'},
                                style_cell={'whiteSpace': 'normal',
                                            'height': 'auto',
                                            'lineHeight': '40px',
                                            'textAlign': 'center',
                                              'font_size': '15px',
                                              'fontWeight': 'bold'
                                            },
                                  style_data={'border': '1px black solid'})
        ], style={'width': '70%', 'align': 'right', 'display': 'inline-block'})
    ], 
        className="row"),
    
    
    html.H5('Drag handle to select date', style = {'fontWeight': 'bold'}),

    dcc.Slider(id = 'slct_month', min=df['slider'].min(), #the first date
               max=df['slider'].max() + 1, #the last date
               value=df['slider'].min(), #default: the first
               marks = {numd: {'label' : date.strftime('%m/%d'), 'style':{'color':'black',
                                                                          'height': '100px', 
                                                                          'width': '100%',
                                                                          'display': 'inline-block'}}
                        for numd,date in zip(df['slider'].unique().tolist(), df['Month'].dt.date.unique())},
               updatemode='drag'
               ),

    
    html.Br(),
    
    html.H3(id='slct_name', children=[], style={'text-align': 'center', 'backgroundColor': 'rgb(102, 102, 102',
                                                'color': 'white'}),
    
    html.Br(),
     
     html.Div([
     
        # html.Div([
        #     html.H4('Mouse over each criteria to view comments',  style={'text-align': 'center'}),
        #     dcc.Graph(id='bubble', figure={}, hoverData={'points': [{'customdata': 'initiative'}]})
        # ], style={'width': '50%', 'align' : 'left', 'display': 'inline-block'}),
        
        html.Div([
            html.H6("Treemap: Darker Highlighted Boxes are the intern's higher rated criteria", 
                          style={'text-align': 'center'}),
            dcc.Markdown("Mouse over each criteria to view comments", 
                          style={'text-align': 'center'}),
            dcc.Graph(id = 'treemap', figure={}, 
                      hoverData={'points': [{'label': 'initiative'}]}
                      )
        ], style={'width': '50%', 'display': 'inline-block'}),

         html.Div([
            html.H6('Comments',  style={'text-align': 'center'}),
           dash_table.DataTable(id = 'table', data = [],
                                style_header={'backgroundColor': 'wheat',
                                               'border': '4px black solid',
                                               'font-family': 'Old Standard TT, serif',
                                               'font_size': '35px',
                                               'fontWeight': 'bold'},
                                style_cell={'whiteSpace': 'normal',
                                            'height': 'auto',
                                            'lineHeight': '60px',
                                            'textAlign': 'center',
                                             'font_size': '17px'
                                            },
                                 style_data={'border': '1px black solid' }, 
                                 merge_duplicate_headers = True,
                                 
                                 style_header_conditional=[
        { 'if': { 'column_id': 'pos_comm', 'header_index': 1}, 'backgroundColor': '#6AB187'},
         { 'if': { 'column_id': 'pos_comm', 'header_index': 1}, 'font_size': '27'},
         
        { 'if': { 'column_id': 'neg_comm', 'header_index': 1 }, 'backgroundColor': '#D32D41'},
        { 'if': { 'column_id': 'neg_comm', 'header_index': 1 }, 'font_size': '27' }
        ]
        ),
        ], style={'width': '50%', 'align': 'center', 'display': 'inline-block'})
    ], 
        className="row"),
 
    
    
])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='slct_intern', component_property='value'),

    [Input(component_id='slct_prod', component_property='value')]
)
def select_interns (prod):
    
    dff = products[products['Product'] == prod]
    return dff['First name'].to_list()


@app.callback(
   [Output(component_id='team_content', component_property='children'),
    Output(component_id='slct_intern', component_property='disabled')],
    [Input(component_id='team_button', component_property='n_clicks'),
     Input(component_id='ind_button', component_property='n_clicks')])

def show_content (t_button, i_button):
    
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    if 'ind_button' in changed_id:
        content = dcc.Graph(id='facet_graph', figure={})
        show = False
        
    else:
       content = dcc.Graph(id = 'donuts', figure = {})
       show = True

    return content, show

    

@app.callback(

     Output(component_id='facet_graph', component_property='figure'),

    
    [Input(component_id='slct_intern', component_property='value'),
     Input(component_id='slct_month', component_property='value')]
)
def update_graphs(option_intern, option_month):
    print(option_intern)
    print(type(option_intern))
    
    print(option_month)
    print(type(option_month))


    dff = df.copy()
    dff = dff[dff["First name"].isin(option_intern)].sort_values(['criteria', 'Month'])
    
    # Plotly Express
    fig = px.line(dff, x = 'Month', y ='rating', color = 'First name',
                  template = 'simple_white', facet_col = 'criteria',
                  hover_name = 'First name', hover_data = ['criteria', 'rating'],
                  title = 'Perfomance by criteria')
    
    fig.update_traces(mode = 'markers+lines')
    fig.update_xaxes(tickangle=45, title = 'Date')
    fig.update_yaxes(range=[0, 4])
    fig.update_layout(title_x=0.5)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    return fig

@app.callback(
    Output(component_id='donuts', component_property='figure'),
    [Input(component_id='slct_prod', component_property='value')]
)

def Update_donuts (prod):
    
    donut = df_prod.groupby(['First name', 'Product'], as_index = False).mean()
    donut = donut[donut['Product'] == prod]
    
    bar = df_prod.groupby(['Month', 'Product'], as_index = False).mean()
    bar = bar[bar['Product'] == prod]
    
    
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'xy'}]],
                        subplot_titles = ("Member contributions", "Performance by Product"))
    
    fig.add_trace(go.Pie(labels=donut['First name'], values=np.round(donut['rating'], decimals = 1), 
                         hole = .55,
                         marker_colors = px.colors.sequential.RdBu), row = 1, col = 1)
    
    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                  marker=dict(line=dict(color='#000000', width=2)))
    
    
    fig.add_trace(go.Scatter(x = bar['Month'], y = bar['rating'], marker_color='crimson', mode = 'lines+markers'),
              1, 2)
    
    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_yaxes(title_text="Team Average Rating", row=1, col=2)

    
    fig.update_layout(template = 'simple_white',
                       autosize=True,
    margin=dict(
        l=10,
        r=10,
        b=7,
        t = 80,
        pad = 4
    ), title = '{} Member Contributions & {} Performance by Date (Group Average)'.format(prod, prod),
    title_x=0.5,
    annotations=[dict(text=prod, x=0.23, y=0.5, font_size=20, showarrow=False),
                    dict(text = str(np.round(donut['rating'].sum(), decimals = 1)),
                          x=0.23, y=0.4, font_size=17, showarrow=False)])
    
    return fig


@app.callback(
    [Output(component_id='radio_single', component_property='options'),
    Output(component_id='radio_single', component_property='value')],
    [Input(component_id='slct_intern', component_property='value')]
)
def Select_intern (selected_intern):
     return [{'label': str(i), 'value': i} for i in selected_intern], selected_intern[0]




@app.callback(
    [Output(component_id='slct_name', component_property='children'),
     Output(component_id='treemap', component_property='figure')
    ],
    
    [Input(component_id='radio_single', component_property='value'),
     Input(component_id='slct_month', component_property='value')]
)

def update_single_plots(option_intern, option_month):
    
    dff = df.copy()
    dff = dff[dff["First name"] == option_intern]
    dff = dff[dff['slider'] == option_month]
    
    info_name = 'Intern: {} - Date: {}'.format(option_intern, dff['Month'].to_list()[0].strftime('%m/%d'))
    

    fig2 = go.Figure(go.Treemap(labels = dff['criteria'].to_list(),
                                parents = ['', '', '', '', ''], values = dff['rating'].to_list(),
                                marker_colorscale = 'YlOrRd', 
                                textposition = 'middle center',
                        
                                texttemplate = "%{label} <br> %{value:s} ",
                                textinfo = 'label+value+text', #label=dff['criteria']
                                  ))
    
    fig2.update_layout(hovermode = 'closest')
    
    # fig3 = go.Figure(data=go.Scatter(x = dff['criteria'], y = dff['rating'], 
    #                             mode='markers', marker_color=['turquoise', 'violet', 'wheat', 
    #                                                           'blue', 'red'],
    #                               customdata=dff['criteria']
                            
    #                   ))

                              

    return info_name, fig2


@app.callback(
    [Output(component_id='change_table', component_property='data'),
      Output(component_id='change_table', component_property='columns'),
      Output(component_id='change_table', component_property='style_data_conditional'),
      Output(component_id='submission', component_property='figure')],
    
    [Input(component_id='radio_single', component_property='value')]
)

def update_change_table (option_intern):
    
    dff = df.copy()
    dff = dff[dff["First name"] == option_intern]
    
    period = dff['Month'].unique()
    
    f_dff = dff[dff['Month'] == period[-2]].sort_values(['criteria'])
    final_dff = dff[dff['Month'] == period[-1]].sort_values(['criteria'])
    
    final_dff['changes'] = final_dff['rating'].values - f_dff['rating'].values

    
    changes = {}
    for crit, rate in zip(final_dff['criteria'], final_dff['changes']):
        changes[crit] = rate
        
        
    dff['submission_graph'] = dff['Submission'].apply(lambda x: 1 if x == 'On-time' else -int(x[0]))
    dff['status'] = dff['Submission'].apply(lambda x: 'On-time' if x == 'On-time' else 'Late')
    
    dff1 = dff.drop_duplicates('Month')
    clrs = ["#D32D41" if x == 'Late' else  "#6AB187" for x in dff1['status']]
    clrs = list(dict.fromkeys(clrs))
    
    fig = px.bar(dff1, 
                  x = 'Month', y = 'submission_graph', hover_name = 'First name',
                  hover_data = ['Submission'],
                  color = 'status', template = 'simple_white', color_discrete_sequence=clrs)
    
    
    fig.update_layout(
        autosize=False,
        width=400,
        height=200,
    yaxis=dict(
        title_text="Days late"
    ), xaxis = dict(title_text = 'Date'),
    margin=dict(
        l=10,
        r=10,
        b=10,
        t=10,
        pad=4
    ), template = 'simple_white', showlegend = True
)

    
    return [changes], [{'id': c, 'name': c} for c in final_dff.criteria], highlight_table(final_dff), fig


    
    
@app.callback(
    [Output(component_id='table', component_property='data'),
      Output(component_id='table', component_property='columns')
      ],
    
    [Input(component_id='treemap', component_property='hoverData'),
      Input(component_id='radio_single', component_property='value'),
      Input(component_id='slct_month', component_property='value')]
)

def update_table (hov, option_intern, option_month):

    criteria = hov['points'][0]['label']
    
    
    dff = df.copy()
    dff = dff[dff["First name"] == option_intern]
    dff = dff[dff['slider'] == option_month]
    dff = dff[dff['criteria'] == criteria]
    
    comment = dff[['pos_comm', 'neg_comm']].to_dict('records')
    
    return comment, [{"name": [criteria, 'Most Positive'], "id": 'pos_comm'}, 
{"name": [criteria, 'Most Negative'], "id": 'neg_comm'}]



# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)#,dev_tools_ui=False,dev_tools_props_check=False)
