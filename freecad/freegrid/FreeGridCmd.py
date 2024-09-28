import os
import random

import FreeCAD
import FreeCADGui
import Part
from FreeCAD import Base, Placement, Rotation
from freecad.freegrid import UIPATH
from freecad.freegrid.in3dca import StorageBox, StorageGrid

QT_TRANSLATE_NOOP = FreeCAD.Qt.QT_TRANSLATE_NOOP
translate = FreeCAD.Qt.translate

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
            QT_TRANSLATE_NOOP("App::Property", "Width"),  # property
            QT_TRANSLATE_NOOP("App::Property", "Size"),  # group
            QT_TRANSLATE_NOOP("App::Property", "Number of 50[mm] units in X direction"),  # tooltip
        ).Width = 1
        obj.addProperty(
            "App::PropertyInteger",
            QT_TRANSLATE_NOOP("App::Property", "Depth"),
            QT_TRANSLATE_NOOP("App::Property", "Size"),
            QT_TRANSLATE_NOOP("App::Property", "Number of 50[mm] units in Y direction"),
        ).Depth = 1
        obj.addProperty(
            "App::PropertyLength",
            QT_TRANSLATE_NOOP("App::Property", "MagnetDiameter"),
            QT_TRANSLATE_NOOP("App::Property", "Magnet mount"),
            QT_TRANSLATE_NOOP("App::Property", "Diameter of the magnet"),
        ).MagnetDiameter = paramFreeGrid.GetString("MagnetDiameter", "6mm")
        obj.addProperty(
            "App::PropertyLength",
            QT_TRANSLATE_NOOP("App::Property", "MagnetHeight"),
            QT_TRANSLATE_NOOP("App::Property", "Magnet mount"),
            QT_TRANSLATE_NOOP("App::Property", "Height of the magnet"),
        ).MagnetHeight = paramFreeGrid.GetString("MagnetHeight", "2mm")

    def descriptionStr(self, obj):
        """Return the designation of the storage object."""
        h = ""
        # FIXME: Make it work with inches
        if self.storageType in ["StorageBox", "BitCartridgeHolder"]:
            h = "x{:.1f}mm".format(obj.Height.getValueAs("mm").Value)
        return self.storageType + "_" + str(obj.Width) + "x" + str(obj.Depth) + h

    def onDocumentRestored(self, obj):
        # If in the future more properties are added we can check here
        # to avoid breaking old objects, not necessary as of now.
        pass

    def paramChanged(self, param, value):
        return getattr(self, param) != value


