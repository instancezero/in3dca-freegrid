import os

import FreeCAD
import FreeCADGui
import Part
from FreeCAD import Base, Placement, Rotation, Vector

from freecad.freegrid import SPACING, UIPATH
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

        self.storageType = ""
        self.min_len_constraints = {}
        self.max_len_constraints = {}

        obj.addProperty(
            "App::PropertyIntegerConstraint",
            QT_TRANSLATE_NOOP("App::Property", "Width"),  # property
            QT_TRANSLATE_NOOP("App::Property", "Size"),  # group
            QT_TRANSLATE_NOOP("App::Property", "Number of 50[mm] units in X direction"),  # tooltip
        ).Width = (
            1,
            1,
            50,
            1,
        )  # (Default, Minimum, Maximum, Step size)
        obj.addProperty(
            "App::PropertyIntegerConstraint",
            QT_TRANSLATE_NOOP("App::Property", "Depth"),
            QT_TRANSLATE_NOOP("App::Property", "Size"),
            QT_TRANSLATE_NOOP("App::Property", "Number of 50[mm] units in Y direction"),
        ).Depth = (
            1,
            1,
            50,
            1,
        )  # (Default, Minimum, Maximum, Step size)
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

        obj.addExtension("Part::AttachExtensionPython")
        obj.AttacherEngine = "Engine Plane"

    def check_limits(self, obj, prop):
        """Check if the property being modified is in the dictionaries and apply the constraint"""
        # Old-file compatibility
        if not hasattr(self, "min_len_constraints"):
            self.min_len_constraints = {}
        if not hasattr(self, "max_len_constraints"):
            self.max_len_constraints = {}

        if (
            prop in self.min_len_constraints
            and getattr(obj, prop).getValueAs("mm").Value < self.min_len_constraints[prop]
        ):
            setattr(obj, prop, str(self.min_len_constraints[prop]) + "mm")
        if (
            prop in self.max_len_constraints
            and getattr(obj, prop).getValueAs("mm").Value > self.max_len_constraints[prop]
        ):
            setattr(obj, prop, str(self.max_len_constraints[prop]) + "mm")

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

        # Define value constraints for length properties
        self.min_len_constraints = {
            "Height": 2.6,  # No point having less than 2.6[mm] because geometry remains the same
            "MagnetDiameter": 1,
            "MagnetHeight": 0.2,
            "BoxGripDepth": 1,
        }
        self.max_len_constraints = {"MagnetDiameter": 6.9, "MagnetHeight": 3.4}

        obj.Depth = (paramFreeGrid.GetInt("BoxDepth", 1), 1, 50, 1)
        obj.Width = (paramFreeGrid.GetInt("BoxWidth", 1), 1, 50, 1)
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
            "App::PropertyIntegerConstraint",
            QT_TRANSLATE_NOOP("App::Property", "DivisionsX"),
            QT_TRANSLATE_NOOP("App::Property", "Internal divisions"),
            QT_TRANSLATE_NOOP("App::Property", "Number of divisions along the X axis"),
        ).DivisionsX = (paramFreeGrid.GetInt("DivisionsX", 1), 1, 50, 1)
        obj.addProperty(
            "App::PropertyIntegerConstraint",
            QT_TRANSLATE_NOOP("App::Property", "DivisionsY"),
            QT_TRANSLATE_NOOP("App::Property", "Internal divisions"),
            QT_TRANSLATE_NOOP("App::Property", "Number of divisions along the Y axis"),
        ).DivisionsY = (paramFreeGrid.GetInt("DivisionsY", 1), 1, 50, 1)
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
        obj.addProperty(
            "App::PropertyIntegerConstraint",
            QT_TRANSLATE_NOOP("App::Property", "PositionX"),
            QT_TRANSLATE_NOOP("App::Property", "Position on grid"),
            QT_TRANSLATE_NOOP(
                "App::Property", "Box position on the grid in the X axis.\nStarts at zero."
            ),
        ).PositionX = (0, 0, 50, 1)
        obj.addProperty(
            "App::PropertyIntegerConstraint",
            QT_TRANSLATE_NOOP("App::Property", "PositionY"),
            QT_TRANSLATE_NOOP("App::Property", "Position on grid"),
            QT_TRANSLATE_NOOP(
                "App::Property", "Box position on the grid in the Y axis.\nStarts at zero."
            ),
        ).PositionY = (0, 0, 50, 1)

    def onChanged(self, obj, prop):
        """Verify length properties are inside limits and disable properties if needed"""

        self.check_limits(obj, prop)

        if prop == "MagnetOption":
            obj.setEditorMode("MagnetDiameter", obj.MagnetOption == "noMagnets")
            obj.setEditorMode("MagnetHeight", obj.MagnetOption == "noMagnets")
        elif prop == "PositionX":
            self.offset_changed = True
            if obj.PositionX < 0:
                obj.PositionX = 0
        elif prop == "PositionY":
            self.offset_changed = True
            if obj.PositionY < 0:
                obj.PositionY = 0
        # PositionX is created before PositionY, so check both exist before translating
        if (
            prop in ["PositionX", "PositionY"]
            and hasattr(obj, "PositionX")
            and hasattr(obj, "PositionY")
        ):
            obj.AttachmentOffset = Placement(
                Vector(obj.PositionX * SPACING, obj.PositionY * SPACING, 3.2),
                Rotation(0.0, 0.0, 0.0),
            )

    def generate_box(self, obj) -> Part.Shape:
        """Create a box using the object properties as parameters."""
        box = StorageBox.StorageBox()
        # Size
        x = obj.Width
        y = obj.Depth
        z = obj.Height.getValueAs("mm").Value
        # dividers = divisions - 1
        box.divisions_x = obj.DivisionsX
        box.divisions_y = obj.DivisionsY
        try:
            box.division_height = obj.DivisionHeight / 100.0  # users can't input bad data
        except AttributeError:
            box.division_height = 1.0
        FreeCAD.Console.PrintWarning(box.division_height)
        # Features
        box.closed_front = not obj.BoxOpenFront
        box.ramp = obj.BoxRamp  # scoop
        bg_depth = obj.BoxGripDepth.getValueAs("mm").Value
        if obj.BoxGrip and bg_depth > 0:
            box.grip_depth = bg_depth
        box.floor_support = obj.FloorSupport
        # Magnets
        mag_d = obj.MagnetDiameter.getValueAs("mm").Value
        mag_h = obj.MagnetHeight.getValueAs("mm").Value
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

        # Update position when attached-to object changes position
        obj.positionBySupport()

        # Generate the shape if it is null or if the property that
        # changed is not one of the offset components
        if obj.Shape.isNull() or not self.offset_changed:
            obj.Shape = self.generate_box(obj)
            obj.Label = self.descriptionStr(obj)

        self.offset_changed = False


