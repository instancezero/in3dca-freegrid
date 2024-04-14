import os

import FreeCAD
import FreeCADGui as Gui
from PySide import QtGui
from freecad.freegrid import ICONPATH, IMGPATH, UIPATH
from freecad.freegrid.FreeGridCmd import SketchUI, StorageBoxObject, StorageGridObject
from freecad.freegrid.in3dca import StorageBox

from TranslateUtils import translate

paramFreeGrid = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/FreeGrid")


class ViewProvider(object):
    """
    Base class for defining the visual representation and behavior of
    FreeCAD objects in the GUI.
    """

    def __init__(self, obj, icon_fn=None):
        # Set this object to the proxy object of the actual view provider
        obj.Proxy = self
        self._check_attr()
        # dirname = os.path.dirname(__file__)
        self.icon_fn = icon_fn or os.path.join(ICONPATH, "FreeGrid.svg")

    def _check_attr(self):
        """Check for missing attributes."""
        if not hasattr(self, "icon_fn"):
            setattr(self, "icon_fn", os.path.join(ICONPATH, "FreeGrid.svg"))

    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        self._check_attr()
        return self.icon_fn

    if (FreeCAD.Version()[0] + "." + FreeCAD.Version()[1]) >= "0.22":

        def dumps(self):
            #        return {'ObjectName' : self.Object.Name}
            return None

        def loads(self, state):
            if state is not None:
                import FreeCAD

                doc = FreeCAD.ActiveDocument  # crap
                self.Object = doc.getObject(state["ObjectName"])

    else:

        def __getstate__(self):
            #        return {'ObjectName' : self.Object.Name}
            return None

        def __setstate__(self, state):
            if state is not None:
                doc = FreeCAD.ActiveDocument  # crap
                self.Object = doc.getObject(state["ObjectName"])


class BaseCommand(object):
    """Base class to prepare all the commands."""

    def __init__(self):
        pass

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        pass

    @property
    def view(self):
        """Get the active view in the FreeCAD GUI."""
        return Gui.ActiveDocument.ActiveView

    def toolTipWithIcon(self, icon_size: int = 125) -> str:
        """Return an html formatted string to include the command's icon along the tooltip."""
        if paramFreeGrid.GetBool("tooltipPicture", True):
            tt = (
                "<img src="
                + os.path.join(ICONPATH, self.pixmap)
                + " align=left width='"
                + str(icon_size)
                + "' height='"
                + str(icon_size)
                + "' type='svg/xml' />"
                + "<div align=center>"
                + self.toolTip
                + "</div>"
            )
        else:
            tt = self.toolTip

        return tt

    def GetResources(self):
        return {
            "Pixmap": self.pixmap,
            "MenuText": self.menuText,
            "ToolTip": self.toolTipWithIcon(paramFreeGrid.GetInt("iconTooltipSize", 125)),
        }


class BaseObjectCommand(BaseCommand):
    """
    Base class to prepare all the commands that create
    a Storage object in the GUI.
    """

    NAME = ""
    FREEGRID_FUNCTION = None

    def Activated(self):
        Gui.doCommandGui("import freecad.freegrid.commands")
        Gui.doCommandGui("freecad.freegrid.commands.{}.create()".format(self.__class__.__name__))
        FreeCAD.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")

    @classmethod
    def create(cls):
        """Create the generic object that will be converted to storage object."""
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument()

        doc.openTransaction(translate("Commands", "Create {}", "Transaction").format(cls.NAME))

        if FreeCAD.GuiUp:
            body = Gui.ActiveDocument.ActiveView.getActiveObject("pdbody")
            part = Gui.ActiveDocument.ActiveView.getActiveObject("part")

            if body:
                obj = FreeCAD.ActiveDocument.addObject("PartDesign::FeaturePython", cls.NAME)
            else:
                obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", cls.NAME)

            ViewProvider(obj.ViewObject, cls.pixmap)
            cls.FREEGRID_FUNCTION(obj)

            if body:
                body.addObject(obj)
            elif part:
                part.Group += [obj]
        else:
            obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", cls.NAME)
            cls.FREEGRID_FUNCTION(obj)

        doc.commitTransaction()

        return obj


class CreateStorageBox(BaseObjectCommand):
    NAME = "StorageBox"
    FREEGRID_FUNCTION = lambda obj: StorageBoxObject(obj)
    pixmap = "box.svg"
    menuText = translate("Commands", "Storage box")
    toolTip = translate("Commands", "Create a storage box")


class CreateStorageGrid(BaseObjectCommand):
    NAME = "StorageGrid"
    FREEGRID_FUNCTION = lambda obj: StorageGridObject(obj)
    pixmap = "grid.svg"
    menuText = translate("Commands", "Storage grid")
    toolTip = translate("Commands", "Create a storage grid")


class CreateSketch(BaseCommand):
    pixmap = "sketch.svg"
    menuText = translate("Commands", "Sketch")
    toolTip = translate("Commands", "Generate inner box profile")

    def Activated(self):
        try:
            selection = Gui.Selection.getSelection()
            if len(selection) == 1:
                obj = selection[0]
                if isinstance(obj.Proxy, StorageBoxObject):
                    # Use  depth and width values from selected StorageBox
                    box = StorageBox.StorageBox()
                    box.closed_front = not obj.boxOpenFront
                    box.insert_as_sketch(obj.width, obj.depth)
                    FreeCAD.ActiveDocument.recompute()
                else:
                    raise TypeError("Selected object is not a StorageBox.")
            else:
                SketchUI()
        except Exception as e:
            FreeCAD.Console.PrintError(f"Error: {str(e)}\n")


class OpenPreferencePage(BaseCommand):
    pixmap = "preferences_page.svg"
    menuText = translate("Commands", "Preferences page")
    toolTip = translate("Commands", "Open the FreeGrid preferences page")

    def IsActive(self):
        return True

    def Activated(self):
        Gui.showPreferences("FreeGrid")


class About(BaseCommand):
    pixmap = "about.svg"
    menuText = translate("Commands", "About FreeGrid")
    toolTip = translate("Commands", "Show information about FreeGrid")

    def IsActive(self):
        return True

    def Activated(self):
        self.dialog = Gui.PySideUic.loadUi(os.path.join(UIPATH, "about.ui"))
        # TODO: make a good rendered banner
        banner = QtGui.QPixmap(os.path.join(IMGPATH, "banner.png"))
        self.dialog.picture.setPixmap(banner.scaledToHeight(300))
        self.dialog.closeButton.clicked.connect(self.dialog.close)
        self.dialog.exec_()
