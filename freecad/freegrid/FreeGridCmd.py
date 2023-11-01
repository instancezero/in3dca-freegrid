import os
import Part
import FreeCAD
import FreeCADGui as Gui
from FreeCAD import Base, Placement, Rotation

from freecad.freegrid.in3dca import StorageBox, StorageGrid
from freecad.freegrid import FreeGridBase, FreeGridCmd
from freecad.freegrid import ICONPATH


pq = FreeCAD.Units.parseQuantity

StorageBoxParameters = {"width", "depth",
                        "height", "divisionsX", "divisionsY",
                        "boxOpenFront", "boxRamp", "boxGrip", "boxGripDepth",
                        "floorSupport",
                        "magnetDiameter", "magnetHeight", "magnetOption"}
StorageGridParameters = {"width", "depth", "cornerConnectors", "isSubstractive",
                         "extraBottom", "magnetDiameter", "magnetHeight",
                        "magnetOption"}

class StorageObject(FreeGridBase.BaseObject):
    """
    Class that controls the generation of all types of storage objects.
    """
    def __init__(self, obj, StorageType):
        super().__init__(obj)
        self.StorageType = StorageType
        self.VerifyMissingAttrs(obj, StorageType)

        obj.Proxy = self

    def VerifyMissingAttrs(self, obj, StorageType):
        """ Add missing attributes to objects """

        if StorageType == "StorageBox":
            # Storage Box parameters
            if not hasattr(obj, "height"):
                obj.addProperty("App::PropertyLength", "height", "Size",
                                "Height (in z direction), enter value and unit\n\
                                example: 4cm, 1dm, 3in, 0.5ft)").height = "5cm"
            if not hasattr(obj, "divisionsX"):
                obj.addProperty("App::PropertyInteger", "divisionsX", "Internal divisions",
                                "Number of divisions along the X axis)").divisionsX = 1
            if not hasattr(obj, "divisionsY"):
                obj.addProperty("App::PropertyInteger", "divisionsY", "Internal divisions",
                                "Number of divisions along the Y axis)").divisionsY = 1
            if not hasattr(obj, "boxOpenFront"):
                obj.addProperty("App::PropertyBool", "boxOpenFront", "Box features",
                                "Leave front of box open").boxOpenFront = False
            if not hasattr(obj, "boxRamp"):
                obj.addProperty("App::PropertyBool", "boxRamp", "Box features",
                                "Add scoop inside front of box").boxRamp = True
            if not hasattr(obj, "boxGrip"):
                obj.addProperty("App::PropertyBool", "boxGrip", "Box features",
                                "Add grip/label area at rear of box").boxGrip = True
            if not hasattr(obj, "boxGripDepth"):
                obj.addProperty("App::PropertyLength", "boxGripDepth", "Box features",
                                "Depth of grip (mm)").boxGripDepth = "15mm"
            if not hasattr(obj, "floorSupport"):
                obj.addProperty("App::PropertyBool", "floorSupport", "Box features",
                                "Add integral floor support").floorSupport = True
            if not hasattr(obj, "magnetOption"):
                obj.addProperty("App::PropertyEnumeration", "magnetOption", "Magnet mount",
                                "Options to add magnets").magnetOption = \
                                ["allIntersections", "cornersOnly", "noMagnets"]
                obj.magnetOption = "allIntersections"
        elif StorageType == "StorageGrid":
            # Storage Grid parameters
            if  not hasattr(obj, "cornerConnectors"):
                obj.addProperty("App::PropertyBool", "cornerConnectors", "Grid features",
                                "Space for locking connectors at outside corners"
                                ).cornerConnectors = True
            if not hasattr(obj, "isSubstractive"):
                obj.addProperty("App::PropertyBool", "isSubstractive", "Grid features",
                                "Create a grid suitable for substractive manufacturing"
                                ).isSubstractive = False
            if not hasattr(obj, "extraBottom"):
                obj.addProperty("App::PropertyLength", "extraBottom", "Grid features",
                                "Extra thickness under grid (mm)").extraBottom = "16mm"
            if not hasattr(obj, "includeMagnet"):
                obj.addProperty("App::PropertyBool", "includeMagnet", "Magnet mount",
                                "Include magnets receptacles").includeMagnet = True

    def onDocumentRestored(self, obj):
        # for backward compatibility: add missing attribute if needed
        self.VerifyMissingAttrs(obj, self.StorageType)

    def paramChanged(self, param, value):
        return getattr(self, param) != value

    def generate_box(self, obj) -> Part.Shape:
        """ Create a box using the object properties as parameters """
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
            box.boxGripDepth = depth
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

    def generate_grid(self, obj) -> Part.Shape:
        """ Create a box using the object properties as parameters """
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
        """ Create the object """

        if self.StorageType == "StorageBox":
            obj.Shape = self.generate_box(obj)
        elif self.StorageType == "StorageGrid":
            obj.Shape = self.generate_grid(obj)
            obj.Placement = Placement(Base.Vector(0.0, 0.0, -3.2), Rotation())

        # Set completed label
        obj.Label = FreeGridBase.descriptionStr(obj, self.StorageType)


