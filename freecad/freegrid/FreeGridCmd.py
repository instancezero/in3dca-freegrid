import os

import FreeCAD
import FreeCADGui
import Part
from FreeCAD import Placement, Rotation, Vector

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
        obj.Proxy = self  # Stores a reference to the Python instance in the FeaturePython object

        self.storageType = ""
        self.min_len_constraints = {"MagnetDiameter": 1, "MagnetHeight": 0.2}
        self.max_len_constraints = {"MagnetDiameter": 6.9, "MagnetHeight": 3.4}

        obj.addProperty(
            "App::PropertyIntegerConstraint",
            QT_TRANSLATE_NOOP("App::Property", "Width"),  # property
            QT_TRANSLATE_NOOP("App::Property", "Size"),  # group
            QT_TRANSLATE_NOOP(
                "App::Property", "Number of 50 mm units in the X direction of the object"
            ),  # tooltip
        ).Width = (1, 1, 50, 1)  # (Default, Minimum, Maximum, Step size)
        obj.addProperty(
            "App::PropertyIntegerConstraint",
            QT_TRANSLATE_NOOP("App::Property", "Depth"),
            QT_TRANSLATE_NOOP("App::Property", "Size"),
            QT_TRANSLATE_NOOP(
                "App::Property", "Number of 50 mm units in the Y direction of the object"
            ),
        ).Depth = (1, 1, 50, 1)  # (Default, Minimum, Maximum, Step size)
        obj.addProperty(
            "App::PropertyLength",
            QT_TRANSLATE_NOOP("App::Property", "MagnetDiameter"),
            QT_TRANSLATE_NOOP("App::Property", "Magnet mount"),
            QT_TRANSLATE_NOOP("App::Property", "Diameter of the magnets"),
        ).MagnetDiameter = paramFreeGrid.GetString("MagnetDiameter", "6mm")
        obj.addProperty(
            "App::PropertyLength",
            QT_TRANSLATE_NOOP("App::Property", "MagnetHeight"),
            QT_TRANSLATE_NOOP("App::Property", "Magnet mount"),
            QT_TRANSLATE_NOOP("App::Property", "Height of the magnets"),
        ).MagnetHeight = paramFreeGrid.GetString("MagnetHeight", "2mm")

        obj.addExtension("Part::AttachExtensionPython")
        obj.AttacherEngine = "Engine Plane"

    def check_limits(self, obj, prop: str):
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

    def descriptionStr(self, obj) -> str:
        """Return the designation of the storage object."""
        h = ""
        if self.storageType in ["StorageBox", "BitCartridgeHolder"]:
            (preferred, value, unit) = obj.Height.getUserPreferred()
            h = f"x{preferred}"
        return f"{self.storageType}_{obj.Width}x{obj.Depth}{h}"

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
        # No point having less than 2.6[mm] because geometry remains the same
        self.min_len_constraints["Height"] = 2.6
        self.min_len_constraints["BoxGripDepth"] = 1

        obj.Depth = (paramFreeGrid.GetInt("BoxDepth", 1), 1, 50, 1)
        obj.Width = (paramFreeGrid.GetInt("BoxWidth", 1), 1, 50, 1)

        obj.addProperty(
            "App::PropertyLength",
            QT_TRANSLATE_NOOP("App::Property", "Height"),
            QT_TRANSLATE_NOOP("App::Property", "Size"),
            QT_TRANSLATE_NOOP("App::Property", "Height of the object"),
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
            QT_TRANSLATE_NOOP("App::Property", "Leave the front of the box open"),
        ).BoxOpenFront = paramFreeGrid.GetBool("BoxOpenFront", False)
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "BoxRamp"),
            QT_TRANSLATE_NOOP("App::Property", "Box features"),
            QT_TRANSLATE_NOOP("App::Property", "Add a scoop inside the front of box"),
        ).BoxRamp = paramFreeGrid.GetBool("BoxRamp", True)
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "BoxGrip"),
            QT_TRANSLATE_NOOP("App::Property", "Box features"),
            QT_TRANSLATE_NOOP("App::Property", "Add grip/label area at the rear of box"),
        ).BoxGrip = paramFreeGrid.GetBool("BoxGrip", True)
        obj.addProperty(
            "App::PropertyLength",
            QT_TRANSLATE_NOOP("App::Property", "BoxGripDepth"),
            QT_TRANSLATE_NOOP("App::Property", "Box features"),
            QT_TRANSLATE_NOOP("App::Property", "Depth of the grip"),
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
                "App::Property", "Object position on the grid along the X axis.\nStarts at zero."
            ),
        ).PositionX = (0, 0, 50, 1)
        obj.addProperty(
            "App::PropertyIntegerConstraint",
            QT_TRANSLATE_NOOP("App::Property", "PositionY"),
            QT_TRANSLATE_NOOP("App::Property", "Position on grid"),
            QT_TRANSLATE_NOOP(
                "App::Property", "Object position on the grid along the Y axis.\nStarts at zero."
            ),
        ).PositionY = (0, 0, 50, 1)

    def onChanged(self, obj, prop: str):
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
        self.min_len_constraints["SideLength"] = 10

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

        obj.Depth = (paramFreeGrid.GetInt("GridDepth", 2), 1, 50, 1)
        obj.Width = (paramFreeGrid.GetInt("GridWidth", 3), 1, 50, 1)
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "CornerConnectors"),
            QT_TRANSLATE_NOOP("App::Property", "Grid features"),
            QT_TRANSLATE_NOOP("App::Property", "Add cavities for corner connectors"),
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
            QT_TRANSLATE_NOOP("App::Property", "Extra thickness under the grid"),
        ).ExtraBottomMaterial = "16mm"
        obj.setEditorMode("ExtraBottomMaterial", True)
        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "IncludeMagnets"),
            QT_TRANSLATE_NOOP("App::Property", "Magnet mount"),
            QT_TRANSLATE_NOOP("App::Property", "Include magnet receptacles"),
        ).IncludeMagnets = paramFreeGrid.GetBool("IncludeMagnets", True)

    def onChanged(self, obj, prop: str):
        """Verify length properties are inside limits and disable properties if needed"""

        self.check_limits(obj, prop)

        if prop == "IncludeMagnets":
            obj.setEditorMode("MagnetDiameter", not obj.IncludeMagnets)
            obj.setEditorMode("MagnetHeight", not obj.IncludeMagnets)
        elif prop == "IsSubtractive" and hasattr(obj, "ExtraBottomMaterial"):
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


