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

def parse():
  with cnx:
    cursor = cnx.cursor()
    cursor.execute("create table queue(CLUSTER varchar(255), JOBID varchar(255), PPARTITION varchar(255), NNAME varchar(255), USER varchar(255), STATE varchar(255), RTIME varchar(255), TIME_LIMI varchar(255), NODES int, NODELIST TEXT, MIN_CPUS INT, CPUS float, PRIORITY INT, START_TIME varchar(255), FEATURES varchar(255), SCHEDNODES varchar(255))")
    in_file = open("/data/matt/squeue/2018-03-13/01-01-02.txt")
    
    cluster = ""
    for line in in_file.readlines():
      line_list = line.split()
      if len(line_list) > 2 and line_list[0] != 'JOBID':
         line_list[12] = line_list[12].replace('T', ' ')
         cursor.execute("insert into queue(CLUSTER, JOBID, PPARTITION, NNAME, USER, STATE, RTIME, TIME_LIMI, NODES, NODELIST, MIN_CPUS, CPUS, PRIORITY, START_TIME, FEATURES, SCHEDNODES) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [cluster] + line_list)
      elif len(line_list) == 2:
        cluster = line_list[1]      

def main():
  opts, _ = getopt(sys.argv[1:], "f:i:u:p:d:c:h")
  global cnx
  j_file = None
  j_file_path = ''

  for opt in opts:
    if opt[0] == '-c':
      j_file_path = opt[1]

  try:
    if j_file_path == '':
      resource_package = 'DashMetrics'
      resource_path = '/'.join(('statics', 'config.json'))
      conf = pkg_resources.resource_stream(resource_package, resource_path)
      j_file = json.load(conf)
    else:
      j_file = json.load(open(j_file_path))
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
  parse()
main()
