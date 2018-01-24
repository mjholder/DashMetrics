# DashMetrics

### Installing
To install, clone this repo and go to the directory where setup.py is located and run
```
# python setup.py bdist_rpm
```
Install the rpm
```
# yum install dist/DashMetrics-x.x_x.noarch.rpm
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

It takes, on average, 2 minutes for dm_populate to add 129,549 entries.
```
# dm_populate -h

-f        Specify the directory containing metric data files.
          (Required)
-i        Specify the IP the database you are connecting to
          is hosted on. Default is 'localhost'.
-u        The username for accessing the database.
          Default username is 'root'
-p        The password for accessing the database.
-d        Specify the name of the database. (Required)
-h        Displays this message and quits.
```
dm_dash runs the dash webapp on 0.0.0.0:8050 by default.
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
-d        The name of the database (Required)
-h        Displays this message and quits.
```
