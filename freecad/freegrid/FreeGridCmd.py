import os
import sys

import Part
import FreeCAD
import FreeCADGui as Gui

from PySide import QtGui
from FreeCAD import Base, Placement, Rotation

from TranslateUtils import translate
from freecad.freegrid import UIPATH
from freecad.freegrid.in3dca import StorageBox, StorageGrid


storage_box_parameters = {
    "width", "depth", "height", "divisionsX", "divisionsY",
    "boxOpenFront", "boxRamp", "boxGrip", "boxGripDepth",
    "floorSupport",
    "magnetDiameter", "magnetHeight", "magnetOption"
}
storage_grid_parameters = {
    "width", "depth", "cornerConnectors", "isSubstractive",
    "extraBottom",
    "magnetDiameter", "magnetHeight", "includeMagnet"
}

# Helper functions

def FSShowError():
    """Show traceback of system error."""
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


# Classes used to create the objects

class StorageObject:
    """Base class for all objects."""
    def __init__(self, obj):
        """ Initialize common properties """
        obj.addProperty("App::PropertyInteger", "width", "Size", translate(
            "StoragePropDesc", "Number of 50[mm] units in x direction")).width = 1
        obj.addProperty("App::PropertyInteger", "depth", "Size", translate(
            "StoragePropDesc", "Number of 50[mm] units in y direction")).depth = 1
        obj.addProperty("App::PropertyLength", "magnetDiameter", "Magnet mount",
            translate("StoragePropDesc", "Diameter of the magnet")
                        ).magnetDiameter = "6mm"
        obj.addProperty("App::PropertyLength", "magnetHeight", "Magnet mount",
            translate("StoragePropDesc", "Height of the magnet")).magnetHeight = "2mm"


    def descriptionStr(self, obj):
        """Return the designation of the storage object."""
        h = ""
        if self.storageType == "StorageBox":
            h = "x{:.1f}mm".format(obj.height.Value)
        return self.storageType + "_" + str(obj.width) + "x" + str(obj.depth) + h


    def onDocumentRestored(self, obj):
        # If in the future more properties are added we can check here
        # to avoid breaking old objects, not neccessary as of now.
        pass


    def paramChanged(self, param, value):
        return getattr(self, param) != value


class BoxObject(StorageObject):
    """Generate the Storage Box shape."""
    def __init__(self, obj):
        """Initialize storage box object, add properties."""
        super().__init__(obj)
        self.storageType = "StorageBox"
        obj.Proxy = self
        obj.addProperty("App::PropertyLength", "height", "Size", translate(
            "StoragePropDesc", "Height (in z direction), enter value and unit\n"\
            + "example: 4cm, 1dm, 3in, 0.5ft")).height = "5cm"
        obj.addProperty("App::PropertyInteger", "divisionsX", "Internal divisions",
            translate("StoragePropDesc", "Number of divisions along the X axis")
                        ).divisionsX = 1
        obj.addProperty("App::PropertyInteger", "divisionsY", "Internal divisions",
            translate("StoragePropDesc", "Number of divisions along the Y axis")
                        ).divisionsY = 1
        obj.addProperty("App::PropertyBool", "boxOpenFront", "Box features",
            translate("StoragePropDesc", "Leave front of box open")
                        ).boxOpenFront = False
        obj.addProperty("App::PropertyBool", "boxRamp", "Box features",
            translate("StoragePropDesc", "Add scoop inside front of box")
                        ).boxRamp = True
        obj.addProperty("App::PropertyBool", "boxGrip", "Box features",
            translate("StoragePropDesc", "Add grip/label area at rear of box")
                        ).boxGrip = True
        obj.addProperty("App::PropertyLength", "boxGripDepth", "Box features",
            translate("StoragePropDesc", "Depth of grip (mm)")).boxGripDepth = "15mm"
        obj.addProperty("App::PropertyBool", "floorSupport", "Box features",
            translate("StoragePropDesc", "Add integral floor support")
                        ).floorSupport = True
        obj.addProperty("App::PropertyEnumeration", "magnetOption", "Magnet mount",
            translate("StoragePropDesc", "Options to add magnets")).magnetOption = \
                        ["allIntersections", "cornersOnly", "noMagnets"]
        obj.magnetOption = "allIntersections"


    def generate_box(self, obj) -> Part.Shape:
        """Create a box using the object properties as parameters."""
        box = StorageBox.StorageBox()
        # Size
        x = max(1, obj.width)
        y = max(1, obj.depth)
        z = max(10, obj.height.getValueAs('mm'))
        # dividers = divisions - 1
        box.divisions_x = max(1, obj.divisionsX)
        box.divisions_y = max(1, obj.divisionsY)
        # Features
        box.closed_front = not obj.boxOpenFront
        box.ramp = obj.boxRamp # scoop
        depth = max(1, obj.boxGripDepth.getValueAs('mm'))
        if obj.boxGrip and depth > 0:
            box.grip_depth = depth
        box.floor_support = obj.floorSupport
        # Magnets
        mag_d = min(max(1, obj.magnetDiameter.getValueAs('mm')), 6.9)
        mag_h = min(max(0.2, obj.magnetHeight.getValueAs('mm')), 3.4)
        if obj.magnetOption == "noMagnets":
            box.magnets = False
            box.magnets_corners_only = True
        elif obj.magnetOption == "allIntersections":
            box.magnets = True
            box.magnets_corners_only = False
        elif obj.magnetOption == "cornersOnly":
            box.magnets = True
            box.magnets_corners_only = True
        box.as_components = False

        return box.make(x, y, z, mag_d, mag_h)


    def execute(self, obj):
        """Create the requested storage box object."""
        obj.Shape = self.generate_box(obj)
        obj.Label = self.descriptionStr(obj)