class BitCartridgeHolderObject(StorageBoxObject):
    """Generate the Bit Cartridge Holder shape."""

    def __init__(self, obj):
        """Initialize storage box object, add properties."""

        super().__init__(obj)

        self.storageType = "BitCartridgeHolder"

        # Define value constraints for length properties
        self.min_len_constraints = {
            "Height": 2.6,  # No point having less than 2.6[mm] because geometry remains the same
            "MagnetDiameter": 1,
            "MagnetHeight": 0.2,
            "BoxGripDepth": 1,
            "SideLength": 10,
        }
        self.max_len_constraints = {"MagnetDiameter": 6.9, "MagnetHeight": 3.4}

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
        size = obj.SideLength.getValueAs("mm").Value
        x = obj.Width
        y = obj.Depth
        z = obj.Height.getValueAs("mm").Value
        # Features
        bit_c_h.floor_support = obj.FloorSupport
        # Magnets
        mag_d = obj.MagnetDiameter.getValueAs("mm").Value
        mag_h = obj.MagnetHeight.getValueAs("mm").Value
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

        # Update position when attached-to object changes position
        obj.positionBySupport()

        # Generate the shape if it is null or if the property that
        # changed is not one of the offset components
        if obj.Shape.isNull() or not self.offset_changed:
            obj.Shape = self.generate_bit_c_h(obj)
            obj.Label = self.descriptionStr(obj)

        self.offset_changed = False


class StorageGridObject(StorageObject):
    """Generate the Storage Grid shape."""

    def __init__(self, obj):
        """Initialize storage grid object, add properties."""

        super().__init__(obj)

        self.storageType = "StorageGrid"

        # Define value constraints for length properties
        self.min_len_constraints = {"MagnetDiameter": 1, "MagnetHeight": 0.2}
        self.max_len_constraints = {"MagnetDiameter": 6.9, "MagnetHeight": 3.4}

        obj.Proxy = self
        obj.Depth = (paramFreeGrid.GetInt("GridDepth", 2), 1, 50, 1)
        obj.Width = (paramFreeGrid.GetInt("GridWidth", 3), 1, 50, 1)
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
        obj.setEditorMode("ExtraBottomMaterial", True)
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "IncludeMagnets"),
            QT_TRANSLATE_NOOP("App::Property", "Magnet mount"),
            QT_TRANSLATE_NOOP("App::Property", "Include magnet receptacles"),
        ).IncludeMagnets = paramFreeGrid.GetBool("IncludeMagnets", True)

    def onChanged(self, obj, prop):
        """Verify length properties are inside limits and disable properties if needed"""

        self.check_limits(obj, prop)

        if prop == "IncludeMagnets":
            obj.setEditorMode("MagnetDiameter", not obj.IncludeMagnets)
            obj.setEditorMode("MagnetHeight", not obj.IncludeMagnets)
        elif prop == "IsSubtractive":
            obj.setEditorMode("ExtraBottomMaterial", not obj.IsSubtractive)

    def generate_grid(self, obj) -> Part.Shape:
        """Create a grid using the object properties as parameters."""
        grid = StorageGrid.StorageGrid()
        # Size
        x = obj.Width
        y = obj.Depth
        # Features
        grid.corner_connectors = obj.CornerConnectors
        grid.is_subtractive = obj.IsSubtractive
        extra_bottom = obj.ExtraBottomMaterial.getValueAs("mm").Value
        # Magnets
        mag_d = obj.MagnetDiameter.getValueAs("mm").Value
        mag_h = obj.MagnetHeight.getValueAs("mm").Value
        grid.magnets = obj.IncludeMagnets

        # NOTE: `x` and `y` are swapped in order to maintain
        # consistency with property names.
        return grid.make(x, y, mag_d, mag_h, extra_bottom)

    def execute(self, obj):
        """Create the requested storage grid object."""

        # Update position when attached-to object changes position.
        obj.positionBySupport()

        obj.Shape = self.generate_grid(obj)
        obj.Label = self.descriptionStr(obj)


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
