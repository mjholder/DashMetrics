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

# defaults is a dictionary that stores each graphs previous range. Index 0 and 1 are the x axis range.
# 2 and 3 are the y axis range but reversed. Index 4 and 5 are used to say if the
# corresponding axis was updated in the current date range where 4 is the x
# axis and 5 is the y axis. 'h' is the hourly graph, 'd' is daily, 'm' is monthly,
# 'b' is bulk, 'c' is the current range that every graph is compated too.
cnx = None
cursor = None
app = dash.Dash()
counter = 0
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
  cursor.execute("select * from daily where date between %s and %s", [start_date, end_date])
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
  cursor.execute("select * from monthly where date between %s and %s", [start_date, end_date])
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

def defaults_unpacker(values):
  output = []
  for v in range(0, 4):
    if values[v] == 'True' or values[v] == '1':
      output.append(True)
    else:
      try:
        output.append(float(values[v]))
      except:
        output.append(values[v])
        
  try:
    output.append(bool(values[4]))
    output.append(bool(values[5]))
  except IndexError:
    # This only happens for prev_c which doesn't have x_changed and y_changed 
    pass
  return output

def defaults_packer(defaults, index):
  cursor.execute("replace into prev_m(id, x_start, x_end, y_start, y_end, x_changed, y_changed) values(%s, %s, %s, %s, %s, %s, %s)", [index, defaults['m'][0], defaults['m'][1], defaults['m'][2], defaults['m'][3], defaults['m'][4], defaults['m'][5]])
  cursor.execute("replace into prev_h(id, x_start, x_end, y_start, y_end, x_changed, y_changed) values(%s, %s, %s, %s, %s, %s, %s)", [index, defaults['h'][0], defaults['h'][1], defaults['h'][2], defaults['h'][3], defaults['h'][4], defaults['h'][5]])
  cursor.execute("replace into prev_d(id, x_start, x_end, y_start, y_end, x_changed, y_changed) values(%s, %s, %s, %s, %s, %s, %s)", [index, defaults['d'][0], defaults['d'][1], defaults['d'][2], defaults['d'][3], defaults['d'][4], defaults['d'][5]])
  cursor.execute("replace into prev_b(id, x_start, x_end, y_start, y_end, x_changed, y_changed) values(%s, %s, %s, %s, %s, %s, %s)", [index, defaults['b'][0], defaults['b'][1], defaults['b'][2], defaults['b'][3], defaults['b'][4], defaults['b'][5]])
  cursor.execute("replace into prev_c(id, x_start, x_end, y_start, y_end) values(%s, %s, %s, %s, %s)", [index, defaults['c'][0], defaults['c'][1], defaults['c'][2], defaults['c'][3]])
  cursor.execute("replace into last_picked(id, picked) values(%s, %s)", [index, defaults['lp']])

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
  defaults = {
    'h': [],
    'd': [],
    'b': [],
    'm': [],
    'c': [],
    'lp': ''
  }

  cursor.execute("select x_start, x_end, y_start, y_end, x_changed, y_changed from prev_h where id = %s", [index])
  defaults['h'] = defaults_unpacker(cursor.fetchall()[0])

  cursor.execute("select x_start, x_end, y_start, y_end, x_changed, y_changed from prev_b where id = %s", [index])
  defaults['b'] = defaults_unpacker(cursor.fetchall()[0])

  cursor.execute("select x_start, x_end, y_start, y_end, x_changed, y_changed from prev_d where id = %s", [index])
  defaults['d'] = defaults_unpacker(cursor.fetchall()[0])

  cursor.execute("select x_start, x_end, y_start, y_end, x_changed, y_changed from prev_m where id = %s", [index])
  defaults['m'] = defaults_unpacker(cursor.fetchall()[0])

  cursor.execute("select x_start, x_end, y_start, y_end from prev_c where id = %s", [index])
  defaults['c'] = defaults_unpacker(cursor.fetchall()[0])

  cursor.execute("select picked from last_picked where id = %s", [index])
  lp = cursor.fetchall()[0][0]
  if lp == 'None':
    defaults['lp'] = None
  else:
    defaults['lp'] = lp
  
  cursor.execute("select * from hourly where date between %s and %s order by date ASC, time ASC", [start_date, end_date])
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
        if int(defaults['b'][3]) != int(b.values()[0]) or int(my_defaults['b'][2]) != int(b.values()[1]):
          defaults['b'][3] = b.values()[0]
          defaults['b'][2] = b.values()[1]
          defaults['b'][5] = True
          picked = 'b'
      elif type(b.values()[0]) == bool:
        if (defaults['b'][0] != b.values()[0] or defaults['b'][2] != b.values()[1]) and not len(b.values()) == 1:
          defaults['b'] = [True,True,True,True,False,False]
          picked = 'b'

    if h != None and picked == None:
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
        if int(defaults['h'][3]) != int(h.values()[0]) or int(defaults['h'][2]) != int(h.values()[1]):
          defaults['h'][3] = h.values()[0]
          defaults['h'][2] = h.values()[1]
          defaults['h'][5] = True
          picked = 'h'
      elif type(h.values()[0]) == bool:
        if (defaults['h'][0] != h.values()[0] or defaults['h'][2] != h.values()[1]) and not len(h.values()) == 1:
          defaults['h'] = [True,True,True,True,False,False]
          picked = 'h'

    if d != None and picked == None:
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
        if int(defaults['d'][3]) != int(d.values()[0]) or int(defaults['d'][2]) != int(d.values()[1]):
          defaults['d'][3] = d.values()[0]
          defaults['d'][2] = d.values()[1]
          defaults['d'][5] = True
          picked = 'd'
      elif type(d.values()[0]) == bool:
        if (defaults['d'][0] != d.values()[0] or  defaults['d'][2] != d.values()[1]) and not len(d.values()) == 1:
          defaults['d'] = [True,True,True,True,False,False]
          picked = 'd'

    if m != None and picked == None:
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
        if int(defaults['m'][3]) != int(m.values()[0]) or int(defaults['m'][2]) != int(m.values()[1]):
          defaults['m'][3] = m.values()[0]
          defaults['m'][2] = m.values()[1]
          defaults['m'][5] = True
          picked = 'm'
      elif type(m.values()[0]) == bool:
        if (defaults['m'][0] != m.values()[0] or defaults['m'][2] != m.values()[1]) and not len(m.values()) == 1:
          defaults['m'] = [True,True,True,True,False,False]
          picked = 'm'

  except IndexError:
    picked = None
  try:
    if len(m.values()) == 1 and len(h.values()) == 1 and len(b.values()) == 1 and len(d.values()) == 1:
      picked = defaults['lp']
      defaults[picked][4:] = [True, True]
  except:
    pass

  # if the callback was triggered by zooming picked equals which graph was zoomed in on
  if picked != None:
    defaults['lp'] = picked;
    # if both the x and y axis have been zoomed in
    if defaults[picked][4] and defaults[picked][5]:
      defaults['c'] = defaults[picked][:4]
      defaults_packer(defaults, index)
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
      defaults_packer(defaults, index)
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
      defaults_packer(defaults, index)
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
      defaults_packer(defaults, index)
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
    defaults['h'][4:] = [False,False]
    defaults['b'][4:] = [False,False]
    defaults['d'][4:] = [False,False]
    defaults['m'][4:] = [False,False]
    defaults['c'] = [True,True,True,True]
    defaults_packer(defaults, index)
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
    cursor.execute("select * from entries where date between %s and %s order by date ASC, time ASC", [start_date, end_date])
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
  Output(component_id = 'download', component_property = 'download'),
  [Input(component_id = 'file-format', component_property = 'value')]
)
def download_format(fformat):
  return 'data.' + fformat

