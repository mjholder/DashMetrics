import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
from getopt import getopt
import sys
import MySQLdb as mysqldb
import threading
import pkg_resources
import pandas as pd
import urllib
import json
import plotly

cnx = None
cursor = None
app = dash.Dash()
counter = 0
app.config['suppress_callback_exceptions'] = True

def parse_data(data):
  output = {'x':[], 'y':[]}
  for d in data:
    output['y'].append(d[13])
    output['x'].append(d[1])
  return output

@app.callback(
  Output(component_id = 'graph', component_property = 'figure'),
  [Input(component_id = 'datatable', component_property = 'rows'),
   Input(component_id = 'datatable', component_property = 'selected_row_indices')]
)
def update_figure(rows, selected_row_indices):
  dff = pd.DataFrame(rows)
  print "j: " + str(len(dff['JOBID'])) + ", c: " + str(len(dff['CPUS']))
  fig = plotly.tools.make_subplots(
    rows = 3, cols = 1,
    subplot_titles = ('CPUs', 'Minimum CPUs', 'Nodes'),
    shared_xaxes = True
  )
  marker = {'color': ['#0074D9'] * len(dff)}
  for i in (selected_row_indices or []):
    marker['color'][i] = '#FF851B'
  fig.append_trace({
    'x': dff['JOBID'],
    'y': dff['CPUS'],
    'type': 'bar',
    'marker': marker
  }, 1, 1)
  fig.append_trace({
    'x': dff['JOBID'],
    'y': dff['MIN_CPUS'],
    'type': 'bar',
    'marker': marker
  }, 2, 1)
  fig.append_trace({
    'x': dff['JOBID'],
    'y': dff['NODES'],
    'type': 'bar',
    'marker': marker
  }, 3, 1)

  return fig

def main():
  global cnx
  global cursor
  global app

  cnx = mysqldb.connect('0.0.0.0', 'root', '', 'sdiag')
  cnx.autocommit(True)
  cursor = cnx.cursor()
  cursor.execute("select `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='sdiag' AND `TABLE_NAME`='queue'")
  field_names = [i[0] for i in cursor.fetchall()]
  data = {}
  for field in field_names:
    cursor.execute("select " + field + " from queue")
    data[field] = [i[0] for i in cursor.fetchall()]
  data_df = pd.DataFrame(data)
  app.layout = html.Div(children=[
    dt.DataTable(
      rows = data_df.to_dict('records'),
      row_selectable = True,
      filterable = True,
      sortable = True,
      selected_row_indices = [],
      id = 'datatable',
    ),

    dcc.Graph(
      id = 'graph',
    ),
  ])
  app.run_server(debug=True, host='0.0.0.0', port=8050)

main()
