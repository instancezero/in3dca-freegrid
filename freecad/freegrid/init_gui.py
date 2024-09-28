# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# * This program is free software: you can redistribute it and/or modify    *
# * it under the terms of the GNU General Public License as published by    *
# * the Free Software Foundation, either version 3 of the License, or       *
# * (at your option) any later version.                                     *
# *                                                                         *
# * This program is distributed in the hope that it will be useful,         *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of          *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           *
# * GNU General Public License for more details.                            *
# *                                                                         *
# * You should have received a copy of the GNU General Public License       *
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.   *
# *                                                                         *
# ***************************************************************************
# TODO: create a Wiki page

try:
    import FreeCAD
    import FreeCADGui
except ImportError as e:
    print(f"Failed to import module: {e}\nModule not loaded with FreeCAD")

import os

from freecad.freegrid import ICONPATH, TRANSLATIONSPATH, UIPATH, __version__

translate = FreeCAD.Qt.translate

# Add translations path
FreeCADGui.addLanguagePath(TRANSLATIONSPATH)
FreeCADGui.updateLocale()

try:
    from FreeCADGui import Workbench
except ImportError as e:
    FreeCAD.Console.PrintWarning(
        translate(
            "Log",
            "You are using the FreeGrid Workbench with an old version of FreeCAD (<0.16)",
        )
    )
    FreeCAD.Console.PrintWarning(
        translate(
            "Log",
            "The class Workbench is loaded, although not imported: magic",
        )
    )


class FreeGridWorkbench(Workbench):
    """
    A FreeCAD Workbench that creates parametric storage solutions.
    """

    MenuText = "FreeGrid"
    ToolTip = translate("Workbench", "Parametric 3D printed storage system")
    Icon = os.path.join(ICONPATH, "FreeGrid.svg")

    commands = [
        "FreeGrid_StorageBox",
        "FreeGrid_BitCartridgeHolder",
        "FreeGrid_StorageGrid",
        "FreeGrid_Sketch",
        "Separator",
        "FreeGrid_PreferencesPage",
        "FreeGrid_About",
    ]

    def Initialize(self):
        """
        This function is called at the first activation of the workbench,
        here is the place to import all the commands.
        """

        # Add commands to toolbar and menu

        from freecad.freegrid import commands

        self.appendToolbar("FreeGrid", self.commands)
        self.appendMenu("FreeGrid", self.commands)

        FreeCADGui.addCommand("FreeGrid_StorageBox", commands.CreateStorageBox())
        FreeCADGui.addCommand("FreeGrid_BitCartridgeHolder", commands.CreateBitCartridgeHolder())
        FreeCADGui.addCommand("FreeGrid_StorageGrid", commands.CreateStorageGrid())
        FreeCADGui.addCommand("FreeGrid_Sketch", commands.CreateSketch())
        FreeCADGui.addCommand("FreeGrid_PreferencesPage", commands.OpenPreferencePage())
        FreeCADGui.addCommand("FreeGrid_About", commands.About())

        FreeCADGui.addIconPath(ICONPATH)
        FreeCADGui.addPreferencePage(os.path.join(UIPATH, "preferences.ui"), "FreeGrid")

        FreeCAD.Console.PrintMessage(
            translate("Log", "FreeGrid Workbench initialized v{}").format(__version__) + "\n"
        )

    def Activated(self):
        """
        Code which should be computed when a user switch to this workbench.
        """
        # FreeCAD.Console.PrintMessage("Hola\n")
        pass

    def Deactivated(self):
        """
        Code which should be computed when this workbench is deactivated.
        """
        # FreeCAD.Console.PrintMessage("Adiós\n")
        pass

    def ContextMenu(self, recipient):
        """
        This is executed whenever the user right-clicks on screen
        "recipient" will be either "view" or "tree".
        """
        self.appendContextMenu("FreeGrid", self.commands)  # add commands to the context menu

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(FreeGridWorkbench())