@app.callback(
  Output(component_id = 'download', component_property = 'href'),
  [Input(component_id = 'graph-select', component_property = 'value'),
   Input(component_id = 'hourly', component_property = 'figure'),
   Input(component_id = 'my_index', component_property = 'children'),
   Input(component_id = 'file-format', component_property = 'value')]
)
def download(value, hourly, index, fformat):
  has_time = False
  cursor.execute("select * from prev_c where id = %s", [index])
  time_bounds = cursor.fetchall()[0][1:3]
  if value == 'monthly':
    if hourly['layout']['xaxis'].has_key('autorange'):
      start_date = datetime.strptime(str(hourly['layout']['xaxis']['range'][0]), '%Y-%m-%d %H:%M:%S') - timedelta(days=1)
      try:
        cursor.execute("select * from monthly where date between %s and %s order by date ASC, time ASC", [start_date, hourly['layout']['xaxis']['range'][1]])
        has_time = True
      except:
        cursor.execute("select * from monthly where date between %s and %s order by date ASC", [start_date, hourly['layout']['xaxis']['range'][1]])
      raw_data_h = cursor.fetchall()
    else:
      start_date = datetime.strptime(str(time_bounds[0]), '%Y-%m-%d %H:%M:%S.%f') - timedelta(days=1)
      try:
        cursor.execute("select * from monthly where date between %s and %s order by date ASC, time ASC", [start_date, time_bounds[1]])
        has_time = True
      except:
        cursor.execute("select * from monthly where date between %s and %s order by date ASC", [start_date, time_bounds[1]])
      raw_data_h = cursor.fetchall()

  elif value == 'daily':
    if hourly['layout']['xaxis'].has_key('autorange'):
      start_date = datetime.strptime(str(hourly['layout']['xaxis']['range'][0]), '%Y-%m-%d %H:%M:%S') - timedelta(days=1)
      try:
        cursor.execute("select * from daily where date between %s and %s order by date ASC, time ASC", [start_date, hourly['layout']['xaxis']['range'][1]])
        has_time = True
      except:
        cursor.execute("select * from daily where date between %s and %s order by date ASC", [start_date, hourly['layout']['xaxis']['range'][1]])
      raw_data_h = cursor.fetchall()
    else:
      start_date = datetime.strptime(str(time_bounds[0]), '%Y-%m-%d %H:%M:%S.%f') - timedelta(days=1)
      try:
        cursor.execute("select * from daily where date between %s and %s order by date ASC, time ASC", [start_date, time_bounds[1]])
        has_time = True
      except:
        cursor.execute("select * from daily where date between %s and %s order by date ASC", [start_date, time_bounds[1]])
      raw_data_h = cursor.fetchall()

  elif value == 'hourly':
    if hourly['layout']['xaxis'].has_key('autorange'):
      start_date = datetime.strptime(str(hourly['layout']['xaxis']['range'][0]), '%Y-%m-%d %H:%M:%S') - timedelta(days=1)
      try:
        cursor.execute("select * from hourly where date between %s and %s order by date ASC, time ASC", [start_date, hourly['layout']['xaxis']['range'][1]])
        has_time = True
      except:
        cursor.execute("select * from hourly where date between %s and %s order by date ASC", [start_date, hourly['layout']['xaxis']['range'][1]])
      raw_data_h = cursor.fetchall()
    else:
      start_date = datetime.strptime(str(time_bounds[0]), '%Y-%m-%d %H:%M:%S.%f') - timedelta(days=1)
      try:
        cursor.execute("select * from hourly where date between %s and %s order by date ASC, time ASC", [start_date, time_bounds[1]])
        has_time = True
      except:
        cursor.execute("select * from hourly where date between %s and %s order by date ASC", [start_date, time_bounds[1]])
      raw_data_h = cursor.fetchall()

  elif value == 'entries':
    if hourly['layout']['xaxis'].has_key('autorange'):
      start_date = datetime.strptime(str(hourly['layout']['xaxis']['range'][0]), '%Y-%m-%d %H:%M:%S') - timedelta(days=1)
      try:
        cursor.execute("select * from entries where date between %s and %s order by date ASC, time ASC", [start_date, hourly['layout']['xaxis']['range'][1]])
        has_time = True
      except:
        cursor.execute("select * from entries where date between %s and %s order by date ASC", [start_date, hourly['layout']['xaxis']['range'][1]])
      raw_data_h = cursor.fetchall()
    else:
      start_date = datetime.strptime(str(time_bounds[0]), '%Y-%m-%d %H:%M:%S.%f') - timedelta(days=1)
      try:
        cursor.execute("select * from entries where date between %s and %s order by date ASC, time ASC", [start_date, time_bounds[1]])
        has_time = True
      except:
        cursor.execute("select * from entries where date between %s and %s order by date ASC", [start_date, time_bounds[1]])
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
  if fformat == 'csv':
    csv_string = df.to_csv(index = False, encoding = 'utf-8')
  elif fformat == 'json':
    csv_string = df.to_json()
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
  global cursor
  counter += 1
  cursor.execute("insert into prev_m(x_start, x_end, y_start, y_end, x_changed, y_changed) values('True', 'True', 'True', 'True', 0, 0)")
  cursor.execute("insert into prev_b(x_start, x_end, y_start, y_end, x_changed, y_changed) values('True', 'True', 'True', 'True', 0, 0)")
  cursor.execute("insert into prev_h(x_start, x_end, y_start, y_end, x_changed, y_changed) values('True', 'True', 'True', 'True', 0, 0)")
  cursor.execute("insert into prev_d(x_start, x_end, y_start, y_end, x_changed, y_changed) values('True', 'True', 'True', 'True', 0, 0)")
  cursor.execute("insert into prev_c(x_start, x_end, y_start, y_end) values('True', 'True', 'True', 'True')")
  cursor.execute("insert into last_picked(picked) values('None')")
  
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
  cnx.autocommit(True)
  cursor = cnx.cursor()

  try:
    cursor.execute("drop table last_picked")
    cursor.execute("drop table prev_m")
    cursor.execute("drop table prev_d")
    cursor.execute("drop table prev_h")
    cursor.execute("drop table prev_b")
    cursor.execute("drop table prev_c")
  except:
    pass

  cursor.execute("create table last_picked(id int not null auto_increment, picked char(4), primary key (id))")
  cursor.execute("create table prev_m(id int not null auto_increment, x_start tinytext, x_end tinytext, y_start tinytext, y_end tinytext, x_changed int, y_changed int, primary key (id))")
  cursor.execute("create table prev_d(id int not null auto_increment, x_start tinytext, x_end tinytext, y_start tinytext, y_end tinytext, x_changed int, y_changed int, primary key (id))")
  cursor.execute("create table prev_h(id int not null auto_increment, x_start tinytext, x_end tinytext, y_start tinytext, y_end tinytext, x_changed int, y_changed int, primary key (id))")
  cursor.execute("create table prev_b(id int not null auto_increment, x_start tinytext, x_end tinytext, y_start tinytext, y_end tinytext, x_changed int, y_changed int, primary key (id))")
  cursor.execute("create table prev_c(id int not null auto_increment, x_start tinytext, x_end tinytext, y_start tinytext, y_end tinytext, primary key(id))")

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

    html.Label('Select download format'),

    dcc.Dropdown(
      id = 'file-format',
      options = [{'label': 'CSV', 'value': 'csv'},
                 {'label': 'JSON', 'value': 'json'}],
      value = 'csv'
    ),

    html.A(
      children = 'Click to download',
      id = 'download',
      download = 'data.csv',
      href = '',
      target = '_blank'
    ),

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

