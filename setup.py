#import distribute_setup
import re
#distribute_setup.use_setuptools()

from setuptools import setup

# Parse version from _version.py.
version_file = "tina/_version.py"
version_str = open("tina/_version.py", "rt").read()
version_regex = r"^__version__\s*=\s*['\"]([^'\"]*)['\"]"
match = re.search(version_regex, version_str, re.MULTILINE)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Unable to find version string in '%s'" % version_file)

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
  version=version,
  url='https://github.com/RSEmail/tina/',
  packages=['tina', 'tina.commands'],
  license='GNU General Public License, version 3 (GPL-3.0)',
  long_description=open('README.md').read(),
)
