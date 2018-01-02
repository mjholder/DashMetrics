import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
from getopt import getopt
import sys
import MySQLdb as mysqldb

cnx = None
cursor = None

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
  [dash.dependencies.Input(component_id = 'date-picker-daily', component_property = 'end_date'),
   dash.dependencies.Input(component_id = 'date-picker-daily', component_property = 'start_date')]
)
def update_daily(end_date, start_date):
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
   dash.dependencies.Input(component_id = 'date-picker-monthly', component_property = 'start_date')]
)
def update_monthly(end_date, start_date):
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
  [dash.dependencies.Input(component_id = 'date-picker-hourly', component_property = 'end_date'),
   dash.dependencies.Input(component_id = 'date-picker-hourly', component_property = 'start_date')]
)
def update_hourly(end_date, start_date):
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

  return {
    'data':[
        {'x': data_h['date'], 'y': data_h['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
        {'x': data_h['date'], 'y': data_h['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
        {'x': data_h['date'], 'y': data_h['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
      ],
      'layout':{'title': 'Hourly'}
  }

# Bulk
@app.callback(
  dash.dependencies.Output(component_id = 'bulk', component_property = 'figure'),
  [dash.dependencies.Input(component_id = 'date-picker-bulk', component_property = 'end_date'),
   dash.dependencies.Input(component_id = 'date-picker-bulk', component_property = 'start_date')]
)
def update_bulk(end_date, start_date):
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

  return {
    'data':[
        {'x': data_t['date'], 'y': data_t['ml'], 'type': 'line', 'name': 'Main Last Cycle'},
        {'x': data_t['date'], 'y': data_t['bl'], 'type': 'line', 'name': 'Backfill Last Cycle'},
        {'x': data_t['date'], 'y': data_t['bm'], 'type': 'line', 'name': 'Backfill Mean Cycle'},
      ],
      'layout':{'title': 'All Points'}
  }

def main():
  opts, _ = getopt(sys.argv[1:], "w:q:i:u:p:d:h")
  global cnx
  global cursor
  i = 'localhost'
  u = 'root'
  p = ''
  d = ''
  q = ''
  w = ''

  for opt in opts:
    if opt[0] == '-w':
      w = opt[1]
    if opt[0] == '-q':
      q = opt[1]
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
    print "You must provide a database name and directory path."
    usage()
    sys.exit(0)

  cnx = mysqldb.connect(i, u, p, d)
  cursor = cnx.cursor()

# This is used for the day limits when seleting from the date range
  cursor.execute("select date from entries order by date ASC")
  time = cursor.fetchall()

  app = dash.Dash()

  app.layout = html.Div(children=[
    html.H1(children='Cycle Metrics'),

    dcc.Graph(
      id = 'monthly'
    ),

    dcc.DatePickerRange(
      id = 'date-picker-monthly',
      min_date_allowed = time[0][0],
      max_date_allowed = time[-1][0],
      start_date = time[0][0],
      end_date = time[-1][0]
    ),

      dcc.Graph(
      id = 'daily'
    ),

    dcc.DatePickerRange(
      id = 'date-picker-daily',
      min_date_allowed = time[0][0],
      max_date_allowed = time[-1][0],
      start_date = time[0][0],
      end_date = time[-1][0]
    ),

    dcc.Graph(
      id = 'hourly',
    ),

    dcc.DatePickerRange(
      id = 'date-picker-hourly',
      min_date_allowed = time[0][0],
      max_date_allowed = time[-1][0],
      start_date = time[0][0],
      end_date = time[-1][0]
    ),

    dcc.Graph(
      id = 'bulk',
    ),

    dcc.DatePickerRange(
      id = 'date-picker-bulk',
      min_date_allowed = time[0][0],
      max_date_allowed = time[-1][0],
      start_date = time[0][0],
      end_date = time[-1][0]
    ),

  ])
  #if __name__ == '__main__':
  app.run_server(debug=True, host='0.0.0.0')
