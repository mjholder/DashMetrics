# DashMetrics

### Required packages
```
# pip install dash==0.20.0
# pip install dash-renderer==0.11.2
# pip install dash-html-components==0.8.0
# pip install dash-core-components==0.18.0
# pip install plotly --upgrade
```
Also it is required to use a MySQL database.

### Installing from Source
To install, clone this repo
```
# git clone https://github.com/mjholder/DashMetrics.git
```
and go to the directory where setup.py is located and run
```
# python setup.py bdist_rpm
```
Install the rpm
```
# yum install dist/DashMetrics-x.x_x.noarch.rpm
```
### Installing with RPM
Download the rpm file and go to the directory where it's located, then install the rpm
```
# yum install DashMetrics-x.x_x.noarch.rpm
```
### Using
There are two commands to use
```
# dm_populate
and
# dm_dash
```
dm_populate is used to populate a specified database with data. It fills the specified database with 4 tables:
1. entries: this contains all the individual data points
2. hourly: this contains the average of the data points per hour
3. daily: this contains the average of the data points in hourly per day
4. monthly: this contains the average of the data points in daily per month

It takes, on average, 2 minutes for dm_populate to add 130,000 entries.
```
# dm_populate -h

-f        Specify the directory containing metric data files.
          (Required)
-i        Specify the IP the database you are connecting to
          is hosted on. Default is 'localhost'.
-u        The username for accessing the database.
          Default username is 'root'
-p        The password for accessing the database.
-d        Specify the name of the database. Default is sdiag.
-c        Specify a path to load a custom config.json.
-h        Displays this message and quits.
```
dm_dash runs the dash webapp. This is hosted on 0.0.0.0:8050 by default. This also fill the specified database with
6 tables that are used to store and compare data returned from users visiting the website. These tables get reset
each time dm_dash is started and each user has their own row.
```
# dm_dash -h

-w        Specify the ip for Dash to run on.
          Default ip is '0.0.0.0'.
-q        Specify the port for Dash to run on.
          Defualt port is '8050'.
-i        Specify the ip of the database you are
          connecting to. Default is 'localhost'.
-u        The username for accessing the database.
          Default username is 'root'.
-p        The password for accessing the database.
-d        The name of the database. Default is sdiag.
-c        Specify a path to load a custom config.json.
-h        Displays this message and quits.
```
When viewing the dash, the "All Points" graph is disabled by default due to it's tendencies to take a while to load/update.
### Uninstalling
To uninstall run
```
# yum remove DashMetrics
```
