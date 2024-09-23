# -*- coding: utf-8 -*-
###############################################################################
#
#  Copyright 2018 Mark Ganson <TheMarkster> mwganson at gmail
#
#  InitGui.py
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
###############################################################################
import dynamicdatawb_locator
dynamicdataWBPath = os.path.dirname(dynamicdatawb_locator.__file__)
global dynamicdataWB_icons_path
dynamicdataWB_icons_path = os.path.join(dynamicdataWBPath,'Resources','icons')
global main_dynamicdataWB_Icon
main_dynamicdataWB_Icon = os.path.join(dynamicdataWB_icons_path , 'DynamicDataLogo.svg')
global contextMenuAdded
contextMenuAdded = False

#def myFunc(string):
#    print (string)
#    global act
#    act.setVisible(True)

#mw=Gui.getMainWindow()
#bar=mw.menuBar()
#act=bar.addAction("MyCmd")
#mw.workbenchActivated.connect(myFunc)

####################################################################################
# Initialize the workbench
class DynamicDataWorkbench(Workbench):


    global main_dynamicdataWB_Icon

    MenuText = "DynamicData"
    ToolTip = "DynamicData workbench"
    Icon = main_dynamicdataWB_Icon #already defined in package.xml file

    def __init__(self):
#        self.__class__.Icon = main_dynamicdataWB_Icon
        self.list = None
        pass

    def Initialize(self):
        """This function is executed when FreeCAD starts"""
        import DynamicDataCmd #needed files for FreeCAD commands
        pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")
        self.list = ["DynamicDataCreateObject", "DynamicDataAddProperty",
                    "DynamicDataEditEnumeration", "DynamicDataCreateConfiguration",
                    "DynamicDataRemoveProperty", "DynamicDataImportNamedConstraints",
                    "DynamicDataImportAliases","DynamicDataCopyProperty",
                    "DynamicDataRenameProperty","DynamicDataSetTooltip",
                    "DynamicDataMoveToNewGroup","DynamicDataSettings",
                    "DynamicDataCommands"] # A list of command names created in the line above
        if pg.GetBool("CondensedToolbar", True):
            self.appendToolbar("DynamicData Commands",  [self.list[-1]]) # leave DDCommands off toolbar
        else:
            self.appendToolbar("DynamicData Commands", self.list[:-5])
        self.appendMenu("&DynamicData", self.list) # creates a new menu
        #considered putting the menu inside the Edit menu, but decided against it
        #self.appendMenu(["&Edit","DynamicData"],self.list) # appends a submenu to an existing menu

        if pg.GetBool("AddToFreeCADPreferences",True):
            Gui.addPreferencePage(DynamicDataCmd.uiPath + "/dynamicdataprefs.ui", "DynamicData")
            Gui.addIcon("preferences-dynamicdata",dynamicdataWB_icons_path + "/DynamicDataPreferencesLogo.svg")

    def myCallbackFunction(self,result):
        if result == "True":
            FreeCAD.Console.PrintWarning("A new version of DynamicData is available for update in the Addon Manager.\n")
        else:
            #FreeCAD.Console.PrintMessage("DD up to date\n")
            pass #up to date

    def Activated(self):
        """This function is executed when the workbench is activated."""
        #global act
        #act.setVisible(True)
        import AddonManager
        if hasattr(AddonManager, "check_updates"):
            AddonManager.check_updates("DynamicData",self.myCallbackFunction)
        return

    def Deactivated(self):
        """This function is executed when the workbench is deactivated."""
        #FreeCAD will hide our menu and toolbar upon exiting the wb, so we setup a singleshot
        #to unhide them once FreeCAD is finished, 2 seconds later
        from PySide import QtCore
        QtCore.QTimer.singleShot(2000, self.showMenu)
        return

    def showMenu(self):
        global contextMenuAdded
        from PySide import QtGui
        window = QtGui.QApplication.activeWindow()
        #freecad hides wb toolbars on leaving wb, we unhide ours here to keep it around
        #if the user has it set in parameters to do so
        pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")
        keep = pg.GetBool('KeepToolbar',True)
        if not keep:
            return
        tb = window.findChildren(QtGui.QToolBar) if window else []
        for bar in tb:
            if "DynamicData Commands" in bar.objectName():
                bar.setVisible(True)
        #following would reactivate menu after leaving workbench, but the menu moves, so don't reactivate for now
        #we'll still have the toolbar anyway and we don't want to clutter up the menu outside the workbench
        #menu = window.menuWidget()
        #actions = menu.actions
        #a = actions()
        #for ii in range(0,len(a)):
        #    #FreeCAD.Console.PrintMessage(str(ii)+' '+str(a[ii].text())+'\n')
        #    if a[ii].text() == 'DynamicData':
        #        a[ii].setVisible(True)
        #        subMenu = a[ii].menu()
        #        subMenu.setVisible(True)
        #        subActions = a[ii].menu().actions()
        #        for jj in range(0,len(subActions)):
        #            # FreeCAD.Console.PrintMessage('    '+str(jj)+' '+str(subActions[jj].text())+'\n')
        #            FreeCAD.Console.PrintMessage(str(subActions[jj].isVisible())+'\n')
        #            subActions[jj].setVisible(True)
        #        break

        # following keeps the context menu active, too.


        class DDContextMenuEditor:
            DEBUG = False

            def modifyContextMenu(self, recipient):
                if recipient == "View":
                    if Gui.activeWorkbench().name() != "DynamicDataWorkbench":
                        return [{"append":"DynamicDataCommands", "menuItem":"Std_Delete"}]
                elif recipient == "Tree":
                    if Gui.activeWorkbench().name() != "DynamicDataWorkbench":
                        return [{"append":"DynamicDataCommands", "menuItem":"Std_Delete"}]
                elif DDContextMenuEditor.DEBUG == True:
                    FreeCAD.Console.PrintMessage(f"Recipient = {recipient}")

        manip = DDContextMenuEditor()
        if hasattr(Gui,"addWorkbenchManipulator") and not contextMenuAdded:
            Gui.addWorkbenchManipulator(manip)
            contextMenuAdded = True

    def ContextMenu(self, recipient):
        """This is executed whenever the user right-clicks on screen"""
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu("DynamicData", self.list) # add commands to the context menu

    def GetClassName(self):
        """This function is mandatory if this is a full python workbench"""
        return "Gui::PythonWorkbench"


wb = DynamicDataWorkbench()
Gui.addWorkbench(wb)
