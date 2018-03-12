import MySQLdb as mysqldb
import os
import sys
import json
import pkg_resources
from getopt import getopt

cnx = None

def usage():
  print " -f        Specify the directory containing metric data files."
  print "           (Required)"
  print " -i        Specify the IP the database you are connecting to"
  print "           is hosted on. Default is 'localhost'."
  print " -u        The username for accessing the database."
  print "           Default username is 'root'"
  print " -p        The password for accessing the database."
  print " -d        Specify the name of the database. Default is sdiag"
  print " -c        Specify a path to load a custom config.json."
  print " -h        Displays this message and quits."

# this takes data from an input file and places the data into the entries table
def parse(in_file, filename):
  date = ''
  time = ''
  main_l = 0
  back_l = 0
  back_m = 0
  
  months = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12' 
  }

  is_main = True
  try:
    for i, line in enumerate(in_file):
      # Date and Time
      if line.startswith('sdiag'):
        temp = line.split()
        if len(temp[5]) > 1:
          date = temp[7] + '-' + months.get(temp[4]) + '-' + temp[5]
        else:
          date = temp[7] + '-' + months.get(temp[4]) + '-0' + temp[5]

        time = temp[6]

      # Last Cycle
      if line.startswith('\tLast cycle:'):
        if is_main:
          main_l = line.split()[2]
        else:
          back_l = line.split()[2]
   
      # Mean Cycle
      if line.startswith('\tMean cycle:'):
        if is_main:
          is_main = False
        else:
          back_m = line.split()[2]
          break
  except:
    print("Error with file: " + str(filename))

  if date != '':
    with cnx:
      cursor = cnx.cursor()
      cursor.execute("insert into entries(date, time, main_last, backfill_last, backfill_mean) values('" + date + "', '" + time + "', " + str(main_l) + ", " + str(back_l) + ", " + str(back_m) + ")") 

# iterate through every input data file and create the entries table
def bulk(path):
  with cnx:
    cursor = cnx.cursor()
#   This table will hold the original data points
    try:
      cursor.execute("create table entries(date DATE, time TIME, main_last INT, backfill_last INT, backfill_mean INT)")
    except:
      print("table entries already exists")

  for directory in os.listdir(path):
    for filename in os.listdir(path+directory):
      i = open(path+directory+'/'+filename)
      parse(i, filename)
      i.close()

# populates the hourly table
def hourly():
  with cnx:
    cursor = cnx.cursor()
    cursor.execute("select * from entries order by date(date) asc, time(time) asc")
    entries = cursor.fetchall()
    cur_time = 0
    count = 0
    cur_date = str(entries[0][0])
    avgs = {
      'ml': 0,
      'bl': 0,
      'bm': 0
    }
    try:
      cursor.execute("create table hourly(date DATE, time TIME, main_last INT, backfill_last INT, backfill_mean INT)")
    except:
      print("hourly table already exists")

    for entry in entries:
      if(((entry[1].seconds - cur_time) >= 3600 or cur_date != str(entry[0])) and count != 0):
        cur_time = entry[1].seconds
        cur_date = str(entry[0])
        cursor.execute("insert into hourly(date, time, main_last, backfill_last, backfill_mean) values('" + cur_date + "', '" + str(entry[1]) + "', " + str(avgs['ml']/count) + ", " + str(avgs['bl']/count) + ", " + str(avgs['bm']/count) + ")")
        avgs['ml'] = 0
        avgs['bl'] = 0
        avgs['bm'] = 0
        count = 0
      else:
        count += 1
        avgs['ml'] += entry[2]
        avgs['bl'] += entry[3]
        avgs['bm'] += entry[4]

    cursor.execute("insert into hourly(date, time, main_last, backfill_last, backfill_mean) values('" + cur_date + "', '" + str(entry[1]) + "', " + str(avgs['ml']/count) + ", " + str(avgs['bl']/count) + ", " + str(avgs['bm']/count) + ")")
      
