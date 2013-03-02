import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup

setup(
  name='python-boilerplate',
  version='0.1dev',
  entry_points={
  'console_scripts': [
      'mybin = tina.mymodule:main'
    ]
  },
  test_suite='tina.test',
  packages=['tina'],
  license='Creative Commons Attribution-Noncommercial-Share Alike license',
  long_description=open('README.md').read(),
)
