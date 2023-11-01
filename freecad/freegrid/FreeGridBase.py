import FreeCAD
import sys


class BaseObject:
    """ Base class for all objects """

    def __init__(self, obj):
        """ Initialize common properties """
        obj.addProperty("App::PropertyInteger", "width", "Size",
                        "Number of 50[mm] units in x direction").width = 1
        obj.addProperty("App::PropertyInteger", "depth", "Size",
                        "Number of 50[mm] units in y direction").depth = 1
        obj.addProperty("App::PropertyLength", "magnetDiameter", "Magnet mount",
                        "Diameter of the magnet").magnetDiameter = "6mm"
        obj.addProperty("App::PropertyLength", "magnetHeight", "Magnet mount",
                        "Height of the magnet").magnetHeight = "2mm"

# Helper functions

def descriptionStr(obj, t):
    """ Return the textual representation of the screw length x width """
    h = ""
    if t == "StorageBox":
        h = "x{:.1f}mm".format(obj.height.Value)

    return t + "_" + str(obj.width) + "x" + str(obj.depth) + h


def FSShowError():
    """ Show traceback of system error """
    lastErr = sys.exc_info()
    tb = lastErr[2]
    tbnext = tb
    x = 10
    while tbnext is not None and x > 0:
        FreeCAD.Console.PrintError(
            "At " + tbnext.tb_frame.f_code.co_filename + " Line " +
                str(tbnext.tb_lineno) + "\n"
        )
        tbnext = tbnext.tb_next
        x = x - 1
    FreeCAD.Console.PrintError(
        str(lastErr[1]) + ": " + lastErr[1].__doc__ + "\n")