class BaseCommand(object):
    NAME = ""
    FREEGRID_FUNCTION = None

    def __init__(self):
        pass

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        Gui.doCommandGui("import freecad.freegrid.FreeGridCmd")
        Gui.doCommandGui("freecad.freegrid.FreeGridCmd.{}.create()".format(
            self.__class__.__name__))
        FreeCAD.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")

    @classmethod
    def create(cls):
        if FreeCAD.GuiUp:
            body = Gui.ActiveDocument.ActiveView.getActiveObject("pdbody")
            part = Gui.ActiveDocument.ActiveView.getActiveObject("part")

            if body:
                obj = FreeCAD.ActiveDocument.addObject("PartDesign::FeaturePython", cls.NAME)
            else:
                obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", cls.NAME)

            ViewProvider(obj.ViewObject, cls.Pixmap)
            cls.FREEGRID_FUNCTION(obj, cls.NAME)

            if body:
                body.addObject(obj)
            elif part:
                part.Group += [obj]
        else:
            obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", cls.NAME)
            cls.FREEGRID_FUNCTION(obj)

        return obj

    def GetResources(self):
        return {'Pixmap': self.Pixmap,
                'MenuText': self.MenuText,
                'ToolTip': self.ToolTip}


class ViewProvider(object):
    def __init__(self, obj, icon_fn=None):
        # Set this object to the proxy object of the actual view provider
        obj.Proxy = self
        self._check_attr()
        dirname = os.path.dirname(__file__)
        self.icon_fn = icon_fn or os.path.join(dirname, "icons", "box.svg")

    def _check_attr(self):
        ''' Check for missing attributes. '''
        if not hasattr(self, "icon_fn"):
            setattr(self, "icon_fn", os.path.join(os.path.dirname(__file__), "icons", "box.svg"))

    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        self._check_attr()
        return self.icon_fn

    if (FreeCAD.Version()[0]+'.'+FreeCAD.Version()[1]) >= '0.22':
        def dumps(self):
            #        return {'ObjectName' : self.Object.Name}
            return None

        def loads(self, state):
            if state is not None:
                import FreeCAD
                doc = FreeCAD.ActiveDocument  # crap
                self.Object = doc.getObject(state['ObjectName'])
    else:
        def __getstate__(self):
            #        return {'ObjectName' : self.Object.Name}
            return None

        def __setstate__(self, state):
            if state is not None:
                doc = FreeCAD.ActiveDocument  # crap
                self.Object = doc.getObject(state['ObjectName'])


class CreateStorageBox(BaseCommand):
    NAME = "StorageBox"
    FREEGRID_FUNCTION = lambda obj, name="Box": FreeGridCmd.StorageObject(obj, name)
    Pixmap = os.path.join(ICONPATH, 'box.svg')
    MenuText = 'Storage box'
    # ToolTip = 'Create a storage box'
    ToolTip = "<img src=" + Pixmap + " align=left width='125' height='125' \
                type='svg/xml' />" + "<div align=center>Create a storage box</div>"

class CreateStorageGrid(BaseCommand):
    NAME = "StorageGrid"
    FREEGRID_FUNCTION = lambda obj, name="Grid": FreeGridCmd.StorageObject(obj, name)
    Pixmap = os.path.join(ICONPATH, 'grid.svg')
    MenuText = 'Storage grid'
    ToolTip = "<img src=" + Pixmap + " align=left width='125' height='125' \
                type='svg/xml' />" + "<div align=center>Create a storage grid</div>"

