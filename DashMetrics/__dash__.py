import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from textwrap import dedent as d
from datetime import datetime as dt
from getopt import getopt
import sys
import MySQLdb as mysqldb
import threading

# defaults stores each graphs previous range. Index 0 and 1 are the x axis range.
# 2 and 3 are the y axis range but reversed. Index 4 and 5 are used to say if the
# corresponding axis was updated in the current date range where 4 is the x
# axis and 5 is the y axis. 'h' is the hourly graph, 'd' is daily, 'm' is monthly,
# 'b' is bulk, 'c' is the current range that every graph is compated too
defaults = {'h': [True, True, True, True, False, False], 'd': [True, True, True, True, False, False], 'm': [True, True, True, True, False, False], 'b': [True, True, True, True, False, False], 'c': [True, True, True, True]}
cnx = None
cursor = None
app = dash.Dash()

app.config['suppress_callback_exceptions']=True

def usage():
  print " -w        Specify the ip for Dash to run on."
  print "           Default ip is '0.0.0.0'."
  print " -q        Specify the port for Dash to run on."
  print "           Defualt port is '8050'."
  print " -i        Specify the ip of the database you are"
  print "           connecting to. Default is 'localhost'."
  print " -u        The username for accessing the database."
  print "           Default username is 'root'."
  print " -p        The password for accessing the database."
  print " -d        The name of the database (Required)"
  print " -h        Displays this message and quits."

