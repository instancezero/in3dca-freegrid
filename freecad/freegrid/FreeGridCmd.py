import os
import random

import FreeCAD
import FreeCADGui
import Part
from FreeCAD import Base, Placement, Rotation
from freecad.freegrid import UIPATH
from freecad.freegrid.in3dca import StorageBox, StorageGrid

from TranslateUtils import translate

# NOTE: The variables used in the FreeGrid preference page are automatically saved because the UI file uses
# the FreeCAD custom `Gui::Pref*` Qt widgets. In the code you only need to read the values.
paramFreeGrid = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/FreeGrid")


class StorageObject:
    """Base class for all objects."""

    def __init__(self, obj):
        """Initialize common properties."""
        self.just_created = True
        self.storageType = ""
        obj.addProperty(
            "App::PropertyInteger",
            "width",
            translate("StorageObject", "Size", "Property group"),
            translate(
                "StorageObject",
                "Number of 50[mm] units in X direction",
                "Property tooltip",
            ),
        ).width = 1
        obj.addProperty(
            "App::PropertyInteger",
            "depth",
            translate("StorageObject", "Size", "Property group"),
            translate(
                "StorageObject",
                "Number of 50[mm] units in Y direction",
                "Property tooltip",
            ),
        ).depth = 1
        obj.addProperty(
            "App::PropertyLength",
            "magnetDiameter",
            translate("StorageObject", "Magnet mount", "Property group"),
            translate("StorageObject", "Diameter of the magnet", "Property tooltip"),
        ).magnetDiameter = paramFreeGrid.GetString("magnetDiameter", "6mm")
        obj.addProperty(
            "App::PropertyLength",
            "magnetHeight",
            translate("StorageObject", "Magnet mount", "Property group"),
            translate("StorageObject", "Height of the magnet", "Property tooltip"),
        ).magnetHeight = paramFreeGrid.GetString("magnetHeight", "2mm")

    def descriptionStr(self, obj):
        """Return the designation of the storage object."""
        h = ""
        # FIXME: Make it work with inches
        if self.storageType == "StorageBox":
            h = "x{:.1f}mm".format(obj.height.Value)
        return self.storageType + "_" + str(obj.width) + "x" + str(obj.depth) + h

    def onDocumentRestored(self, obj):
        # If in the future more properties are added we can check here
        # to avoid breaking old objects, not neccessary as of now.
        pass

    def paramChanged(self, param, value):
        return getattr(self, param) != value


class StorageBoxObject(StorageObject):
    """Generate the Storage Box shape."""

    def __init__(self, obj):
        """Initialize storage box object, add properties."""
        super().__init__(obj)
        self.storageType = "StorageBox"
        obj.depth = paramFreeGrid.GetInt("boxDepth", 1)
        obj.width = paramFreeGrid.GetInt("boxWidth", 1)
        obj.Proxy = self
        # TODO: check if it works when default system is imperial
        obj.addProperty(
            "App::PropertyLength",
            "height",
            translate("StorageBoxObject", "Size", "Property group"),
            translate(
                "StorageBoxObject",
                "Height (in Z direction), enter value and unit\n" "example: 4cm, 1dm, 3in, 0.5ft",
                "Property tooltip",
            ),
        ).height = paramFreeGrid.GetString("boxHeight", "50mm")
        obj.addProperty(
            "App::PropertyInteger",
            "divisionsX",
            translate("StorageBoxObject", "Internal divisions", "Property group"),
            translate(
                "StorageBoxObject",
                "Number of divisions along the X axis",
                "Property tooltip",
            ),
        ).divisionsX = paramFreeGrid.GetInt("divisionsX", 1)
        obj.addProperty(
            "App::PropertyInteger",
            "divisionsY",
            translate("StorageBoxObject", "Internal divisions", "Property group"),
            translate(
                "StorageBoxObject",
                "Number of divisions along the Y axis",
                "Property tooltip",
            ),
        ).divisionsY = paramFreeGrid.GetInt("divisionsY", 1)
        obj.addProperty(
            "App::PropertyBool",
            "boxOpenFront",
            translate("StorageBoxObject", "Box features", "Property group"),
            translate("StorageBoxObject", "Leave front of box open", "Property tooltip"),
        ).boxOpenFront = paramFreeGrid.GetBool("boxOpenFront", False)
        obj.addProperty(
            "App::PropertyBool",
            "boxRamp",
            translate("StorageBoxObject", "Box features", "Property group"),
            translate("StorageBoxObject", "Add scoop inside front of box", "Property tooltip"),
        ).boxRamp = paramFreeGrid.GetBool("boxRamp", True)
        obj.addProperty(
            "App::PropertyBool",
            "boxGrip",
            translate("StorageBoxObject", "Box features", "Property group"),
            translate(
                "StorageBoxObject",
                "Add grip/label area at rear of box",
                "Property tooltip",
            ),
        ).boxGrip = paramFreeGrid.GetBool("boxGrip", True)
        obj.addProperty(
            "App::PropertyLength",
            "boxGripDepth",
            translate("StorageBoxObject", "Box features", "Property group"),
            translate("StorageBoxObject", "Depth of grip (mm)", "Property tooltip"),
        ).boxGripDepth = paramFreeGrid.GetString("boxGripDepth", "15mm")
        obj.addProperty(
            "App::PropertyBool",
            "floorSupport",
            translate("StorageBoxObject", "Box features", "Property group"),
            translate("StorageBoxObject", "Add integral floor support", "Property tooltip"),
        ).floorSupport = paramFreeGrid.GetBool("floorSupport", True)
        obj.addProperty(
            "App::PropertyEnumeration",
            "magnetOption",
            translate("StorageBoxObject", "Magnet mount", "Property group"),
            translate("StorageBoxObject", "Options to add magnets", "Property tooltip"),
        ).magnetOption = ["allIntersections", "cornersOnly", "noMagnets"]
        obj.magnetOption = "allIntersections"

    def generate_box(self, obj) -> Part.Shape:
        """Create a box using the object properties as parameters."""
        box = StorageBox.StorageBox()
        # Size
        x = max(1, obj.width)
        y = max(1, obj.depth)
        z = max(10, obj.height.getValueAs("mm"))
        # dividers = divisions - 1
        box.divisions_x = max(1, obj.divisionsX)
        box.divisions_y = max(1, obj.divisionsY)
        # Features
        box.closed_front = not obj.boxOpenFront
        box.ramp = obj.boxRamp  # scoop
        depth = max(1, obj.boxGripDepth.getValueAs("mm"))
        if obj.boxGrip and depth > 0:
            box.grip_depth = depth
        box.floor_support = obj.floorSupport
        # Magnets
        mag_d = min(max(1, obj.magnetDiameter.getValueAs("mm")), 6.9)
        mag_h = min(max(0.2, obj.magnetHeight.getValueAs("mm")), 3.4)
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
        if self.just_created:
            self.just_created = False
            if paramFreeGrid.GetBool("randomColor", True):
                random_color = tuple(random.random() for _ in range(3))
                obj.ViewObject.ShapeColor = random_color


