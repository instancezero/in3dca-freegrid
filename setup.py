from setuptools import setup
from pyfreegrid import __version__

setup(
    name="freecad.freegrid",
    version=str(__version__),
    packages=["freecad", "freecad.freegrid"],
    maintainer="hasecllu",
    maintainer_email="hasecilu@tuta.io",
    url="https://github.com/instancezero/in3dca-freegrid/tree/WorkBench",
    description="A simple tools workbench for generating\
      FreeGrid storage system components.",
    include_package_data=True,
)