# Daily
# the inclusion of the relayoutData for h, d, m, b is only to trigger this function
@app.callback(
  dash.dependencies.Output(component_id = 'daily', component_property = 'figure'),
  [dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'end_date'),
   dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'start_date'),
   dash.dependencies.Input(component_id = 'hourly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'daily', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'monthly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'bulk', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'hourly', component_property = 'figure')]
)
def update_daily(end_date, start_date, h, d, m, b, figure):
  global defaults
  cursor.execute("select * from daily where date between '" + str(start_date) + "' and '" + str(end_date) + "'")
  data = cursor.fetchall()
  data_t = {
    'date': [],
    'ml': [],
    'bl': [],
    'bm': []
  }

  for point in data:
    data_t['date'].append(str(point[0]))
    data_t['ml'].append(point[1])
    data_t['bl'].append(point[2])
    data_t['bm'].append(point[3])

  if figure['layout']['xaxis'].has_key('autorange') and figure['layout']['yaxis'].has_key('autorange'):
    return {'data':[
           {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
           {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
           {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
           ],
           'layout': {'title': 'Daily', 'xaxis': {'range': [True,True]}, 'yaxis': {'range': [True,True]}}
    }
  else:
    return {'data':[
           {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
           {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
           {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
           ],
           'layout': {'title': 'Daily', 'xaxis': {'range': figure['layout']['xaxis']['range']}, 'yaxis': {'range': figure['layout']['yaxis']['range']}}
    }
# Monthly
# the inclusion of the relayoutData for h, d, m, b is only to trigger this function
@app.callback(
  dash.dependencies.Output(component_id = 'monthly', component_property = 'figure'),
  [dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'end_date'),
   dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'start_date'),
   dash.dependencies.Input(component_id = 'hourly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'daily', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'monthly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'bulk', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'hourly', component_property = 'figure')]
)
def update_monthly(end_date, start_date, h, d, m, b, figure):
  global defaults
  if start_date[-2:] != '01':
    start_date = start_date[:-2] + '01'
  cursor.execute("select * from monthly where date between '" + str(start_date) + "' and '" + str(end_date) + "'")
  raw_data_m = cursor.fetchall()

  data_m = {
    'date': [],
    'ml': [],
    'bl': [],
    'bm': []
  }

  for point in raw_data_m:
    data_m['date'].append(str(point[0]))
    data_m['ml'].append(point[1])
    data_m['bl'].append(point[2])
    data_m['bm'].append(point[3])

  if figure['layout']['xaxis'].has_key('autorange') and figure['layout']['yaxis'].has_key('autorange'):
    return {'data':[
           {'x': data_m['date'], 'y': data_m['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
           {'x': data_m['date'], 'y': data_m['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
           {'x': data_m['date'], 'y': data_m['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
           ],
           'layout': {'title': 'Monthly', 'xaxis': {'range': [True,True]}, 'yaxis': {'range': [True,True]}}
    }
  else:
    return {'data':[
           {'x': data_m['date'], 'y': data_m['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
           {'x': data_m['date'], 'y': data_m['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
           {'x': data_m['date'], 'y': data_m['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
           ],
           'layout': {'title': 'Monthly', 'xaxis': {'range': figure['layout']['xaxis']['range']}, 'yaxis': {'range': figure['layout']['yaxis']['range']}}
    }

# Hourly
@app.callback(
  dash.dependencies.Output(component_id = 'hourly', component_property = 'figure'),
  [dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'end_date'),
   dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'start_date'),
   dash.dependencies.Input(component_id = 'hourly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'daily', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'monthly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'bulk', component_property = 'relayoutData')]
)
def update_hourly(end_date, start_date, h, d, m, b):
  global defaults
  cursor.execute("select * from hourly where date between '" + str(start_date) + "' and '" + str(end_date) + "' order by date ASC, time ASC")
  raw_data_h = cursor.fetchall()
  data_h = {
    'date': [],
    'ml': [],
    'bl': [],
    'bm': []
  }

  for point in raw_data_h:
    data_h['date'].append(str(point[0]) + " " + str(point[1]))
    data_h['ml'].append(point[2])
    data_h['bl'].append(point[3])
    data_h['bm'].append(point[4])
  
  # picked is which graph was zoomed in on
  # if type is unicode than the graph was an x axis zoom, or an x and y axis zoom
  # if type is float than it is only a y axis zoom
  # if type is bool than the graph goes to default zoom
  picked = None
  if b != None:
    if type(b.values()[0]) == unicode:
      if defaults['b'][0] != b.values()[0] or defaults['b'][1] != b.values()[1]:
        defaults['b'][0] = b.values()[0]
        defaults['b'][1] = b.values()[1]
        defaults['b'][4] = True
        if len(b.values()) > 2 and (b.values()[2] != defaults['b'][3] or b.values()[3] != defaults['b'][2]):
          defaults['b'][3] = b.values()[2]
          defaults['b'][2] = b.values()[3]
          defaults['b'][5] = True
        picked = 'b'
    elif type(b.values()[0]) == float:
      if defaults['b'][3] != b.values()[0] or defaults['b'][2] != b.values()[1]:
        defaults['b'][3] = b.values()[0]
        defaults['b'][2] = b.values()[1]
        defaults['b'][5] = True
        picked = 'b'
    elif type(b.values()[0]) == bool:
      if defaults['b'][0] != b.values()[0] or defaults['b'][2] != b.values()[1]:
        defaults['b'] = [True,True,True,True,False,False]
        picked = 'b'

  if h != None:
    if type(h.values()[0]) == unicode:
      if defaults['h'][0] != h.values()[0] or defaults['h'][1] != h.values()[1]:
        defaults['h'][0] = h.values()[0]
        defaults['h'][1] = h.values()[1]
        defaults['h'][4] = True
        if len(h.values()) > 2 and (h.values()[2] != defaults['h'][3] or h.values()[3] != defaults['h'][2]):
          defaults['h'][3] = h.values()[2]
          defaults['h'][2] = h.values()[3]
          defaults['h'][5] = True
        picked = 'h'
    elif type(h.values()[0]) == float:
      if defaults['h'][3] != h.values()[0] or defaults['h'][2] != h.values()[1]:
        defaults['h'][3] = h.values()[0]
        defaults['h'][2] = h.values()[1]
        defaults['h'][5] = True
        picked = 'h'
    elif type(h.values()[0]) == bool:
      if defaults['h'][0] != h.values()[0] or defaults['h'][2] != h.values()[1]:
        defaults['h'] = [True,True,True,True,False,False]
        picked = 'h'

  if d != None:
    if type(d.values()[0]) == unicode:
      if defaults['d'][0] != d.values()[0] or defaults['d'][1] != d.values()[1]:
        defaults['d'][0] = d.values()[0]
        defaults['d'][1] = d.values()[1]
        defaults['d'][4] = True
        if len(d.values()) > 2 and (d.values()[2] != defaults['d'][3] or d.values()[3] != defaults['d'][2]):
          defaults['d'][3] = d.values()[2]
          defaults['d'][2] = d.values()[3]
          defaults['d'][5] = True
        picked = 'd'
    elif type(d.values()[0]) == float:
      if defaults['d'][3] != d.values()[0] or defaults['d'][2] != d.values()[1]:
        defaults['d'][3] = d.values()[0]
        defaults['d'][2] = d.values()[1]
        defaults['d'][5] = True
        picked = 'd'
    elif type(d.values()[0]) == bool:
      if defaults['d'][0] != d.values()[0] or defaults['d'][2] != d.values()[1]:
        defaults['d'] = [True,True,True,True,False,False]
        picked = 'd'

  if m != None:
    if type(m.values()[0]) == unicode:
      if defaults['m'][0] != m.values()[0] or defaults['m'][1] != m.values()[1]:
        defaults['m'][0] = m.values()[0]
        defaults['m'][1] = m.values()[1]
        defaults['m'][4] = True
        if len(m.values()) > 2 and (m.values()[2] != defaults['m'][3] or m.values()[3] != defaults['m'][2]):
          defaults['m'][3] = m.values()[2]
          defaults['m'][2] = m.values()[3]
          defaults['m'][5] = True
        picked = 'm'
    elif type(m.values()[0]) == float:
      if defaults['m'][3] != m.values()[0] or defaults['m'][2] != m.values()[1]:
        defaults['m'][3] = m.values()[0]
        defaults['m'][2] = m.values()[1]
        defaults['m'][5] = True
        picked = 'm'
    elif type(m.values()[0]) == bool:
      if defaults['m'][0] != m.values()[0] or defaults['m'][2] != m.values()[1]:
        defaults['m'] = [True,True,True,True,False,False]
        picked = 'm'
  
  # if the callback was triggered by zooming picked equals which graph was zoomed in on
  if picked != None:
    # if both the x and y axis have been zoomed in
    if defaults[picked][4] and defaults[picked][5]:
      defaults['c'] = defaults[picked][:4]
      return {'data':[
                {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
                ],
                'layout': {'title': 'Hourly', 'xaxis': {'range': defaults['c'][:2]}, 'yaxis': {'range': defaults['c'][2:]}}
      }
    # if only zoomed into the x axis
    elif defaults[picked][4]:
      defaults['c'][:2] = defaults[picked][:2]
      return {'data':[
                {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
                ],
                'layout': {'title': 'Hourly', 'xaxis': {'range': defaults['c'][:2]}, 'yaxis': {'range': defaults['c'][2:]}}
      }
    # if only zoomed into y axis
    elif defaults[picked][5]:
      defaults['c'][2:] = defaults[picked][2:4]
      return {'data':[
                {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
                ],
                'layout': {'title': 'Hourly', 'xaxis': {'range': defaults['c'][:2]}, 'yaxis': {'range': defaults['c'][2:]}}
      }
    # this gets called if a graph has been double clicked on to resume default zoom scale
    else:
      defaults['c'] = [True,True,True,True]
      return {
        'data':[
            {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
            {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
            {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
          ],
          'layout':{'title': 'Hourly', 'xaxis': {'range': [True, True]}, 'yaxis': {'range': [True, True]}}
      }
  # this gets called on startup or changing date range
  else:
    for e in defaults:
      defaults[e][4:] = [False,False]
    defaults['c'] = [True,True,True,True]
    return {
      'data':[
          {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
          {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
          {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
        ],
        'layout':{'title': 'Hourly', 'xaxis': {'range': [True, True]}, 'yaxis': {'range': [True, True]}}
    }

@app.callback(
  dash.dependencies.Output(component_id = 'bulk', component_property = 'style'),
  [dash.dependencies.Input(component_id = 'activator', component_property = 'values')]
)
def show_bulk(values):
  if 'active' in values:
    return {'visibility': 'visible'}
  else:
    return {'visibility': 'hidden'}


# Bulk
# the inclusion of the relayoutData for h, d, m, b is only to trigger this function
@app.callback(
  dash.dependencies.Output(component_id = 'bulk', component_property = 'figure'),
  [dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'end_date'),
   dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'start_date'),
   dash.dependencies.Input(component_id = 'activator', component_property = 'values'),
   dash.dependencies.Input(component_id = 'hourly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'daily', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'monthly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'bulk', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'hourly', component_property = 'figure')]
)
def update_bulk(end_date, start_date, values, h, d, m, b, figure):
  global defaults
  if 'active' in values:
    cursor.execute("select * from entries where date between '" + str(start_date) + "' and '" + str(end_date) + "' order by date ASC, time ASC")
    data = cursor.fetchall()
    data_t = {
      'date': [],
      'ml': [],
      'bl': [],
      'bm': []
    }

    for point in data:
      data_t['date'].append(str(point[0]) + " " + str(point[1]))
      data_t['ml'].append(point[2])
      data_t['bl'].append(point[3])
      data_t['bm'].append(point[4])
    # this series of if else's check which, if any, axises are in there default range
    if figure['layout']['xaxis'].has_key('autorange') and figure['layout']['yaxis'].has_key('autorange'):
      return {'data':[
             {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
             {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
             {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
             ],
             'layout': {'title': 'All Points', 'xaxis': {'range': [True,True]}, 'yaxis': {'range': [True,True]}}
      }
    elif figure['layout']['yaxis'].has_key('autorange'):
      return {'data':[
             {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
             {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
             {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
             ],
             'layout': {'title': 'All Points', 'xaxis': {'range': figure['layout']['xaxis']['range']}, 'yaxis': {'range': [True,True]}}
      }
    elif figure['layout']['xaxis'].has_key('autorange'):
      return {'data':[
             {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
             {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
             {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
             ],
             'layout': {'title': 'All Points', 'xaxis': {'range': [True,True]}, 'yaxis': {'range': figure['layout']['yaxis']['range']}}
      }
    else:
      return {'data':[
             {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
             {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
             {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
             ],
             'layout': {'title': 'All Points', 'xaxis': {'range': figure['layout']['xaxis']['range']}, 'yaxis': {'range': figure['layout']['yaxis']['range']}}
      }

  else:
    return {
      'data':[],
      'layout':{'title': 'All Points'}
    }

def main():
  opts, _ = getopt(sys.argv[1:], "w:q:i:u:p:d:h")
  global cnx
  global cursor
  global app
  i = 'localhost'
  u = 'root'
  p = ''
  d = ''
  q = 8050
  w = '0.0.0.0'
  
  for opt in opts:
    if opt[0] == '-w':
      w = opt[1]
    if opt[0] == '-q':
      q = int(opt[1])
    if opt[0] == '-i':
      i = opt[1]
    if opt[0] == '-u':
      u = opt[1]
    if opt[0] == '-p':
      p = opt[1]
    if opt[0] == '-d':
      d = opt[1]
    if opt[0] == '-h':
      usage()
      sys.exit(0)

  if d == '':
    print "You must provide a database name."
    usage()
    sys.exit(0)

  cnx = mysqldb.connect(i, u, p, d)
  cursor = cnx.cursor()

# This is used for the day limits when seleting from the date range
  cursor.execute("select date from entries order by date ASC")
  time = cursor.fetchall()
  app.layout = html.Div(children=[
    html.H1(children='Cycle Metrics', style = {'text-align':'center'}),    

    html.Div('Select Date Range'),

    dcc.DatePickerRange(
      id = 'date-picker-monthly',
      min_date_allowed = time[0][0],
      max_date_allowed = time[-1][0],
      start_date = time[0][0],
      end_date = time[-1][0],
    ),

    dcc.Checklist(
      id = 'activator',
      options=[
        {'label': 'Show All Points', 'value': 'active'}
      ],
      values = [''],
      style = {'text-align':'right'}
    ),

    dcc.Graph(
      id = 'monthly',
    ),

    dcc.Graph(
      id = 'daily'
    ),

    dcc.Graph(
      id = 'hourly',
    ),

    dcc.Graph(
      id = 'bulk',
      style = {'visibility': 'hidden'}
    ),

  ])
  app.run_server(debug=True, host=w, port=q)
