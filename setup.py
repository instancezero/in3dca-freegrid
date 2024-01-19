from setuptools import setup
from pyfreegrid import __version__
import os

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "freecad", "freegrid", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.freegrid',
      version=str(__version__),
      packages=['freecad',
                'freecad.freegrid',
                'pyfreegrid'],
      maintainer="hasecllu",
      maintainer_email="hasecilu@tuta.io",
      url="https://github.com/instancezero/in3dca-freegrid/tree/WorkBench",
      description="A simple tools workbench for generating\
      FreeGrid storage system components.",
      include_package_data=True)
