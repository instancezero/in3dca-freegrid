import os
import FreeCAD
import FreeCADGui

from freecad.freegrid import UIPATH

paramFreeGrid = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/FreeGrid")
pq = FreeCAD.Units.parseQuantity


class FreeGridPreferencesPage:
    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(UIPATH, "preferences.ui"))

        self.form.TooltipPicture.clicked.connect(self.tooltipPictureCheckboxClicked)
        self.form.BoxGrip.clicked.connect(self.boxGripCheckboxClicked)

        self.tooltipPictureCheckboxClicked()
        self.boxGripCheckboxClicked()

    def tooltipPictureCheckboxClicked(self):
        self.form.IconTooltipSize.setEnabled(self.form.TooltipPicture.isChecked())

    def boxGripCheckboxClicked(self):
        self.form.BoxGripDepth.setEnabled(self.form.BoxGrip.isChecked())

    def loadSettings(self):
        """Mandatory method to load the saved settings on parameters to the GUI"""
        # General
        self.form.RandomColor.setChecked(paramFreeGrid.GetBool("RandomColor"))
        self.form.TooltipPicture.setChecked(paramFreeGrid.GetBool("TooltipPicture"))
        self.form.IconTooltipSize.setValue(paramFreeGrid.GetInt("IconTooltipSize"))
        # Box
        self.form.BoxDepth.setValue(paramFreeGrid.GetInt("BoxDepth"))
        self.form.BoxWidth.setValue(paramFreeGrid.GetInt("BoxWidth"))
        # self.form.BoxHeight.setValue(pq(paramFreeGrid.GetString("BoxHeight")).getValueAs("mm"))
        self.form.BoxHeight.setValue(paramFreeGrid.GetString("BoxHeight"))
        self.form.DivisionsX.setValue(paramFreeGrid.GetInt("DivisionsX"))
        self.form.DivisionsY.setValue(paramFreeGrid.GetInt("DivisionsY"))
        self.form.DivisionHeight.setValue(paramFreeGrid.GetInt("DivisionHeight"))
        self.form.BoxOpenFront.setChecked(paramFreeGrid.GetBool("BoxOpenFront"))
        self.form.BoxRamp.setChecked(paramFreeGrid.GetBool("BoxRamp"))
        self.form.FloorSupport.setChecked(paramFreeGrid.GetBool("FloorSupport"))
        self.form.BoxGrip.setChecked(paramFreeGrid.GetBool("BoxGrip"))
        self.form.BoxGripDepth.setValue(
            pq(paramFreeGrid.GetString("BoxGripDepth")).getValueAs("mm")
        )
        self.form.MagnetOption.setCurrentIndex(paramFreeGrid.GetInt("MagnetOption"))
        # Grid
        self.form.GridDepth.setValue(paramFreeGrid.GetInt("GridDepth"))
        self.form.GridWidth.setValue(paramFreeGrid.GetInt("GridWidth"))
        self.form.CornerConnectors.setChecked(paramFreeGrid.GetBool("CornerConnectors"))
        self.form.IncludeMagnets.setChecked(paramFreeGrid.GetBool("IncludeMagnets"))
        # Magnet
        self.form.MagnetDiameter.setValue(
            pq(paramFreeGrid.GetString("MagnetDiameter")).getValueAs("mm")
        )
        self.form.MagnetHeight.setValue(
            pq(paramFreeGrid.GetString("MagnetHeight")).getValueAs("mm")
        )

    def saveSettings(self):
        """Mandatory method to save the settings on parameters"""
        # General
        paramFreeGrid.SetBool("RandomColor", self.form.RandomColor.isChecked())
        paramFreeGrid.SetBool("tooltipPicture", self.form.TooltipPicture.isChecked())
        paramFreeGrid.SetInt("iconTooltipSize", self.form.IconTooltipSize.value())
        # Box
        paramFreeGrid.SetInt("BoxDepth", self.form.BoxDepth.value())
        paramFreeGrid.SetInt("BoxWidth", self.form.BoxWidth.value())
        paramFreeGrid.SetString("BoxHeight", self.form.BoxHeight.text())
        paramFreeGrid.SetInt("DivisionsX", self.form.DivisionsX.value())
        paramFreeGrid.SetInt("DivisionsY", self.form.DivisionsY.value())
        paramFreeGrid.SetInt("DivisionHeight", self.form.DivisionHeight.value())
        paramFreeGrid.SetBool("BoxOpenFront", self.form.BoxOpenFront.isChecked())
        paramFreeGrid.SetBool("BoxRamp", self.form.BoxRamp.isChecked())
        paramFreeGrid.SetBool("FloorSupport", self.form.FloorSupport.isChecked())
        paramFreeGrid.SetBool("BoxGrip", self.form.BoxGrip.isChecked())
        paramFreeGrid.SetString("BoxGripDepth", self.form.BoxGripDepth.text())
        paramFreeGrid.SetInt("MagnetOption", self.form.MagnetOption.currentIndex())
        # Grid
        paramFreeGrid.SetInt("GridDepth", self.form.GridDepth.value())
        paramFreeGrid.SetInt("GridWidth", self.form.GridWidth.value())
        paramFreeGrid.SetBool("CornerConnectors", self.form.CornerConnectors.isChecked())
        paramFreeGrid.SetBool("IncludeMagnets", self.form.IncludeMagnets.isChecked())
        # Magnet
        paramFreeGrid.SetString("MagnetDiameter", self.form.MagnetDiameter.text())
        paramFreeGrid.SetString("MagnetHeight", self.form.MagnetHeight.text())