class GridObject(StorageObject):
    """Generate the Storage Grid shape."""
    def __init__(self, obj):
        """Initialize storage grid object, add properties."""
        super().__init__(obj)
        self.storageType = "StorageGrid"
        obj.Proxy = self
        obj.addProperty("App::PropertyBool", "cornerConnectors", "Grid features",
            translate("StoragePropDesc",
                      "Space for locking connectors at outside corners")
                        ).cornerConnectors = True
        obj.addProperty("App::PropertyBool", "isSubstractive", "Grid features",
            translate("StoragePropDesc",
                      "Create a grid suitable for substractive manufacturing")
                        ).isSubstractive = False
        obj.addProperty("App::PropertyLength", "extraBottom", "Grid features",
            translate("StoragePropDesc", "Extra thickness under grid (mm)")
                        ).extraBottom = "16mm"
        obj.addProperty("App::PropertyBool", "includeMagnet", "Magnet mount",
            translate("StoragePropDesc", "Include magnets receptacles")
                        ).includeMagnet = True


    def generate_grid(self, obj) -> Part.Shape:
        """Create a grid using the object properties as parameters."""
        grid = StorageGrid.StorageGrid()
        # Size
        x = max(1, obj.width)
        y = max(1, obj.depth)
        # Features
        grid.corner_connectors = obj.cornerConnectors
        grid.is_substractive = obj.isSubstractive
        extra_bottom = max(0, obj.extraBottom.getValueAs('mm'))
        # Magnets
        mag_d = min(max(1, obj.magnetDiameter.getValueAs('mm')), 6.9)
        mag_h = min(max(0.2, obj.magnetHeight.getValueAs('mm')), 3.4)
        grid.magnets = obj.includeMagnet

        return grid.make(x, y, mag_d, mag_h, extra_bottom)


    def execute(self, obj):
        """Create the requested storage grid object."""
        obj.Shape = self.generate_grid(obj)
        obj.Placement = Placement(Base.Vector(0.0, 0.0, -3.2), Rotation())
        obj.Label = self.descriptionStr(obj)


class Sketch():
    """Generate a sketch using a dockable user interface."""

    # TODO: If a StorageObject is selected, get their width and depth
    # and make the sketch of that size instead of displaying the UI.

    def __init__(self, view):
        self.view = view

        plus_int = QtGui.QIntValidator()
        plus_int.setBottom(1)

        self.form = Gui.PySideUic.loadUi(os.path.join(UIPATH, "sketch.ui"))
        self.form.inside_sketch_button.clicked.connect(self.createSketch)
        self.form.sketch_x.setValidator(plus_int)
        self.form.sketch_x.setMaxLength(3)
        self.form.sketch_x.setText("1")
        self.form.sketch_y.setValidator(plus_int)
        self.form.sketch_y.setMaxLength(3)
        self.form.sketch_y.setText("1")

        Gui.Control.showDialog(self)

    def createSketch(self):
        box = StorageBox.StorageBox()
        x = int(self.form.sketch_x.text())
        y = int(self.form.sketch_y.text())
        box.closed_front = not self.form.sketch_open_front.isChecked()
        box.insert_as_sketch(x, y)

        FreeCAD.ActiveDocument.recompute()
        Gui.Control.closeDialog()