class StorageBoxObject(StorageObject):
    """Generate the Storage Box shape."""

    def __init__(self, obj):
        """Initialize storage box object, add properties."""
        super().__init__(obj)
        self.storageType = "StorageBox"
        self.magnetOptions = ["allIntersections", "cornersOnly", "noMagnets"]
        obj.Depth = paramFreeGrid.GetInt("BoxDepth", 1)
        obj.Width = paramFreeGrid.GetInt("BoxWidth", 1)
        obj.Proxy = self
        # TODO: check if it works when default system is imperial
        obj.addProperty(
            "App::PropertyLength",
            QT_TRANSLATE_NOOP("App::Property", "Height"),
            QT_TRANSLATE_NOOP("App::Property", "Size"),
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Height (in Z direction), enter value and unit\nexample: 4cm, 1dm, 3in, 0.5ft",
            ),
        ).Height = paramFreeGrid.GetString("BoxHeight", "50mm")
        obj.addProperty(
            "App::PropertyInteger",
            QT_TRANSLATE_NOOP("App::Property", "DivisionsX"),
            QT_TRANSLATE_NOOP("App::Property", "Internal divisions"),
            QT_TRANSLATE_NOOP("App::Property", "Number of divisions along the X axis"),
        ).DivisionsX = paramFreeGrid.GetInt("DivisionsX", 1)
        obj.addProperty(
            "App::PropertyInteger",
            QT_TRANSLATE_NOOP("App::Property", "DivisionsY"),
            QT_TRANSLATE_NOOP("App::Property", "Internal divisions"),
            QT_TRANSLATE_NOOP("App::Property", "Number of divisions along the Y axis"),
        ).DivisionsY = paramFreeGrid.GetInt("DivisionsY", 1)
        obj.addProperty(
            "App::PropertyPercent",
            QT_TRANSLATE_NOOP("App::Property", "DivisionHeight"),
            QT_TRANSLATE_NOOP("App::Property", "Internal divisions"),
            QT_TRANSLATE_NOOP("App::Property", "Height of internal divisions relative to the box"),
        ).DivisionHeight = paramFreeGrid.GetInt("DivisionHeight", 100)
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "BoxOpenFront"),
            QT_TRANSLATE_NOOP("App::Property", "Box features"),
            QT_TRANSLATE_NOOP("App::Property", "Leave front of box open"),
        ).BoxOpenFront = paramFreeGrid.GetBool("BoxOpenFront", False)
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "BoxRamp"),
            QT_TRANSLATE_NOOP("App::Property", "Box features"),
            QT_TRANSLATE_NOOP("App::Property", "Add scoop inside front of box"),
        ).BoxRamp = paramFreeGrid.GetBool("BoxRamp", True)
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "BoxGrip"),
            QT_TRANSLATE_NOOP("App::Property", "Box features"),
            QT_TRANSLATE_NOOP("App::Property", "Add grip/label area at rear of box"),
        ).BoxGrip = paramFreeGrid.GetBool("BoxGrip", True)
        obj.addProperty(
            "App::PropertyLength",
            QT_TRANSLATE_NOOP("App::Property", "BoxGripDepth"),
            QT_TRANSLATE_NOOP("App::Property", "Box features"),
            QT_TRANSLATE_NOOP("App::Property", "Depth of grip (mm)"),
        ).BoxGripDepth = paramFreeGrid.GetString("BoxGripDepth", "15mm")
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "FloorSupport"),
            QT_TRANSLATE_NOOP("App::Property", "Box features"),
            QT_TRANSLATE_NOOP("App::Property", "Add integral floor support"),
        ).FloorSupport = paramFreeGrid.GetBool("FloorSupport", True)
        obj.addProperty(
            "App::PropertyEnumeration",
            QT_TRANSLATE_NOOP("App::Property", "MagnetOption"),
            QT_TRANSLATE_NOOP("App::Property", "Magnet mount"),
            QT_TRANSLATE_NOOP("App::Property", "Options to add magnets"),
        ).MagnetOption = self.magnetOptions
        obj.MagnetOption = self.magnetOptions[paramFreeGrid.GetInt("MagnetOption", 0)]

    def onChanged(self, obj, prop):
        if prop == "MagnetOption":
            obj.setEditorMode("MagnetDiameter", obj.MagnetOption == "noMagnets")
            obj.setEditorMode("MagnetHeight", obj.MagnetOption == "noMagnets")

    def generate_box(self, obj) -> Part.Shape:
        """Create a box using the object properties as parameters."""
        box = StorageBox.StorageBox()
        # Size
        x = max(1, obj.Width)
        y = max(1, obj.Depth)
        # No point having less than 2.6[mm] because geometry remains the same
        z = max(2.6, obj.Height.getValueAs("mm").Value)
        # dividers = divisions - 1
        box.divisions_x = max(1, obj.DivisionsX)
        box.divisions_y = max(1, obj.DivisionsY)
        try:
            box.division_height = min(100, max(1, obj.DivisionHeight)) / 100.0
        except AttributeError:
            box.division_height = 1.0
        FreeCAD.Console.PrintWarning(box.division_height)
        # Features
        box.closed_front = not obj.BoxOpenFront
        box.ramp = obj.BoxRamp  # scoop
        depth = max(1, obj.BoxGripDepth.getValueAs("mm").Value)
        if obj.BoxGrip and depth > 0:
            box.grip_depth = depth
        box.floor_support = obj.FloorSupport
        # Magnets
        mag_d = min(max(1, obj.MagnetDiameter.getValueAs("mm").Value), 6.9)
        mag_h = min(max(0.2, obj.MagnetHeight.getValueAs("mm").Value), 3.4)
        if obj.MagnetOption == "noMagnets":
            box.magnets = False
            box.magnets_corners_only = True
        elif obj.MagnetOption == "allIntersections":
            box.magnets = True
            box.magnets_corners_only = False
        elif obj.MagnetOption == "cornersOnly":
            box.magnets = True
            box.magnets_corners_only = True
        box.as_components = False

        # NOTE: `x` and `y` are swapped in order to maintain
        # consistency with property names.
        return box.make(x, y, z, mag_d, mag_h)

    def execute(self, obj):
        """Create the requested storage box object."""
        obj.Shape = self.generate_box(obj)
        obj.Label = self.descriptionStr(obj)
        if self.just_created:
            self.just_created = False
            if paramFreeGrid.GetBool("RandomColor", True):
                random_color = tuple(random.random() for _ in range(3))
                obj.ViewObject.ShapeColor = random_color


