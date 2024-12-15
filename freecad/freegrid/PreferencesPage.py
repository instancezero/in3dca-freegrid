import os
import FreeCAD
import FreeCADGui

from freecad.freegrid import UIPATH

paramFreeGrid = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/FreeGrid")


class FreeGridPreferencesPage:
    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(UIPATH, "preferences.ui"))

        self.form.tooltipPicture.clicked.connect(self.tooltipPictureCheckboxClicked)
        self.form.BoxGrip.clicked.connect(self.boxGripCheckboxClicked)

        self.tooltipPictureCheckboxClicked()
        self.boxGripCheckboxClicked()

    def tooltipPictureCheckboxClicked(self):
        self.form.iconTooltipSize.setEnabled(self.form.tooltipPicture.isChecked())

    def boxGripCheckboxClicked(self):
        self.form.BoxGripDepth.setEnabled(self.form.BoxGrip.isChecked())

    def loadSettings(self):
        """Mandatory method to load the saved settings on parameters to the GUI"""
        # General
        self.form.RandomColor = FreeCAD.ParamGet(paramFreeGrid).GetBool("RandomColor")
        self.form.tooltipPicture = FreeCAD.ParamGet(paramFreeGrid).GetBool("tooltipPicture")
        self.form.iconTooltipSize = FreeCAD.ParamGet(paramFreeGrid).GetInt("iconTooltipSize")
        # Box
        self.form.BoxDepth = FreeCAD.ParamGet(paramFreeGrid).GetInt("BoxDepth")
        self.form.BoxWidth = FreeCAD.ParamGet(paramFreeGrid).GetInt("BoxWidth")
        self.form.BoxHeight = FreeCAD.ParamGet(paramFreeGrid).GetString("BoxHeight")
        self.form.DivisionsX = FreeCAD.ParamGet(paramFreeGrid).GetInt("DivisionsX")
        self.form.DivisionsY = FreeCAD.ParamGet(paramFreeGrid).GetInt("DivisionsY")
        self.form.DivisionHeight = FreeCAD.ParamGet(paramFreeGrid).GetInt("DivisionHeight")
        self.form.BoxOpenFront = FreeCAD.ParamGet(paramFreeGrid).GetBool("BoxOpenFront")
        self.form.BoxRamp = FreeCAD.ParamGet(paramFreeGrid).GetBool("BoxRamp")
        self.form.FloorSupport = FreeCAD.ParamGet(paramFreeGrid).GetBool("FloorSupport")
        self.form.BoxGrip = FreeCAD.ParamGet(paramFreeGrid).GetBool("BoxGrip")
        self.form.BoxGripDepth = FreeCAD.ParamGet(paramFreeGrid).GetString("BoxGripDepth")
        self.form.MagnetOption = FreeCAD.ParamGet(paramFreeGrid).GetString("MagnetOption")
        # Grid
        self.form.GripDepth = FreeCAD.ParamGet(paramFreeGrid).GetInt("GripDepth")
        self.form.GripWidth = FreeCAD.ParamGet(paramFreeGrid).GetInt("GripWidth")
        self.form.CornerConnectors = FreeCAD.ParamGet(paramFreeGrid).GetBool("CornerConnectors")
        self.form.IncludeMagnets = FreeCAD.ParamGet(paramFreeGrid).GetBool("IncludeMagnets")
        # Magnet
        self.form.MagnetDiameter = FreeCAD.ParamGet(paramFreeGrid).GetString("MagnetDiameter")
        self.form.MagnetHeight = FreeCAD.ParamGet(paramFreeGrid).GetString("MagnetHeight")

    def saveSettings(self):
        """Mandatory method to save the settings on parameters"""
        # General
        FreeCAD.ParamGet(paramFreeGrid).SetBool("RandomColor", self.form.RandomColor)
        FreeCAD.ParamGet(paramFreeGrid).SetBool("tooltipPicture", self.form.tooltipPicture)
        FreeCAD.ParamGet(paramFreeGrid).SetInt("iconTooltipSize", self.form.iconTooltipSize)
        # Box
        FreeCAD.ParamGet(paramFreeGrid).SetInt("BoxDepth", self.form.BoxDepth)
        FreeCAD.ParamGet(paramFreeGrid).SetInt("BoxWidth", self.form.BoxWidth)
        FreeCAD.ParamGet(paramFreeGrid).SetString("BoxHeight", self.form.BoxHeight)
        FreeCAD.ParamGet(paramFreeGrid).SetInt("DivisionsX", self.form.DivisionsX)
        FreeCAD.ParamGet(paramFreeGrid).SetInt("DivisionsY", self.form.DivisionsY)
        FreeCAD.ParamGet(paramFreeGrid).SetInt("DivisionHeight", self.form.DivisionHeight)
        FreeCAD.ParamGet(paramFreeGrid).SetBool("BoxOpenFront", self.form.BoxOpenFront)
        FreeCAD.ParamGet(paramFreeGrid).SetBool("BoxRamp", self.form.BoxRamp)
        FreeCAD.ParamGet(paramFreeGrid).SetBool("FloorSupport", self.form.FloorSupport)
        FreeCAD.ParamGet(paramFreeGrid).SetBool("BoxGrip", self.form.BoxGrip)
        FreeCAD.ParamGet(paramFreeGrid).SetString("BoxGripDepth", self.form.BoxGripDepth)
        FreeCAD.ParamGet(paramFreeGrid).SetString("MagnetOption", self.form.MagnetOption)
        # Grid
        FreeCAD.ParamGet(paramFreeGrid).SetInt("GripDepth", self.form.GripDepth)
        FreeCAD.ParamGet(paramFreeGrid).SetInt("GripWidth", self.form.GripWidth)
        FreeCAD.ParamGet(paramFreeGrid).SetBool("CornerConnectors", self.form.CornerConnectors)
        FreeCAD.ParamGet(paramFreeGrid).SetBool("IncludeMagnets", self.form.IncludeMagnets)
        # Magnet
        FreeCAD.ParamGet(paramFreeGrid).SetString("MagnetDiameter", self.form.MagnetDiameter)
        FreeCAD.ParamGet(paramFreeGrid).SetString("MagnetHeight", self.form.MagnetHeight)
