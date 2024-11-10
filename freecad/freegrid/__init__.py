import os
import FreeCAD

__version__ = "2.1.1"

path = os.path.join(os.path.dirname(__file__), "resources")

ICONPATH = os.path.join(path, "icons")
IMGPATH = os.path.join(path, "img")
TRANSLATIONSPATH = os.path.join(path, "translations")
UIPATH = os.path.join(path, "ui")

FREECADVERSION = float(FreeCAD.Version()[0] + "." + FreeCAD.Version()[1])

SPACING = 50  # mm


def get_icon_path(icon_name: str) -> str:
    """Returns the path to the SVG icon."""
    return os.path.join(ICONPATH, icon_name + ".svg")