class BitCartridgeHolderObject(StorageBoxObject):
    """Generate the Bit Cartridge Holder shape."""

    def __init__(self, obj):
        """Initialize storage box object, add properties."""
        super().__init__(obj)
        self.storageType = "BitCartridgeHolder"
        self.magnetOptions = ["allIntersections", "cornersOnly", "noMagnets"]
        for prop in [
            "DivisionsX",
            "DivisionsY",
            "DivisionHeight",
            "BoxOpenFront",
            "BoxRamp",
            "BoxGrip",
            "BoxGripDepth",
        ]:
            obj.removeProperty(prop)
        obj.addProperty(
            "App::PropertyLength",
            QT_TRANSLATE_NOOP("App::Property", "SideLength"),
            QT_TRANSLATE_NOOP("App::Property", "Bit Cartridge Holder features"),
            QT_TRANSLATE_NOOP("App::Property", "Length of the longest side of the cartridge"),
        ).SideLength = "15mm"

    def generate_bit_c_h(self, obj) -> Part.Shape:
        """Create a bit cartridge holder using the object properties as parameters."""
        bit_c_h = StorageBox.BitCartridgeHolder()
        # Size
        size = max(10, obj.SideLength.getValueAs("mm").Value)
        x = max(1, obj.Width)
        y = max(1, obj.Depth)
        z = max(0, obj.Height.getValueAs("mm").Value)
        # Features
        bit_c_h.floor_support = obj.FloorSupport
        # Magnets
        mag_d = min(max(1, obj.MagnetDiameter.getValueAs("mm").Value), 6.9)
        mag_h = min(max(0.2, obj.MagnetHeight.getValueAs("mm").Value), 3.4)
        if obj.MagnetOption == "noMagnets":
            bit_c_h.magnets = False
            bit_c_h.magnets_corners_only = True
        elif obj.MagnetOption == "allIntersections":
            bit_c_h.magnets = True
            bit_c_h.magnets_corners_only = False
        elif obj.MagnetOption == "cornersOnly":
            bit_c_h.magnets = True
            bit_c_h.magnets_corners_only = True

        # NOTE: `x` and `y` are swapped in order to maintain
        # consistency with property names.
        return bit_c_h.make(x, y, z, mag_d, mag_h, size=size)

    def execute(self, obj):
        """Create the requested bit cartridge holder object."""
        obj.Shape = self.generate_bit_c_h(obj)
        obj.Label = self.descriptionStr(obj)
        if self.just_created:
            self.just_created = False
            if paramFreeGrid.GetBool("RandomColor", True):
                random_color = tuple(random.random() for _ in range(3))
                obj.ViewObject.ShapeColor = random_color


class StorageGridObject(StorageObject):
    """Generate the Storage Grid shape."""

    def __init__(self, obj):
        """Initialize storage grid object, add properties."""
        super().__init__(obj)
        self.storageType = "StorageGrid"
        obj.Proxy = self
        obj.Depth = paramFreeGrid.GetInt("GridDepth", 2)
        obj.Width = paramFreeGrid.GetInt("GridWidth", 3)
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "CornerConnectors"),
            QT_TRANSLATE_NOOP("App::Property", "Grid features"),
            QT_TRANSLATE_NOOP("App::Property", "Space for locking connectors at outside corners"),
        ).CornerConnectors = paramFreeGrid.GetBool("CornerConnectors", True)
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "IsSubtractive"),
            QT_TRANSLATE_NOOP("App::Property", "Grid features"),
            QT_TRANSLATE_NOOP(
                "App::Property", "Create a grid suitable for subtractive manufacturing"
            ),
        ).IsSubtractive = False
        obj.addProperty(
            "App::PropertyLength",
            QT_TRANSLATE_NOOP("App::Property", "ExtraBottomMaterial"),
            QT_TRANSLATE_NOOP("App::Property", "Grid features"),
            QT_TRANSLATE_NOOP("App::Property", "Extra thickness under grid (mm)"),
        ).ExtraBottomMaterial = "16mm"
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "IncludeMagnets"),
            QT_TRANSLATE_NOOP("App::Property", "Magnet mount"),
            QT_TRANSLATE_NOOP("App::Property", "Include magnet receptacles"),
        ).IncludeMagnets = paramFreeGrid.GetBool("IncludeMagnets", True)

    def onChanged(self, obj, prop):
        if prop == "IncludeMagnets":
            obj.setEditorMode("MagnetDiameter", not obj.IncludeMagnets)
            obj.setEditorMode("MagnetHeight", not obj.IncludeMagnets)

    def generate_grid(self, obj) -> Part.Shape:
        """Create a grid using the object properties as parameters."""
        grid = StorageGrid.StorageGrid()
        # Size
        x = max(1, obj.Width)
        y = max(1, obj.Depth)
        # Features
        grid.corner_connectors = obj.CornerConnectors
        grid.is_subtractive = obj.IsSubtractive
        extra_bottom = max(0, obj.ExtraBottomMaterial.getValueAs("mm").Value)
        # Magnets
        mag_d = min(max(1, obj.MagnetDiameter.getValueAs("mm").Value), 6.9)
        mag_h = min(max(0.2, obj.MagnetHeight.getValueAs("mm").Value), 3.4)
        grid.magnets = obj.IncludeMagnets

        # NOTE: `x` and `y` are swapped in order to maintain
        # consistency with property names.
        return grid.make(x, y, mag_d, mag_h, extra_bottom)

    def execute(self, obj):
        """Create the requested storage grid object."""
        obj.Shape = self.generate_grid(obj)
        obj.Label = self.descriptionStr(obj)
        if self.just_created:
            obj.Placement = Placement(Base.Vector(0.0, 0.0, -3.2), Rotation())
            self.just_created = False
            if paramFreeGrid.GetBool("RandomColor", True):
                random_color = tuple(random.random() for _ in range(3))
                obj.ViewObject.ShapeColor = random_color


class SketchUI:
    """Generate a sketch of an NxM storage box using a task panel."""

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
