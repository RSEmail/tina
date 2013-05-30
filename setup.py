import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup

setup(
  name='tina',
  description='TINA Is Not Arif: A tool for tagging chef cookbooks and their dependencies.',
  maintainer='RSEmail',
  maintainer_email='tina-dev@mailtrust.com',
  entry_points={
  'console_scripts': [
      'tina = tina.tina:main'
    ]
  },
  test_suite='tina.test',
  version='0.6',
  url='https://github.com/RSEmail/tina/',
  packages=['tina'],
  license='GNU General Public License, version 3 (GPL-3.0)',
  long_description=open('README.md').read(),
)
