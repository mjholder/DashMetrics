from setuptools import setup

setup(
  name = 'DashMetrics',
  version = '1.0',
  packages = ['DashMetrics'],
  include_package_data = True,
  entry_points = {
    'console_scripts': [
      'DashMetrics = DashMetrics.__main__:main'
    ]
  }
)
