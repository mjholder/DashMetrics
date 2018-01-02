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
dm_populate is used to populate a specified database with data.
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