class CornerConnectorObject:
    """Corner connector used to join grids at the corners."""

    def __init__(self, obj):
        """Initialize common properties."""
        obj.Proxy = self  # Stores a reference to the Python instance in the FeaturePython object

        obj.addProperty(
            "App::PropertyBool",
            QT_TRANSLATE_NOOP("App::Property", "Half"),
            QT_TRANSLATE_NOOP("App::Property", "Connector features"),
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Use an entire connector to join 4 grids.\nUse half connector to join 2 grids.",
            ),
        ).Half = paramFreeGrid.GetBool("Half", False)
        obj.addExtension("Part::AttachExtensionPython")
        obj.AttacherEngine = "Engine Plane"

    def onChanged(self, obj, prop: str):
        pass

    def execute(self, obj):
        """Create the requested bit cartridge holder object."""

        # Update position when attached-to object changes position
        obj.positionBySupport()

        # Draw corner-quarter and mirror it twice
        p0 = Vector(0, 0, 0)
        p1 = Vector(2.5, 0, 0)
        p2 = Vector(2.5, 0.5, 0)
        p3 = Vector(3.2, 1.2, 0)
        p4 = Vector(4.4, 1.2, 0)
        p5 = Vector(4.4, 2.3, 0)
        p6 = Vector(2.3, 2.3, 0)
        p7 = Vector(2.3, 4.4, 0)
        p8 = Vector(1.2, 4.4, 0)
        p9 = Vector(1.2, 3.2, 0)
        p10 = Vector(0.5, 2.5, 0)
        p11 = Vector(0, 2.5, 0)

        l0 = Part.LineSegment(p0, p1)
        l1 = Part.LineSegment(p1, p2)
        l2 = Part.LineSegment(p2, p3)
        l3 = Part.LineSegment(p3, p4)
        l4 = Part.LineSegment(p4, p5)
        l5 = Part.LineSegment(p5, p6)
        l6 = Part.LineSegment(p6, p7)
        l7 = Part.LineSegment(p7, p8)
        l8 = Part.LineSegment(p8, p9)
        l9 = Part.LineSegment(p9, p10)
        l10 = Part.LineSegment(p10, p11)
        l11 = Part.LineSegment(p11, p0)

        # Create the shape and wire
        shape = Part.Shape([l0, l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11])
        wire = Part.Wire(shape.Edges)
        face = Part.Face(wire)

        # Extrude the solid
        extrusion = face.extrude(Vector(0, 0, 1.9))
        e2 = extrusion.mirror(Vector(0, 0, 0), Vector(1, 0, 0))  # Mirror across the YZ plane
        extrusion = extrusion.fuse(e2)
        if not obj.Half:
            e2 = extrusion.mirror(Vector(0, 0, 0), Vector(0, 1, 0))  # Mirror across the XZ plane
            extrusion = extrusion.fuse(e2)
        obj.Shape = extrusion.removeSplitter()


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