class StorageGridObject(StorageObject):
    """Generate the Storage Grid shape."""

    def __init__(self, obj):
        """Initialize storage grid object, add properties."""
        super().__init__(obj)
        self.storageType = "StorageGrid"
        obj.Proxy = self
        obj.depth = paramFreeGrid.GetInt("gridDepth", 2)
        obj.width = paramFreeGrid.GetInt("gridWidth", 3)
        obj.addProperty(
            "App::PropertyBool",
            "cornerConnectors",
            translate("StorageGridObject", "Grid features", "Property group"),
            translate(
                "StorageGridObject",
                "Space for locking connectors at outside corners",
                "Property tooltip",
            ),
        ).cornerConnectors = paramFreeGrid.GetBool("cornerConnectors", True)
        obj.addProperty(
            "App::PropertyBool",
            "isSubtractive",
            translate("StorageGridObject", "Grid features", "Property group"),
            translate(
                "StorageGridObject",
                "Create a grid suitable for subtractive manufacturing",
                "Property tooltip",
            ),
        ).isSubtractive = False
        obj.addProperty(
            "App::PropertyLength",
            "extraBottom",
            translate("StorageGridObject", "Grid features", "Property group"),
            translate(
                "StorageGridObject",
                "Extra thickness under grid (mm)",
                "Property tooltip",
            ),
        ).extraBottom = "16mm"
        obj.addProperty(
            "App::PropertyBool",
            "includeMagnets",
            translate("StorageGridObject", "Magnet mount", "Property group"),
            translate("StorageGridObject", "Include magnet receptacles", "Property tooltip"),
        ).includeMagnets = paramFreeGrid.GetBool("includeMagnets", True)

    def generate_grid(self, obj) -> Part.Shape:
        """Create a grid using the object properties as parameters."""
        grid = StorageGrid.StorageGrid()
        # Size
        x = max(1, obj.width)
        y = max(1, obj.depth)
        # Features
        grid.corner_connectors = obj.cornerConnectors
        grid.is_subtractive = obj.isSubtractive
        extra_bottom = max(0, obj.extraBottom.getValueAs("mm"))
        # Magnets
        mag_d = min(max(1, obj.magnetDiameter.getValueAs("mm")), 6.9)
        mag_h = min(max(0.2, obj.magnetHeight.getValueAs("mm")), 3.4)
        grid.magnets = obj.includeMagnets

        return grid.make(x, y, mag_d, mag_h, extra_bottom)

    def execute(self, obj):
        """Create the requested storage grid object."""
        obj.Shape = self.generate_grid(obj)
        obj.Placement = Placement(Base.Vector(0.0, 0.0, -3.2), Rotation())
        obj.Label = self.descriptionStr(obj)
        if self.just_created:
            self.just_created = False
            if paramFreeGrid.GetBool("randomColor", True):
                random_color = tuple(random.random() for _ in range(3))
                obj.ViewObject.ShapeColor = random_color


class SketchUI:
    """
    Generate a sketch of an NxM storage box using a dockable user interface.
    Attributes:
    view: The view to which the sketch UI is attached.
    form: The PySide UI form representing the sketch UI.
    """

    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(UIPATH, "sketch.ui"))
        self.form.sketch_x.setRange(1, 50)
        self.form.sketch_x.setValue(1)
        self.form.sketch_y.setRange(1, 50)
        self.form.sketch_y.setValue(1)

        FreeCADGui.Control.showDialog(self)

    def accept(self):
        """Generate the sketch and close the dialog. (OK button)."""
        box = StorageBox.StorageBox()
        box.closed_front = not self.form.sketch_open_front.isChecked()
        box.insert_as_sketch(self.form.sketch_x.value(), self.form.sketch_y.value())

        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Control.closeDialog()

    def reject(self):
        """Close the dialog without generating the sketch. (Close button)."""
        FreeCADGui.Control.closeDialog()
