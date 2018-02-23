import dash
import dash_core_components as dcc
import dash_html_components as html
from textwrap import dedent as d
from datetime import datetime, timedelta
from getopt import getopt
import sys
import MySQLdb as mysqldb
import threading
import pkg_resources
import pandas as pd
import urllib
import json
from dash.dependencies import Input, Output

# defaults is a list of dictionaries that stores each graphs previous range. Index 0 and 1 are the x axis range.
# 2 and 3 are the y axis range but reversed. Index 4 and 5 are used to say if the
# corresponding axis was updated in the current date range where 4 is the x
# axis and 5 is the y axis. 'h' is the hourly graph, 'd' is daily, 'm' is monthly,
# 'b' is bulk, 'c' is the current range that every graph is compated too.
# TODO: make defaults a table in the database rather than variable in this file
defaults = []
cnx = None
cursor = None
app = dash.Dash()
counter = -1
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
  print " -d        The name of the database. Default is sdiag."
  print " -h        Displays this message and quits."

# Daily
# the inclusion of the relayoutData for h, d, m, b is only to trigger this function
@app.callback(
  Output(component_id = 'daily', component_property = 'figure'),
  [Input(component_id = 'date-picker-monthly', component_property = 'end_date'),
   Input(component_id = 'date-picker-monthly', component_property = 'start_date'),
   Input(component_id = 'hourly', component_property = 'relayoutData'),
   Input(component_id = 'daily', component_property = 'relayoutData'),
   Input(component_id = 'monthly', component_property = 'relayoutData'),
   Input(component_id = 'bulk', component_property = 'relayoutData'),
   Input(component_id = 'hourly', component_property = 'figure')]
)
def update_daily(end_date, start_date, h, d, m, b, figure):
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
           'layout': {'title': 'Daily', 'xaxis': {'range': [True,True]}, 'yaxis': {'range': [True,True]}, 'hoverinfo': False},
    }
  else:
    return {'data':[
           {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
           {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
           {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
           ],
           'layout': {'title': 'Daily', 'xaxis': {'range': figure['layout']['xaxis']['range']}, 'yaxis': {'range': figure['layout']['yaxis']['range']}, 'hoverinfo': False},
    }
# Monthly
# the inclusion of the relayoutData for h, d, m, b is only to trigger this function
@app.callback(
  Output(component_id = 'monthly', component_property = 'figure'),
  [Input(component_id = 'date-picker-monthly', component_property = 'end_date'),
   Input(component_id = 'date-picker-monthly', component_property = 'start_date'),
   Input(component_id = 'hourly', component_property = 'relayoutData'),
   Input(component_id = 'daily', component_property = 'relayoutData'),
   Input(component_id = 'monthly', component_property = 'relayoutData'),
   Input(component_id = 'bulk', component_property = 'relayoutData'),
   Input(component_id = 'hourly', component_property = 'figure')]
)
def update_monthly(end_date, start_date, h, d, m, b, figure):
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
  Output(component_id = 'hourly', component_property = 'figure'),
  [Input(component_id = 'date-picker-monthly', component_property = 'end_date'),
   Input(component_id = 'date-picker-monthly', component_property = 'start_date'),
   Input(component_id = 'hourly', component_property = 'relayoutData'),
   Input(component_id = 'daily', component_property = 'relayoutData'),
   Input(component_id = 'monthly', component_property = 'relayoutData'),
   Input(component_id = 'bulk', component_property = 'relayoutData'),
   Input(component_id = 'my_index', component_property = 'children'),
   Input(component_id = 'ranges', component_property = 'children')]
)
def update_hourly(end_date, start_date, h, d, m, b, index, ranges):
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
  try:
    if b != None:
      if type(b.values()[0]) == unicode:
        if defaults[index]['b'][0] != b.values()[0] or defaults[index]['b'][1] != b.values()[1]:
          defaults[index]['b'][0] = b.values()[0]
          defaults[index]['b'][1] = b.values()[1]
          defaults[index]['b'][4] = True
          if len(b.values()) > 2 and (b.values()[2] != defaults[index]['b'][3] or b.values()[3] != defaults[index]['b'][2]):
            defaults[index]['b'][3] = b.values()[2]
            defaults[index]['b'][2] = b.values()[3]
            defaults[index]['b'][5] = True
          picked = 'b'
      elif type(b.values()[0]) == float:
        if defaults[index]['b'][3] != b.values()[0] or my_defaults[index]['b'][2] != b.values()[1]:
          defaults[index]['b'][3] = b.values()[0]
          defaults[index]['b'][2] = b.values()[1]
          defaults[index]['b'][5] = True
          picked = 'b'
      elif type(b.values()[0]) == bool:
        if (defaults[index]['b'][0] != b.values()[0] or defaults[index]['b'][2] != b.values()[1]) and not len(b.values()) == 1:
          defaults[index]['b'] = [True,True,True,True,False,False]
          picked = 'b'

    if h != None and picked == None:
      if type(h.values()[0]) == unicode:
        if defaults[index]['h'][0] != h.values()[0] or defaults[index]['h'][1] != h.values()[1]:
          defaults[index]['h'][0] = h.values()[0]
          defaults[index]['h'][1] = h.values()[1]
          defaults[index]['h'][4] = True
          if len(h.values()) > 2 and (h.values()[2] != defaults[index]['h'][3] or h.values()[3] != defaults[index]['h'][2]):
            defaults[index]['h'][3] = h.values()[2]
            defaults[index]['h'][2] = h.values()[3]
            defaults[index]['h'][5] = True
          picked = 'h'
      elif type(h.values()[0]) == float:
        if defaults[index]['h'][3] != h.values()[0] or defaults[index]['h'][2] != h.values()[1]:
          defaults[index]['h'][3] = h.values()[0]
          defaults[index]['h'][2] = h.values()[1]
          defaults[index]['h'][5] = True
          picked = 'h'
      elif type(h.values()[0]) == bool:
        if (defaults[index]['h'][0] != h.values()[0] or defaults[index]['h'][2] != h.values()[1]) and not len(h.values()) == 1:
          defaults[index]['h'] = [True,True,True,True,False,False]
          picked = 'h'

    if d != None and picked == None:
      if type(d.values()[0]) == unicode:
        if defaults[index]['d'][0] != d.values()[0] or defaults[index]['d'][1] != d.values()[1]:
          defaults[index]['d'][0] = d.values()[0]
          defaults[index]['d'][1] = d.values()[1]
          defaults[index]['d'][4] = True
          if len(d.values()) > 2 and (d.values()[2] != defaults[index]['d'][3] or d.values()[3] != defaults[index]['d'][2]):
            defaults[index]['d'][3] = d.values()[2]
            defaults[index]['d'][2] = d.values()[3]
            defaults[index]['d'][5] = True
          picked = 'd'
      elif type(d.values()[0]) == float:
        if defaults[index]['d'][3] != d.values()[0] or defaults[index]['d'][2] != d.values()[1]:
          defaults[index]['d'][3] = d.values()[0]
          defaults[index]['d'][2] = d.values()[1]
          defaults[index]['d'][5] = True
          picked = 'd'
      elif type(d.values()[0]) == bool:
        if (defaults[index]['d'][0] != d.values()[0] or  defaults[index]['d'][2] != d.values()[1]) and not len(d.values()) == 1:
          defaults[index]['d'] = [True,True,True,True,False,False]
          picked = 'd'

    if m != None and picked == None:
      if type(m.values()[0]) == unicode:
        if defaults[index]['m'][0] != m.values()[0] or defaults[index]['m'][1] != m.values()[1]:
          defaults[index]['m'][0] = m.values()[0]
          defaults[index]['m'][1] = m.values()[1]
          defaults[index]['m'][4] = True
          if m.values()[2] != defaults[index]['m'][3] or m.values()[3] != defaults[index]['m'][2]:
            defaults[index]['m'][3] = m.values()[2]
            defaults[index]['m'][2] = m.values()[3]
            defaults[index]['m'][5] = True
          picked = 'm'
      elif type(m.values()[0]) == float:
        if defaults[index]['m'][3] != m.values()[0] or defaults[index]['m'][2] != m.values()[1]:
          defaults[index]['m'][3] = m.values()[0]
          defaults[index]['m'][2] = m.values()[1]
          defaults[index]['m'][5] = True
          picked = 'm'
      elif type(m.values()[0]) == bool:
        if (defaults[index]['m'][0] != m.values()[0] or defaults[index]['m'][2] != m.values()[1]) and not len(m.values()) == 1:
          defaults[index]['m'] = [True,True,True,True,False,False]
          picked = 'm'

  except IndexError:
    picked = None

  # if the callback was triggered by zooming picked equals which graph was zoomed in on
  if picked != None:
    # if both the x and y axis have been zoomed in
    if defaults[index][picked][4] and defaults[index][picked][5]:
      defaults[index]['c'] = defaults[index][picked][:4]
      return {'data':[
                {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
                ],
                'layout': {'title': 'Hourly', 'xaxis': {'range': defaults[index]['c'][:2]}, 'yaxis': {'range': defaults[index]['c'][2:]}}
      }
    # if only zoomed into the x axis
    elif defaults[index][picked][4]:
      defaults[index]['c'][:2] = defaults[index][picked][:2]
      return {'data':[
                {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
                ],
                'layout': {'title': 'Hourly', 'xaxis': {'range': defaults[index]['c'][:2]}, 'yaxis': {'range': defaults[index]['c'][2:]}}
      }
    # if only zoomed into y axis
    elif defaults[index][picked][5]:
      defaults[index]['c'][2:] = defaults[index][picked][2:4]
      return {'data':[
                {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
                {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
                ],
                'layout': {'title': 'Hourly', 'xaxis': {'range': defaults[index]['c'][:2]}, 'yaxis': {'range': defaults[index]['c'][2:]}}
      }
    # this gets called if a graph has been double clicked on to resume default zoom scale
    else:
      defaults[index]['c'] = [True,True,True,True]
      return {
        'data':[
            {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
            {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
            {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
          ],
          'layout':{'title': 'Hourly', 'xaxis': {'range': [True, True]}, 'yaxis': {'range': [True, True]}}
      }
  # this gets called on startup or changing date range and for some reason
  # we have a chance of getting here from interaction with other components
  # such as the download text or closing the downloads bar in Chrome
  else:
    defaults[index]['h'][4:] = [False,False]
    defaults[index]['b'][4:] = [False,False]
    defaults[index]['d'][4:] = [False,False]
    defaults[index]['m'][4:] = [False,False]
    defaults[index]['c'] = [True,True,True,True]
    return {
      'data':[
          {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
          {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
          {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
        ],
        'layout':{'title': 'Hourly', 'xaxis': {'range': [True, True]}, 'yaxis': {'range': [True, True]}}
    }

@app.callback(
  Output(component_id = 'bulk', component_property = 'style'),
  [Input(component_id = 'activator', component_property = 'values')]
)
def show_bulk(values):
  if 'active' in values:
    return {'visibility': 'visible'}
  else:
    return {'visibility': 'hidden'}


# Bulk
# the inclusion of the relayoutData for h, d, m, b is only to trigger this function
@app.callback(
  Output(component_id = 'bulk', component_property = 'figure'),
  [Input(component_id = 'date-picker-monthly', component_property = 'end_date'),
   Input(component_id = 'date-picker-monthly', component_property = 'start_date'),
   Input(component_id = 'activator', component_property = 'values'),
   Input(component_id = 'hourly', component_property = 'relayoutData'),
   Input(component_id = 'daily', component_property = 'relayoutData'),
   Input(component_id = 'monthly', component_property = 'relayoutData'),
   Input(component_id = 'bulk', component_property = 'relayoutData'),
   Input(component_id = 'hourly', component_property = 'figure')]
)
def update_bulk(end_date, start_date, values, h, d, m, b, figure):
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

@app.callback(
  Output(component_id = 'download', component_property = 'href'),
  [Input(component_id = 'graph-select', component_property = 'value'),
   Input(component_id = 'hourly', component_property = 'figure'),
   Input(component_id = 'my_index', component_property = 'children')]
)
def download(value, hourly, index):
  has_time = False
  if hourly['layout']['xaxis'].has_key('autorange'):
    start_date = datetime.strptime(str(hourly['layout']['xaxis']['range'][0]), '%Y-%m-%d %H:%M:%S') - timedelta(days=1)
    try:
      cursor.execute("select * from " + value + " where date between '" + str(start_date) + "' and '" + str(hourly['layout']['xaxis']['range'][1]) + "' order by date ASC, time ASC")
      has_time = True
    except:
      cursor.execute("select * from " + value + " where date between '" + str(start_date) + "' and '" + str(hourly['layout']['xaxis']['range'][1]) + "' order by date ASC")
    raw_data_h = cursor.fetchall()
  else:
    start_date = datetime.strptime(str(defaults[index]['c'][0]), '%Y-%m-%d %H:%M:%S.%f') - timedelta(days=1)
    try:
      cursor.execute("select * from " + value + " where date between '" + str(start_date) + "' and '" + str(defaults[index]['c'][1]) + "' order by date ASC, time ASC")
      has_time = True
    except:
      cursor.execute("select * from " + value + " where date between '" + str(start_date) + "' and '" + str(defaults[index]['c'][1]) + "' order by date ASC")
    raw_data_h = cursor.fetchall()

  data_h = {
    'date': [],
    'ml': [],
    'bl': [],
    'bm': []
  }
  if has_time:
    for point in raw_data_h:
      data_h['date'].append(str(point[0]) + " " + str(point[1]))
      data_h['ml'].append(point[2])
      data_h['bl'].append(point[3])
      data_h['bm'].append(point[4])
  else:
    for point in raw_data_h:
      data_h['date'].append(str(point[0]))
      data_h['ml'].append(point[1])
      data_h['bl'].append(point[2])
      data_h['bm'].append(point[3])

  df = pd.DataFrame(data_h)
  csv_string = df.to_csv(index = False, encoding = 'utf-8')
  csv_string = "data:text/csv;charset=utf-8," + urllib.quote(csv_string)
  return csv_string

# this assigns each new client a counter number and saves that number to defaults
# holder is just needed to call this callback when anyone connects
# this number is then used to access each users own defaults dictionary
@app.callback(
  Output(component_id = 'my_index', component_property = 'children'),
  [Input(component_id = 'on_connect', component_property = 'children')]
)
def assign(o):
  global counter
  global defaults
  counter += 1
  defaults.insert(counter, {'h': [True, True, True, True, False, False], 'd': [True, True, True, True, False, False], 'm': [True, True, True, True, False, False], 'b': [True, True, True, True, False, False], 'c': [True, True, True, True]})
  return counter

def main():
  opts, _ = getopt(sys.argv[1:], "w:q:i:u:p:d:h")
  global cnx
  global cursor
  global app

  j_file = None
  try:
    resource_package = 'DashMetrics'
    resource_path = '/'.join(('statics', 'config.json'))
    conf = pkg_resources.resource_stream(resource_package, resource_path)
    j_file = json.load(conf)
  except:
    print 'ERROR: config.json is missing. Make sure config.json is in the'
    print 'statics directory when packaging.'
    return

  i = j_file['db_ip']
  u = j_file['db_username']
  p = j_file['db_password']
  d = j_file['db_name']
  q = int(j_file['dash_port'])
  w = j_file['dash_ip']
  
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

    html.Label('Select Graph to download'),

    dcc.Dropdown(
      id = 'graph-select',
      options = [{'label': 'Monthly', 'value': 'monthly'},
                 {'label': 'Daily', 'value': 'daily'},
                 {'label': 'Hourly', 'value': 'hourly'},
                 {'label': 'All Points', 'value': 'entries'}],
      value = 'monthly'
    ),

    html.A(children = 'Click to download', id = 'download', download = 'data.csv', href = '', target = '_blank'),

    dcc.Graph(
      id = 'monthly',
    ),

    dcc.Graph(
      id = 'daily',
    ),

    dcc.Graph(
      id = 'hourly',
    ),

    dcc.Graph(
      id = 'bulk',
      style = {'visibility': 'hidden'}
    ),
    # this holds each client's index
    html.Div(id = 'my_index', style = {'display': 'none'}),

    html.Div(id = 'ranges', style = {'display': 'none'}),
    
    html.Div(id = 'on_connect', style = {'display': 'none'})
  ])
  app.run_server(debug=True, host=w, port=q)
main()
