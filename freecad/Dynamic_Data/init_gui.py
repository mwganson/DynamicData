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

import os
import FreeCAD
import FreeCADGui as Gui

import freecad.Dynamic_Data.dynamicdatawb_locator as dynamicdatawb_locator
dynamicdataWBPath = os.path.dirname(dynamicdatawb_locator.__file__)
global dynamicdataWB_icons_path
dynamicdataWB_icons_path = os.path.join(dynamicdataWBPath,'Resources','icons')
global main_dynamicdataWB_Icon
main_dynamicdataWB_Icon = os.path.join(dynamicdataWB_icons_path , 'DynamicDataLogo.svg')
global contextMenuAdded
contextMenuAdded = False
global pg
pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")

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
class DynamicDataWorkbench(Gui.Workbench):

    global main_dynamicdataWB_Icon
    global hasRequests

    MenuText = "DynamicData"
    ToolTip = "DynamicData workbench"
    Icon = main_dynamicdataWB_Icon #already defined in package.xml file

    def __init__(self):
#        self.__class__.Icon = main_dynamicdataWB_Icon
        self.list = None
        pass

    def Initialize(self):
        """This function is executed when FreeCAD starts"""
        import freecad.Dynamic_Data.DynamicDataCmd as DynamicDataCmd #needed files for FreeCAD commands
        self.list = ["DynamicDataCreateObject", "DynamicDataAddProperty",
                    "DynamicDataEditEnumeration", "DynamicDataCreateConfiguration",
                    "DynamicDataRemoveProperty", "DynamicDataImportNamedConstraints",
                    "DynamicDataImportAliases","DynamicDataCopyProperty",
                    "DynamicDataRenameProperty","DynamicDataRetypeProperty",
                    "DynamicDataSetTooltip",
                    "DynamicDataMoveToNewGroup","DynamicDataSettings",
                    "DynamicDataCommands"] # A list of command names created in the line above
        if pg.GetBool("CondensedToolbar", True):
            self.appendToolbar("DynamicData Commands",  [self.list[-1]]) # leave DDCommands off toolbar
        else:
            self.appendToolbar("DynamicData Commands", self.list[:-6])
        self.appendMenu("&DynamicData", self.list) # creates a new menu
        #considered putting the menu inside the Edit menu, but decided against it
        #self.appendMenu(["&Edit","DynamicData"],self.list) # appends a submenu to an existing menu

        if pg.GetBool("AddToFreeCADPreferences",True):
            Gui.addPreferencePage(DynamicDataCmd.uiPath + "/dynamicdataprefs.ui", "DynamicData")
            Gui.addIcon("preferences-dynamicdata",dynamicdataWB_icons_path + "/DynamicDataPreferencesLogo.svg")

    def Activated(self):
        """This function is executed when the workbench is activated."""
        try:
            import requests
            global hasRequests
            hasRequests = True
            hasRequests = False #testing
        except:
            hasRequests = False
        import xml.etree.ElementTree as ET

        def get_remote_version(user, repo, branch='master'):
            # GitHub raw URL for package.xml
            global hasRequests
            if not hasRequests:
                # check again if requests module is now available
                try:
                    import requests
                    hasRequests = True
                except:
                    FreeCAD.Console.PrintWarning("DynamicData updater: The requests package was not found, cannot check for updates.  Install requests package or disable auotomatic update checking in DynamicData settings to prevent this warning message.\n")
                    return None
            url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/package.xml"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    # Parse the XML content of package.xml
                    xml_content = response.content
                    tree = ET.ElementTree(ET.fromstring(xml_content))
                    root = tree.getroot()
                    # Find the version element and return its text
                    version = root.find("version").text
                    return version
                else:
                    print(f"Failed to fetch package.xml: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Error fetching or parsing package.xml: {e}")
                return None

        def check_for_update(current_version, user, repo, branch, callback):
            latest_version = get_remote_version(user, repo, branch)
            if latest_version and latest_version > current_version:
                callback(latest_version)

        def update_callback(latest_version):
            FreeCAD.Console.PrintWarning(f"DynamicData {latest_version} is now available in the Addon Manager.\n")

        import freecad.Dynamic_Data.DynamicDataCmd as DynamicDataCmd
        current_version = DynamicDataCmd.__version__
        user = "mwganson"
        repo = "DynamicData"
        branch = "master"

        checkUpdates = pg.GetBool("CheckForUpdates", True)

        if checkUpdates:
            check_for_update(current_version, user, repo, branch, update_callback)

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
