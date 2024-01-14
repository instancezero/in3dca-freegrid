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
try:
    import FreeCAD as App
    import FreeCADGui as Gui
except ImportError as e:
    print(f"Failed to import module: {e}\nModule not loaded with FreeCAD")

import os
from freecad.freegrid import ICONPATH

try:
    from FreeCADGui import Workbench
except ImportError as e:
    App.Console.PrintWarning(
        "you are using the FreeGridWorkbench with an old version of FreeCAD (<0.16)")
    App.Console.PrintWarning(
        "the class Workbench is loaded, although not imported: magic")

class FreeGridWorkbench(Gui.Workbench):
    """
    A FreeCAD Workbench that creates parametric storage solutions
    """

    MenuText = "FreeGrid"
    ToolTip = "FreeGrid 3D printed storage system"
    commands = ["CreateStorageBox", "CreateStorageGrid"]
    Icon = os.path.join(ICONPATH, "FreeGrid.svg")

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """

        # Add commmands to toolbar and menu

        from freecad.freegrid import commands

        self.appendToolbar("FreeGrid", self.commands)
        self.appendMenu("FreeGrid", self.commands)

        Gui.addCommand('CreateStorageBox', commands.CreateStorageBox())
        Gui.addCommand('CreateStorageGrid', commands.CreateStorageGrid())

        App.Console.PrintMessage("FreeGrid Workbench initialized\n")

    def Activated(self):
        """
        Code which should be computed when a user switch to this workbench
        """
        # App.Console.PrintMessage("Hola\n")
        pass

    def Deactivated(self):
        """
        Code which should be computed when this workbench is deactivated
        """
        # App.Console.PrintMessage("Adiós\n")
        pass

    def ContextMenu(self, recipient):
        """
        This is executed whenever the user right-clicks on screen
        "recipient" will be either "view" or "tree"
        """
        self.appendContextMenu(
            "FreeGrid", self.commands
        )  # add commands to the context menu

    def GetClassName(self):
        return "Gui::PythonWorkbench"

Gui.addWorkbench(FreeGridWorkbench())