# populates the daily table
def daily():
  with cnx:
    cursor = cnx.cursor()
    cursor.execute("select * from hourly")
    entries = cursor.fetchall()
    cur_date = str(entries[0][0])
    count = 0
    avgs = {
      'ml': 0,
      'bl': 0,
      'bm': 0
    }

    try:
      cursor.execute("create table daily(date Date, main_last INT, backfill_last INT, backfill_mean INT)")
    except:
      print("daily table already exists")

    for entry in entries:
      if(cur_date != str(entry[0]) and count != 0):
        cursor.execute("insert into daily(date, main_last, backfill_last, backfill_mean) values('" + str(cur_date) + "', " + str(avgs['ml']/count) + ", " + str(avgs['bl']/count) + ", " + str(avgs['bm']/count) + ")")
        avgs['ml'] = 0
        avgs['bl'] = 0
        avgs['bm'] = 0
        count = 0
        cur_date = str(entry[0])
      else:
        count += 1
        avgs['ml'] += entry[2]
        avgs['bl'] += entry[3]
        avgs['bm'] += entry[4]
    
    cursor.execute("insert into daily(date, main_last, backfill_last, backfill_mean) values('" + str(cur_date) + "', " + str(avgs['ml']/count) + ", " + str(avgs['bl']/count) + ", " + str(avgs['bm']/count) + ")")

# populates the monthly table
def monthly():
  with cnx:
    cursor = cnx.cursor()
    cursor.execute("select * from daily order by date asc")
    entries = cursor.fetchall()
    cur_month = entries[0][0].month
    cur_date = str(entries[0][0])
    count = 0
    avgs = {
      'ml': 0,
      'bl': 0,
      'bm': 0
    }

    try:
      cursor.execute("create table monthly(date Date, main_last INT, backfill_last INT, backfill_mean INT)")
    except:
      print("monthly table already exists")

    for entry in entries:
      if(cur_month != entry[0].month and count != 0):
        cur_month = entry[0].month
        cursor.execute("insert into monthly(date, main_last, backfill_last, backfill_mean) values('" + str(cur_date) + "', " + str(avgs['ml']/count) + ", " + str(avgs['bl']/count) + ", " + str(avgs['bm']/count) + ")")
        avgs['ml'] = 0
        avgs['bl'] = 0
        avgs['bm'] = 0
        count = 0
        cur_date = str(entry[0])
      else:
        count += 1
        avgs['ml'] += entry[1]
        avgs['bl'] += entry[2]
        avgs['bm'] += entry[3]

    cursor.execute("insert into monthly(date, main_last, backfill_last, backfill_mean) values('" + cur_date + "', " + str(avgs['ml']/count) + ", " + str(avgs['bl']/count) + ", " + str(avgs['bm']/count) + ")")

# main controlling function
def main():
  opts, _ = getopt(sys.argv[1:], "f:i:u:p:d:h")
  global cnx
  j_file = None
  j_file_path = ''

  for opt in opts:
    if opt[0] == '-c':
      j_file_path = opt[1]
      break

  try:
    if j_file_path == '':
      resource_package = 'DashMetrics'
      resource_path = '/'.join(('statics', 'config.json'))
      conf = pkg_resources.resource_stream(resource_package, resource_path)
      j_file = json.load(conf)
    else:
      j_file = json.load(conf)
  except:
    print 'ERROR: config.json is missing. Make sure config.json is in the'
    print 'statics directory when packaging or no config.json in specified path.'
    return

  f = j_file['directory']
  i = j_file['db_ip']
  u = j_file['db_username']
  p = j_file['db_password']
  d = j_file['db_name']

  for opt in opts:
    if opt[0] == '-f':
      f = opt[1]
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

  if f == '':
    print "You must provide a database name and directory path."
    usage()
    sys.exit(0)

  cnx = mysqldb.connect(i, u, p, d)

  print('Adding all entries')
  bulk(f)
  print('Creating hourly table')
  hourly()
  print('Creating daily table')
  daily()
  print('Creating monthly table')
  monthly()
  print('Done!')
