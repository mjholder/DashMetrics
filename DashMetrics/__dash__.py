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

lock = threading.Lock()
defaults = {'h': ['', ''], 'd': ['', ''], 'm': ['', ''], 'b': ['', ''], 's': '', 'e': ''}
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
@app.callback(
  dash.dependencies.Output(component_id = 'daily', component_property = 'figure'),
  [dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'end_date'),
   dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'start_date'),
   dash.dependencies.Input(component_id = 'hourly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'daily', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'monthly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'bulk', component_property = 'relayoutData')]
)
def update_daily(end_date, start_date, h, d, m, b):
  global lock
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

  changed = 0
  lock.acquire()
  relay = None
  if b != None:
    if defaults['b'][0] != b.values()[0] or defaults['b'][1] != b.values()[1]:
      relay = b.values()
      #defaults['b'] = b.values()
      changed = 1

  if h != None:
    if defaults['h'][0] != h.values()[0] or defaults['h'][1] != h.values()[1]:
      relay = h.values()
      #defaults['h'] = h.values()
      changed = 1
  if d != None:
    if defaults['d'][0] != d.values()[0] or defaults['d'][1] != d.values()[1]:
      relay = d.values()
      #defaults['d'] = d.values()
      changed = 1
  if m != None:
    if defaults['m'][0] != m.values()[0] or defaults['m'][1] != m.values()[1]:
      relay = m.values()
      #defaults['m'] = m.values()
      changed = 1

  lock.release()

  if changed:
    return {'data':[
              {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
              {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
              {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
              ],
              'layout': {'title': 'Daily', 'xaxis': {'range': relay}}
    }
  print 'daily'
  return {
    'data':[
        {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
        {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
        {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
      ],
      'layout':{'title': 'Daily'}

  }

# Monthly
@app.callback(
  dash.dependencies.Output(component_id = 'monthly', component_property = 'figure'),
  [dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'end_date'),
   dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'start_date'),
   dash.dependencies.Input(component_id = 'hourly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'daily', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'monthly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'bulk', component_property = 'relayoutData')]
)
def update_monthly(end_date, start_date, h, d, m, b):
  global lock
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

  changed = 0
  lock.acquire()
  relay = None
  if b != None:
    if defaults['b'][0] != b.values()[0] or defaults['b'][1] != b.values()[1]:
      relay = b.values()
      defaults['b'] = b.values()
      changed = 1

  if h != None:
    if defaults['h'][0] != h.values()[0] or defaults['h'][1] != h.values()[1]:
      relay = h.values()
      defaults['h'] = h.values()
      changed = 1
  if d != None:
    if defaults['d'][0] != d.values()[0] or defaults['d'][1] != d.values()[1]:
      relay = d.values()
      defaults['d'] = d.values()
      changed = 1
  if m != None:
    if defaults['m'][0] != m.values()[0] or defaults['m'][1] != m.values()[1]:
      relay = m.values()
      defaults['m'] = m.values()
      changed = 1

  lock.release()

  if changed:
    return {'data':[
              {'x': data_m['date'], 'y': data_m['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
              {'x': data_m['date'], 'y': data_m['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
              {'x': data_m['date'], 'y': data_m['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
              ],
              'layout': {'title': 'Monthly', 'xaxis': {'range': relay}}
    }
  print 'monthly'
  return {
    'data':[
        {'x': data_m['date'], 'y': data_m['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
        {'x': data_m['date'], 'y': data_m['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
        {'x': data_m['date'], 'y': data_m['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
      ],
      'layout':{'title': 'Monthly'}
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
  global lock
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
  changed = 0
  lock.acquire()
  relay = None
  if b != None:
    if defaults['b'][0] != b.values()[0] or defaults['b'][1] != b.values()[1]:
      relay = b.values()
      #defaults['b'] = b.values()
      changed = 1

  if h != None:
    if defaults['h'][0] != h.values()[0] or defaults['h'][1] != h.values()[1]:
      relay = h.values()
      #defaults['h'] = h.values()
      changed = 1
  if d != None:
    if defaults['d'][0] != d.values()[0] or defaults['d'][1] != d.values()[1]:
      relay = d.values()
      #defaults['d'] = d.values()
      changed = 1
  if m != None:
    if defaults['m'][0] != m.values()[0] or defaults['m'][1] != m.values()[1]:
      relay = m.values()
      #defaults['m'] = m.values()
      changed = 1

  lock.release()
  if changed:
    return {'data':[
              {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
              {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
              {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
              ],
              'layout': {'title': 'Hourly', 'xaxis': {'range': relay}}
    }
  print 'hourly'
  return {
    'data':[
        {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
        {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
        {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
      ],
      'layout':{'title': 'Hourly'}
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
@app.callback(
  dash.dependencies.Output(component_id = 'bulk', component_property = 'figure'),
  [dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'end_date'),
   dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'start_date'),
   dash.dependencies.Input(component_id = 'activator', component_property = 'values'),
   dash.dependencies.Input(component_id = 'hourly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'daily', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'monthly', component_property = 'relayoutData'),
   dash.dependencies.Input(component_id = 'bulk', component_property = 'relayoutData')]
)
def update_bulk(end_date, start_date, values, h, d, m, b):
  global defaults
  global lock
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

    changed = 0
    lock.acquire()
    relay = None
    if b != None:
      if defaults['b'][0] != b.values()[0] or defaults['b'][1] != b.values()[1]:
        relay = b.values()
        #defaults['b'] = b.values()
        changed = 1
    if h != None:
      if defaults['h'][0] != h.values()[0] or defaults['h'][1] != h.values()[1]:
        relay = h.values()
        #defaults['h'] = h.values()
        changed = 1
    if d != None:
      if defaults['d'][0] != d.values()[0] or defaults['d'][1] != d.values()[1]:
        relay = d.values()
        #defaults['d'] = d.values()
        changed = 1
    if m != None:
      if defaults['m'][0] != m.values()[0] or defaults['m'][1] != m.values()[1]:
        relay = m.values()
        #defaults['m'] = m.values()
        changed = 1

    lock.release()
    if changed:
      return {'data':[
              {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
              {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
              {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
              ],
              'layout': {'title': 'All Points', 'xaxis': {'range': relay}}
      }
    print 'bulk'
    return {
      'data':[
          {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
          {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
          {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
        ],
        'layout':{'title': 'All Points'}
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
  if __name__ == '__main__':
    app.run_server(debug=True, host=w, port=q)

main()
