# -*- coding: utf-8 -*-
###################################################################################
#
#  DynamicDataCmd.py
#
#  Copyright 2018-2023 Mark Ganson <TheMarkster> mwganson at gmail
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
###################################################################################

__title__   = "DynamicData"
__author__  = "Mark Ganson <TheMarkster>"
__url__     = "https://github.com/mwganson/DynamicData"
__date__    = "2023.12.13"
__version__ = "2.57"
version = float(__version__)
mostRecentTypes=[]
mostRecentTypesLength = 5 #will be updated from parameters


from FreeCAD import Gui
from PySide import QtCore, QtGui

import FreeCAD, FreeCADGui, os, math, re
App = FreeCAD
Gui = FreeCADGui
__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )
uiPath = os.path.join( __dir__, 'Resources', 'ui' )

keepToolbar = True
windowFlags = QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint

class DynamicDataBaseCommandClass:
    """Base class for all commands to provide some common code"""
    #select objects dialog class
    class SelectObjects(QtGui.QDialog):
        def __init__(self, objects, label=""):
            QtGui.QDialog.__init__(self)
            scrollContents = QtGui.QWidget()
            scrollingLayout = QtGui.QVBoxLayout(self)
            scrollContents.setLayout(scrollingLayout)
            scrollArea = QtGui.QScrollArea()
            scrollArea.setVerticalScrollBarPolicy(QtGui.Qt.ScrollBarAlwaysOn)
            scrollArea.setHorizontalScrollBarPolicy(QtGui.Qt.ScrollBarAlwaysOff)
            scrollArea.setWidgetResizable(True)
            scrollArea.setWidget(scrollContents)
            self.signalsBlocked = False

            vBoxLayout = QtGui.QVBoxLayout(self)
            vBoxLayout.addWidget(QtGui.QLabel(label))
            self.all = QtGui.QCheckBox("All")
            self.all.stateChanged.connect(self.allStateChanged)
            vBoxLayout.addWidget(self.all)
            vBoxLayout.addWidget(scrollArea)
            self.setLayout(vBoxLayout)
            buttons = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Ok.__or__(QtGui.QDialogButtonBox.Cancel),
                QtCore.Qt.Horizontal, self)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            self.checkBoxes = []
            self.selected = []
            for ii,object in enumerate(objects):
                self.checkBoxes.append(QtGui.QCheckBox(object))
                self.checkBoxes[-1].setCheckState(self.all.checkState())
                self.checkBoxes[-1].stateChanged.connect(self.checkStateChanged)
                scrollingLayout.addWidget(self.checkBoxes[-1])
            vBoxLayout.addWidget(buttons)

        def checkStateChanged(self, arg):
            if not arg:
                self.signalsBlocked = True
                self.all.setCheckState(QtCore.Qt.Unchecked)
                self.signalsBlocked = False

        def allStateChanged(self, arg):
            if self.signalsBlocked:
                return
            self.checkAll(self.all.checkState())

        def checkAll(self, state):
            for cb in self.checkBoxes:
                cb.setCheckState(state)

        def accept(self):
            self.selected = []
            for cb in self.checkBoxes:
                if cb.checkState():
                    self.selected.append(cb.text())
            super().accept()

        ### end of SelectObjects class definition

    def getSelectedObjects(self, objs, label="", checkAll=True):
        """opens a dialog with objs (strings) in a checkboxed list, returns list of selected"""
        if objs:
            dlg = DynamicDataBaseCommandClass.SelectObjects(objs,label)
            if checkAll:
                dlg.all.setCheckState(QtCore.Qt.Checked)
            else:
                dlg.all.setCheckState(QtCore.Qt.Unchecked)
            ok = dlg.exec_()
            if not ok:
                return []
            return dlg.selected
        return []

    @property
    def PropertyTypes(self):
         return [
            "Acceleration",
            "Angle",
            "Area",
            "Bool",
            "Color",
            "Direction",
            "Distance",
            "Enumeration",
            "File",
            "FileIncluded",
            "Float",
            "FloatConstraint",
            "FloatList",
            "Font",
            "Force",
            "Integer",
            "IntegerConstraint",
            "IntegerList",
            "Length",
            "Link",
            "LinkChild",
            "LinkGlobal",
            "LinkList",
            "LinkListChild",
            "LinkListGlobal",
            "LinkSubList",
            "Material",
            "MaterialList",
            "Matrix",
            "Path",
            "Percent",
            "Placement",
            "PlacementLink",
            "Position",
            "Precision",
            "Pressure",
            "Quantity",
            "QuantityConstraint",
            "Rotation",
            "Speed",
            "String",
            "StringList",
            "Vector",
            "VectorList",
            "VectorDistance",
            "Volume"]

    @property
    def NonLinkableTypes(self):
        return [ #cannot be linked with setExpresion()
            "Bool",
            "Color",
            "Enumeration",
            "File",
            "FileIncluded",
            "FloatList",
            "Font",
            "IntegerList",
            "Link",
            "LinkChild",
            "LinkGlobal",
            "LinkList",
            "LinkListChild",
            "LinkListGlobal",
            "LinkSubList",
            "Material",
            "MaterialList",
            "Matrix",
            "Path",
            "PlacementLink",
            "String",
            "StringList",
            "VectorList"]

    @property
    def VectorTypes(self):
        return [#x,y,z elements must be linked separately
            "Direction",
            "Position",
            "Vector",
            "VectorDistance"]

    def getAllProperties(self, obj, includeViewProps = False, blacklist=[]):
        """get all the properties that we might want to copy or set"""
        props = [prop for prop in obj.PropertiesList if not prop in blacklist]
        if includeViewProps:
            viewProps = [f"(view) {prop}" for prop in obj.ViewObject.PropertiesList if not prop in blacklist]
        else:
            viewProps = []
        return props + viewProps

    def getDynamicProperties(self, obj):
        """get the list of the dynamic properties of obj"""
        props = [p for p in obj.PropertiesList if self.isDynamic(obj,p)]
        return props

    def getGroup(self, obj, prop):
        """return the name of the group this property is in"""
        if not obj:
            return None
        if not prop in obj.PropertiesList:
            return None
        return obj.getGroupOfProperty(prop)

    def getGroups(self,obj,skipList=[]):
        """get the groups of obj, skipping those in skipList"""
        props = [p for p in obj.PropertiesList if obj.getPropertyStatus(p) == [21]]
        groups = []
        for prop in props:
            group = obj.getGroupOfProperty(prop)
            if group and not group in groups and not group in skipList:
                groups.append(group)
        return groups

    def isDynamic(self,obj,prop):
        """checks whether prop is a dynamic property and not a built-in property
        of obj"""
        if prop == "DynamicData":
            return False
        isSo = False
        try:
            oldGroup = obj.getGroupOfProperty(prop)
            obj.setGroupOfProperty(prop,"test")
            obj.setGroupOfProperty(prop,oldGroup)
            isSo = True
        except:
            isSo = False
        return isSo

    def isDDObject(self, obj):
        """checks if this is a DynamicData object"""
        return hasattr(obj, "DynamicData")

    def isValidName(self, name):
        return name == self.fixName(name)

    def fixName(self, name):
        """fixes a name so it can be a valid property name"""
        pattern = re.compile(r'^\d') #can't begin with a number
        pattern2 = re.compile(r'[^0-9a-zA-Z]') #no non-alphanumerics
        REPLACEMENTS = {
            " ": "_",
            ".": "_",
            "ä": "ae",
            "ö": "oe",
            "ü": "ue",
            "Ä": "Ae",
            "Ö": "Oe",
            "Ü": "Ue",
            "ß": "ss",
            "'": ""
        }
        new_name = name
        for k,v in REPLACEMENTS.items():
            new_name = new_name.replace(k, v)
        if pattern.match(new_name):
            new_name = f"_{new_name}"
        new_name = re.sub(pattern2, '_', new_name) #replace with _'s
        return new_name


#######################################################################################
# Keep Toolbar active even after leaving workbench

class DynamicDataSettingsCommandClass(DynamicDataBaseCommandClass):
    """Settings, currently only whether to keep toolbar after leaving workbench"""
    global mostRecentTypes

    class DynamicDataSettingsDlg(QtGui.QDialog):

        pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")

        def __init__(self):
            super(DynamicDataSettingsCommandClass.DynamicDataSettingsDlg, self).__init__(Gui.getMainWindow())
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            self.setAttribute(QtCore.Qt.WA_WindowPropagation, True)
            self.form = Gui.PySideUic.loadUi(uiPath + "/dynamicdataprefs.ui")
            self.setWindowTitle(self.form.windowTitle()+" v."+__version__)
            self.setWindowIcon(QtGui.QIcon("Resources/icons/Settings.svg"))
            lay = QtGui.QVBoxLayout(self)
            lay.addWidget(self.form)
            self.setLayout(lay)
            self.form.KeepToolbar.setChecked(self.pg.GetBool('KeepToolbar', True))
            self.form.SupportViewObjectProperties.setChecked(self.pg.GetBool('SupportViewObjectProperties', False))
            self.form.AddToActiveContainer.setChecked(self.pg.GetBool('AddToActiveContainer', False))
            self.form.AddToFreeCADPreferences.setChecked(self.pg.GetBool("AddToFreeCADPreferences",True))
            self.form.mruLength.setValue(self.pg.GetInt('mruLength', 5))

        def closeEvent(self, event):
            self.pg.SetBool('KeepToolbar', self.form.KeepToolbar.isChecked())
            self.pg.SetBool('SupportViewObjectProperties', self.form.SupportViewObjectProperties.isChecked())
            self.pg.SetBool('AddToActiveContainer', self.form.AddToActiveContainer.isChecked())
            self.pg.SetBool('AddToFreeCADPreferences',self.form.AddToFreeCADPreferences.isChecked())
            self.pg.SetInt('mruLength', self.form.mruLength.value())
            super(DynamicDataSettingsCommandClass.DynamicDataSettingsDlg, self).closeEvent(event)

    def __init__(self):
        pass

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'Settings.svg'), # the name of an icon file available in the resources
                'MenuText': "&Settings",
                'Accel'   : "Ctrl+Shift+D,S",
                'ToolTip' : "Workbench settings dialog"}

    def Activated(self):
        dlg = self.DynamicDataSettingsDlg()
        dlg.open()

    def IsActive(self):
        return True


#Gui.addCommand("DynamicDataKeepToolbar", DynamicDataKeepToolbarCommandClass())


####################################################################################
# Create the dynamic data container object

class DynamicDataCreateObjectCommandClass(DynamicDataBaseCommandClass):
    """Create Object command"""

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'CreateObject.svg'),
                'MenuText': "&Create Object",
                'Accel'   : "Ctrl+Shift+D,C",
                'ToolTip' : "Create the DynamicData object to contain the custom properties"}

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        doc.openTransaction("CreateObject")
        a = doc.addObject("App::FeaturePython","dd")
        a.addProperty("App::PropertyStringList","DynamicData").DynamicData=self.getHelp()
        setattr(a.ViewObject,'DisplayMode',['0']) #avoid enumeration -1 warning
        doc.commitTransaction()
        Gui.Selection.clearSelection()
        pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")
        if pg.GetBool('AddToActiveContainer',False):
            body = Gui.ActiveDocument.ActiveView.getActiveObject("pdbody")
            part = Gui.ActiveDocument.ActiveView.getActiveObject("part")
            if body:
                body.Group += [a]
            elif part:
                part.Group += [a]
        Gui.Selection.addSelection(a) #select so the user can immediately add a new property
        doc.recompute()
        return

    def IsActive(self):
        if not FreeCAD.ActiveDocument:
            return False
        return True

    def getHelp(self):
        return ["Created with DynamicData (v"+__version__+") workbench.",
                "This is a simple container object built",
                "for holding custom properties."
]

#Gui.addCommand("DynamicDataCreateObject", DynamicDataCreateObjectCommandClass())

####################################################################################
# Create or edit an existing configuration

class DynamicDataCreateConfigurationCommandClass(DynamicDataBaseCommandClass):
    """Create or edit a configuration command"""
    class DynamicDataConfigurationDlg(QtGui.QDialog):
        def __init__(self,dd):
            super(DynamicDataCreateConfigurationCommandClass.DynamicDataConfigurationDlg, self).__init__(Gui.getMainWindow())
            self.setAttribute(QtCore.Qt.WA_WindowPropagation, True)
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            self.setWindowTitle(f"DynamicData v{__version__} Configuration Editor")
            self.setWindowIcon(QtGui.QIcon("Resources/icons/DynamicDataCreateConfiguration.svg"))
            self.dd = dd
            self.configuration = {}
            self.curLineEdit = None #used only in event filter and handleCtrlTab()
            hasConfig = self.getConfigurationFromObject()
            lay = QtGui.QVBoxLayout(self)
            self.setLayout(lay)
            self.nameRow = QtGui.QHBoxLayout()
            lay.addLayout(self.nameRow)
            self.configurationNameLabel = QtGui.QLabel("Configuration name:")
            self.nameRow.addWidget(self.configurationNameLabel)
            self.configurationName = QtGui.QLineEdit()
            self.configurationName.setToolTip(\
"Configuration name will be the name given to \n\
the Enumeration property created and to the Group \n\
all the properties go into.")
            self.configurationName.setText(self.configuration["name"])
            self.configurationName.selectAll()
            self.configurationName.textChanged.connect(self.updateDict)
            self.nameRow.addWidget(self.configurationName)
            self.enumCountLabel = QtGui.QLabel("Enum count:")
            self.enumCount = QtGui.QSpinBox()
            self.enumCount.setMinimum(2)
            self.enumCount.setMaximum(100)
            self.enumCount.setSingleStep(1)
            self.enumCount.setValue(self.configuration["enumCount"])
            self.enumCount.valueChanged.connect(self.updateDict)
            self.enumCount.setToolTip( \
"This is the number of configuration options you \n\
will have, for example: small, medium, large would \n\
be 3.")
            self.nameRow.addWidget(self.enumCountLabel)
            self.nameRow.addWidget(self.enumCount)
            self.variableCountLabel = QtGui.QLabel("Variable count:")
            self.nameRow.addWidget(self.variableCountLabel)
            self.variableCount = QtGui.QSpinBox()
            self.variableCount.setMinimum(2)
            self.variableCount.setMaximum(100)
            self.variableCount.setSingleStep(1)
            self.variableCount.setValue(self.configuration["variableCount"])
            self.variableCount.valueChanged.connect(self.updateDict)
            self.variableCount.setToolTip( \
"This is the number of variables you will have \n\
in the configuration.  For example, if you want \n\
Height, Width, and Length, enter 3 here.")
            self.nameRow.addWidget(self.variableCount)

            self.grid_scroller = QtGui.QScrollArea()
            self.gridLayout = QtGui.QGridLayout()
            lay.addWidget(self.grid_scroller)
            #lay.addLayout(self.gridLayout)
            self.gridWidget= QtGui.QWidget()
            self.gridWidget.setLayout(self.gridLayout)
            self.grid_scroller.setWidget(self.gridWidget)
            self.grid_scroller.setWidgetResizable(True)
            self.setupGrid()
            self.buttonLayout = QtGui.QHBoxLayout()
            lay.addLayout(self.buttonLayout)
            self.buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok.__or__(QtGui.QDialogButtonBox.Cancel),\
                QtCore.Qt.Horizontal, self)
            self.buttons.accepted.connect(self.accept)
            self.buttons.rejected.connect(self.reject)
            self.helpCheckBox = QtGui.QCheckBox("Show help")
            self.helpCheckBox.setChecked(False)
            self.helpCheckBox.clicked.connect(self.showHelp)
            self.buttonLayout.addWidget(self.helpCheckBox)
            self.buttonLayout.addWidget(self.buttons)
            self.helpLabel = QtGui.QLabel("Help goes here.")
            self.setupHelpText()
            self.scroll_area = QtGui.QScrollArea()
            lay.addWidget(self.scroll_area)
            self.scroll_area.setWidget(self.helpLabel)
            self.scroll_area.setVisible(False)

            if hasConfig:
                self.fillUpLineEdits()

        def setupHelpText(self):
            txt = """\
A configuration is a set of properties that work together to allow you to set multiple
properties by selecting the configuration you want in an enumeration property.  The
enumeration property is at the heart of the configuration.  The Configuration name: field
will be the name of this enumeration property.  It will also be the name of the group that
the variable properties go into and the name of another group + the word "Lists" that the
list properties will go into.

For example, if the name of the configuration is "Configuration" then you will have a group
named "Configuration" and inside that group an Enumeration property also named "Configuration".
Plus, you will have another group named "Configuration Lists" and inside that group will be a
number of FloatList properties, one for each variable you have.  If you have these 3 variables:
"Height", "Width", and "Length", then in the Configuration group you will have 3 Float properties
of the same name and in the Configration List group there will be "Height List", "Width List",
and "Length List", all FloatList types.

We have 3 different property types: 1) the enumeration property that serves as the configuration
selector; 2) the variable properties (whose names are in the left column, e.g. Height, or Radius);
and 3) the list properties that hold the values the variable properties index into based on which
configuration has been selected.  All variable properties are of type Float and all list properties
are of type FloatList.  (You can replace them with Integer or String property types if you like
after building the configuration by deleting them and adding new properties with the same name,
but if you use the configuration editor to edit the configuration later they will be replaced
again with Float and FloatList types.)

Enum count is how many enums we have in this configuration.  The default is 5, which are "Extra
Small", "Small", "Medium", "Large", and "Extra Large".  "Select size" is not really an enum, but
it will go into the enumeration as a default message to the user.  Edit this so it makes sense
for the enums you are using.  Edit all of these enums by changing their text.  You can remove some
by reducing the Enum count, which can be anywhere from 2 to 100.  You must have at least 2 enums
in the configuration.  Note: when you reduct Enum count or Variable count you lose those rows or
columns, including any data contained in the cells, even if you increase the count afterwards.
When you increase the count you get another row or column with generic names like Variable5 or
Enum7.

Enter the values in the cells that you want for each enum and variable.  In the example default
configuration you have Height, for example.  If you want the Height for the Extra Small enum to
be 2, enter 2 in the cell that aligns with Height and Extra Small.  Any cells left blank will be
filled with the value from the first cell in that row, or 0.0 if it is also blank.

Note: when the "Select size" enum is selected in the enumeration property all of the variable
values will be the value from the first enum, so that it won't break your model until you can
select one of the enums.  Select size is actually an additional extra set of values added to the
ends of the List properties.  You can manually edit these later if you want different defaults.
Your manually edited defaults will not be changed by the editor unless you also change the
number of enums during the edit.

You may apply a configuration to an existing object, such as a Part::Cylinder, and if your variable
names are the same as existing properties, those properties will be incorporated into the configuration.

You may have multiple configurations in the same object, but if you do so you should ensure none of
the variable are the same or else there will be a conflict and the new properties will overwrite the
existing ones.  It is recommended to only have 1 configuration per object.

Variable count is how many variables to have in the configuration.  By default we have 3.  These are:
"Height", "Length", and "Radius".  This are likely not to be the names you will want for your
configuration.  They are just there as placeholders to serve as examples in the default configuration.
You can add more or remove some by changing the Variable count value.

If you click Cancel your changes will be discarded.  If you click OK your configuration will be added
to the selected object.  ANY EXISTING PROPERTIES of the same names WILL BE REPLACED.  But have no fear,
you can use Undo to revert all your changes to the selected object.

"""
            self.helpLabel.setText(txt)

        def showHelp(self):
            self.scroll_area.setVisible(self.helpCheckBox.isChecked())

        def eventFilter(self, obj, event):
            if event.type() == QtGui.QKeyEvent.KeyPress:
                if bool(event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Tab):
                    self.curLineEdit = obj
                    self.handleCtrlTab(False)
                    return True  # Event handled

                elif bool(event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Backtab):
                    self.curLineEdit = obj
                    self.handleCtrlTab(True)
                    return True  # Event handled

            return super().eventFilter(obj, event)

        def handleCtrlTab(self, bShift = False):
            row,col = self.getRowColFromObjectName(self.curLineEdit.objectName())
            objName = f"{row + 1}_{col}" if not bShift else f"{row - 1}_{col}"
            next = self.getLineEditFromConfiguration(objName, bCreate = False)
            if not next:
                return
            else:
                next.setFocus()


        def getLineEditFromConfiguration(self, objName, bCreate = True):
            """get the line edit objName from dictionary if it exists, else created it"""
            lineEdit = None
            for name,obj in self.configuration["lineEdits"].items():
                if name == objName:
                    lineEdit = obj
                    break
            if not lineEdit and bCreate:
                lineEdit = QtGui.QLineEdit()
                lineEdit.setObjectName(objName)
                lineEdit.installEventFilter(self)
                lineEdit.setToolTip("Tab -> next column\nCtrl+Tab -> next row\nCtrl+Shift+Tab ->previous row\nShift+Tab -> previous column")
            elif not bCreate and not lineEdit:
                return None
            self.configuration["lineEdits"][objName] = lineEdit
            return lineEdit

        def addToGrid(self, lineEdit, row, col):
            """add the LineEdit to the grid at row, col"""
            def trigger(objName):
                self.lineEditTextChanged(objName)
            self.gridLayout.addWidget(lineEdit, row, col)
            label = ""
            if row == 0:
                try:
                    label = self.configuration["enums"][col]
                except:
                    label = f"Enum{col}"
                    self.configuration["enums"].append(f"Enum{col}")
            elif col == 0:
                try:
                    label = self.configuration["variables"][row-1]
                except:
                    self.configuration["variables"].append(f"Variable{row}")
                    label = f"Variable{row}"
            lineEdit.setText(label)
            lineEdit.textChanged.connect(lambda text,name=lineEdit.objectName(): trigger(name))
            self.gridLayout.addWidget(lineEdit,row,col)
            self.update()
            FreeCADGui.updateGui()

        def updateTabOrders(self):
            """update the tab orders when adding/removing lineEdit to/from grid"""
            def custom_sort(s):
                # Split the string into parts
                parts = s.split('_')

                # Convert the parts to integers
                x = int(parts[0])
                y = int(parts[1])

                # Combine them using a formula
                return x * 100 + y

            names = {}
            for name,obj in self.configuration["lineEdits"].items():
                names[name] = obj.objectName()
            names = sorted(names, key=custom_sort)
            edits = [self.configuration["lineEdits"][name] for name in names]
            for ii in range(len(edits)-1):
                self.setTabOrder(edits[ii], edits[ii+1])

        def removeFromGrid(self, le):
            """remove the line edit from the grid and from the dictionary"""

            if le.objectName() in self.configuration["lineEdits"].keys():
                val = self.configuration["lineEdits"].pop(le.objectName())
            row,col = self.getRowColFromObjectName(le.objectName())
            widget = self.gridLayout.itemAtPosition(row,col)
            if widget:
                widget.widget().deleteLater()
            self.update()
            FreeCADGui.updateGui()

        def setupGrid(self):
            """setup the grid based on the values in self.configuration dictionary"""
            for row in range(self.configuration["variableCount"]+1):
                for col in range(self.configuration["enumCount"]+1):
                    lineEdit = self.getLineEditFromConfiguration(f"{row}_{col}")
                    self.addToGrid(lineEdit, row, col)

        def lineEditTextChanged(self, lineEditObjectName):
            lineEdit = self.getLineEditFromConfiguration(lineEditObjectName)
            row,col = self.getRowColFromObjectName(lineEditObjectName)
            if row == 0:
                self.configuration["enums"][col] = lineEdit.text()
            elif col == 0:
                self.configuration["variables"][row-1] = lineEdit.text()

        def getRowColFromObjectName(self, objName):
            """returns a tuple (row,col) gotten from the line edit object name
               which is always in the form of row_col"""
            row,col = objName.split("_")
            row = int(row)
            col = int(col)
            return (row,col)

        def isOutOfBounds(self, lineEdit):
            """check if this line edit object needs to be removed from the grid
               by comparing its row,col to enum count and variable count"""
            row,col = self.getRowColFromObjectName(lineEdit.objectName())
            enums = self.enumCount.value()
            variables = self.variableCount.value()
            if col  > enums:
                return True
            if row  > variables:
                return True
            return False

        def updateDict(self):
            """called only when the enum count or variable count changes
               in which cases we need to update the grid of line edits
               updates the dictionary (self.configuration) based on values in form"""
            self.configuration["name"] = self.configurationName.text()
            self.configuration["enumCount"] = self.enumCount.value()
            self.configuration["variableCount"] = self.variableCount.value()

            lineEditsToRemove = [le for le in self.configuration["lineEdits"].values() if self.isOutOfBounds(le)]
            for le in lineEditsToRemove:
                row,col = self.getRowColFromObjectName(le.objectName())
                if row == 0:
                    self.configuration["enums"].pop()
                if col == 0:
                    self.configuration["variables"].pop()
                self.removeFromGrid(le)
            # if lineEditsToRemove:
            #     return
            # now we need to see if we need to add any rows or columns
            numRows = len(self.configuration["variables"])
            numCols = len(self.configuration["enums"])
            enums = self.enumCount.value()
            variables = self.variableCount.value()

            while numCols < enums + 1:
                #need to add a new column, so for each row we add one
                for row in range(numRows+1):
                    lineEdit = self.getLineEditFromConfiguration(f"{row}_{numCols}")
                    self.addToGrid(lineEdit, row, numCols)
                numCols = len(self.configuration["enums"])

            while numRows < variables:
                #need to a new row, so for each column we add one
                for col in range(numCols):
                    lineEdit = self.getLineEditFromConfiguration(f"{numRows+1}_{col}")
                    self.addToGrid(lineEdit, numRows+1, col)
                numRows = len(self.configuration["variables"])
            self.updateTabOrders()

        def getRowValues(self,row):
            """get the line edit values in row as a list"""
            ret = []
            for col,enum in enumerate(self.configuration["enums"]):
                objName = f"{row+1}_{col+1}"
                lineEdit = self.getLineEditFromConfiguration(objName)
                val = 0
                try:
                    val = float(lineEdit.text())
                except:
                    if lineEdit.text():
                        FreeCAD.Console.PrintWarning(f"Couldn't convert to float: {lineEdit.text()} row,col = {row},{col}\n")
                    else:
                        #take value from first cell in row and use that for default
                        firstCell = self.getLineEditFromConfiguration(f"{row+1}_{1}")
                        try:
                            val = float(firstCell.text())
                        except:
                            val = 0
                ret.append(val)
            return ret

        def setConfiguration(self):
            """setup the configuration"""
            dd = self.dd
            name = self.configuration["name"]
            if hasattr(dd,name):
                try:
                    dd.removeProperty(name)
                except:
                    FreeCAD.Console.PrintWarning(f"Unable to remove property: {name}\n")
            if not hasattr(dd,name):
                dd.addProperty("App::PropertyEnumeration",name,name,"Configuration enumeration")
            setattr(dd,name,self.configuration["enums"])
            for row,var in enumerate(self.configuration["variables"]):
                if hasattr(dd,f"{var}List"):
                    try:
                        dd.removeProperty(f"{var}List")
                        FreeCAD.Console.PrintMessage(f"Removed property {var}List\n")
                    except:
                        FreeCAD.Console.PrintWarning(f"Unable to remove property: {var}List\n")
                if not hasattr(dd,f"{var}List"):
                    dd.addProperty("App::PropertyFloatList",f"{var}List",f"{name}Lists",f"List property for {var}")
                    FreeCAD.Console.PrintMessage(f"Added property {var}List\n")
                setattr(dd,f"{var}List", self.getRowValues(row))
                if hasattr(dd,var):
                    try:
                        dd.removeProperty(var)
                        FreeCAD.Console.PrintMessage(f"Removed property {var}\n")
                    except:
                        FreeCAD.Console.PrintWarning(f"Unable to remove property: {var}\n")
                if not hasattr(dd,var):
                    dd.addProperty("App::PropertyFloat",var,name,"Property to link to")
                    FreeCAD.Console.PrintMessage(f"Added property {var}\n")
                dd.setExpression(var,f"{dd.Label}.<<{dd.Label}>>.{var}List[<<{dd.Label}>>.{name}-1]")

        def getConfigurationFromObject(self):
            """return True if we imported one from an object, else False if this is a new configuration"""
            dd = self.dd
            ignored = ["MapMode"]
            props = [prop for prop in dd.PropertiesList if "Enumeration" in dd.getTypeIdOfProperty(prop) and prop not in ignored]

            if len(props) >= 1:
                default_item = 0
                props = ["New configuration"] + props
                prop, ok = QtGui.QInputDialog.getItem(self, "Select configuration", \
                                                      "Choose an enumeration to edit or create a new one\n (Cancel for a new default configuration)",\
                                                       props, default_item, editable=False)
                if not ok or prop == props[0]:
                    self.makeDefaultConfiguration()
                    return False
                else:
                    self.importConfiguration(prop)
                    return True

            else: #no existing enumerations
                self.makeDefaultConfiguration()
                return False

        def importConfiguration(self,prop):
            """imports the configuration from the object where prop is the name of the enumeration"""
            self.configuration["name"] = prop
            self.configuration["enums"] = self.dd.getEnumerationsOfProperty(prop)
            vars = [prop2 for prop2 in self.dd.PropertiesList if hasattr(self.dd,f"{prop2}List")]
            #lists = [prop for prop in dd.PropertiesList if hasattr(dd,prop[:-4])] #drop List from end of property name
            self.configuration["variables"] = vars
            self.configuration["lineEdits"] = {}
            self.configuration["enumCount"] = len(self.configuration["enums"])-1
            self.configuration["variableCount"] = len(vars)

        def makeDefaultConfiguration(self):
            self.configuration["name"] = "Configuration"
            self.configuration["enumCount"] = 5
            self.configuration["variableCount"] = 3
            self.configuration["enums"] = ["Select size","Extra Small","Small","Medium",\
                                        "Large","Extra Large"]
            self.configuration["variables"] = ["Length", "Height", "Radius"]
            self.configuration["lineEdits"] = {}

        def fillUpLineEdits(self):
            """called from __init__() only if dd object has a configuration already,
            so we are going to fill in the Line Edits from that data"""
            #look for List properties
            for var in self.configuration["variables"]:
                lists = [prop for prop in self.dd.PropertiesList if prop == f"{var}List"]
                for ls in lists:
                    values = getattr(self.dd, ls) #e.g. HeightList = [10,20,30], now values = [10,20,30]
                    row = self.configuration["variables"].index(var)
                    for col,val in enumerate(values):
                        lineEdit = self.getLineEditFromConfiguration(f"{row+1}_{col+1}")
                        lineEdit.setText(str(round(val,6)))

        def accept(self):
            self.dd.Document.openTransaction("Create/Edit Configuration")
            self.setConfiguration()
            self.dd.Document.commitTransaction()
            super().accept()

        def reject(self):
            super().reject()


    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'DynamicDataCreateConfiguration.svg'),
                'MenuText': "Create/Edit Con&figuration",
                'Accel'   : "Ctrl+Shift+D,F",
                'ToolTip' : "Create or edit an existing configuration in the selected object"}

    def __init__(self):
        self.props = []
        self.obj = None

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        dlg = self.DynamicDataConfigurationDlg(self.obj) #self.obj is the selected object
        dlg.props = self.props
        dlg.exec_()
        doc.recompute()
        return

    def IsActive(self):
        if not FreeCAD.ActiveDocument:
            return False
        selection = Gui.Selection.getSelection()
        if len(selection) == 1:
            self.obj = selection[0]
            return True
        #where nothing is selected and there is only one dd object, use that object
        if len(selection) == 0:
            dds = [obj for obj in FreeCAD.ActiveDocument.Objects if hasattr(obj,"DynamicData")]
            if len(dds) == 1:
                self.obj = dds[0]
                return True
        return False


#Gui.addCommand("DynamicDataCreateConfiguration", DynamicDataCreateConfigurationCommandClass())


####################################################################################
# Edit an existing Enumeration property

class DynamicDataEditEnumerationCommandClass(DynamicDataBaseCommandClass):
    """Edit Enumeration command"""

    class DynamicDataEnumerationDlg(QtGui.QDialog):
        def __init__(self,dd,props):
            super(DynamicDataEditEnumerationCommandClass.DynamicDataEnumerationDlg, self).__init__(Gui.getMainWindow())
            self.dd = dd
            self.ok = False
            self.props = props
            self.items = []
            self.enumerations = {}
            self.setupEnumerations()
            self.setAttribute(QtCore.Qt.WA_WindowPropagation, True)
            self.setWindowTitle(f"DynamicData v{__version__} Enumeration Editor")
            lay = QtGui.QVBoxLayout(self)
            self.setLayout(lay)
            self.propertiesLabel = QtGui.QLabel("Enumeration Properties:")
            self.propertiesListBox = QtGui.QListWidget(self)

            for prop in self.props:
                item = QtGui.QListWidgetItem(prop)
                self.items.append(item)
                self.propertiesListBox.addItem(item)

            self.propertiesListBox.setSelectionMode(QtGui.QListWidget.SingleSelection)
            self.propertiesListBox.itemClicked.connect(self.handlePropertiesListBoxItemClicked)
            if self.items:
                self.propertiesListBox.setCurrentItem(self.items[0])
            lay.addWidget(self.propertiesLabel)
            lay.addWidget(self.propertiesListBox)
            self.textEditLabel = QtGui.QLabel("Edit the selected property by typing here:")
            lay.addWidget(self.textEditLabel)

            self.textEdit = QtGui.QPlainTextEdit()
            self.textEdit.textChanged.connect(self.textChanged)
            lay.addWidget(self.textEdit)
            self.buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok.__or__(QtGui.QDialogButtonBox.Cancel),\
                QtCore.Qt.Horizontal, self)
            self.buttons.accepted.connect(self.accept)
            self.buttons.rejected.connect(self.reject)
            lay.addWidget(self.buttons)
            self.setupTextEdit()

        def handlePropertiesListBoxItemClicked(self, item):
            """a new enumeration property was selected, so set the QPlainTextEdit"""
            self.updateTextEdit()

        def textChanged(self):
            """The QPlainTextEdit changed, so update enums"""
            self.updateEnumerations()

        def setupEnumerations(self):
            """setup enums from the dd object enumerations"""
            for prop in self.props:
                if not prop in self.enumerations:
                    self.enumerations[prop] = self.dd.getEnumerationsOfProperty(prop)

        def updateEnumerations(self):
            """update enums from QPlainTextEdit"""
            prop = self.getCurrentProp()
            self.enumerations[prop] = self.getTextEditStrings()

        def getCurrentProp(self):
            return self.props[self.propertiesListBox.currentRow()]

        def setupTextEdit(self):
            """puts the text into the QPlainTextEdit from the dd object enumeration properties"""
            if self.props:
                prop = self.props[self.propertiesListBox.currentRow()]
                enums = self.dd.getEnumerationsOfProperty(prop)
                textString = "\n".join(enums)
                self.textEdit.setPlainText(textString)

        def updateTextEdit(self):
            """update the QPlainTextEdit from enums"""
            prop = self.props[self.propertiesListBox.currentRow()]
            enums = self.enumerations[prop]
            textString = "\n".join(enums)
            self.textEdit.setPlainText(textString)

        def getTextEditStrings(self):
            """return the text edit contents as a list of strings"""
            txt = self.textEdit.toPlainText()
            split_text = txt.split("\n")
            return split_text

        def accept(self):
            self.ok = True
            super().accept()

        def reject(self):
            super().reject()


    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'DynamicDataEditEnumerations.svg'),
                'MenuText': "&Edit Enumerations",
                'Accel'   : "Ctrl+Shift+D,E",
                'ToolTip' : "Edit properties of type Enumeration in selected object"}

    def __init__(self):
        self.props = []
        self.obj = None

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        if not self.props:
            FreeCAD.Console.PrintError("DynamicData: Error, no property of type \
Enumeration to edit.  Create one first, and then try again.\n")
            return

        dlg = self.DynamicDataEnumerationDlg(self.obj, self.props) #the dd object
        dlg.props = self.props
        dlg.exec_()
        if dlg.ok:
            doc.openTransaction("Edit Enumeration")
            self.setEnumerations(dlg.enumerations)
            doc.commitTransaction()
        doc.recompute()
        return

    def setEnumerations(self, enum_dict):
        """set the properties of type Enumeration of the dd object from the dictionary enum_dict"""
        dd = self.obj
        for k,v in enum_dict.items():
            setattr(dd,k,v)

    def getEnumerations(self, dd):
        """get the properties of type Enumeration in the selected object
           return the list of such properties or [] if none.  We don't verify
           this is a dd object because we will support all objects, but we will
           ignore some known enumeration properties, such as MapMode"""

        ignored = ["MapMode"]
        self.props = [prop for prop in dd.PropertiesList if bool (not prop in ignored and "App::PropertyEnumeration" in dd.getTypeIdOfProperty(prop))]
        return self.props

    def IsActive(self):
        if not FreeCAD.ActiveDocument:
            return False
        selection = Gui.Selection.getSelection()
        if len(selection) == 1 and self.getEnumerations(selection[0]):
            self.obj = selection[0]
            return True
        #where nothing is selected and there is only one dd object, use that object if it has an enumeration property
        if len(selection) == 0:
            dds = [obj for obj in FreeCAD.ActiveDocument.Objects if hasattr(obj,"DynamicData")]
            if len(dds) == 1:
                self.obj = dds[0]
                if self.getEnumerations(self.obj):
                    return True
        return False


#Gui.addCommand("DynamicDataEditEnumeration", DynamicDataEditEnumerationCommandClass())

####################################################################################
# dialog for adding new property

class MultiTextInput(QtGui.QDialog):
    def __init__(self, obj):
        QtGui.QDialog.__init__(self)
        self.obj = obj
        layout = QtGui.QGridLayout()
        #layout.setColumnStretch(1, 1)
        self.addAnotherProp = False
        self.label = QtGui.QLabel(self)
        self.propertyTypeLabel = QtGui.QLabel("Select App::Property type:")
        self.listWidget = QtGui.QListWidget()
        self.listWidget.currentItemChanged.connect(self.onListWidgetCurrentItemChanged)
        self.label2 = QtGui.QLabel(self)
        self.label2.setStyleSheet('color: red')
        self.nameLabel = QtGui.QLabel("Name: dd")
        self.nameEdit = QtGui.QLineEdit(self)
        self.nameEdit.textChanged.connect(self.on_text_changed)
        self.valueLabel = QtGui.QLabel("Value: ")
        self.valueEdit = QtGui.QLineEdit(self)
        self.valueEdit.textChanged.connect(self.on_value_changed)
        self.groupLabel = QtGui.QLabel("Group: ")
        self.groupCombo = QtGui.QComboBox(self)
        self.groupCombo.setEditable(True)
        self.tooltipLabel = QtGui.QLabel("Tooltip: ")
        self.tooltipPrependLabel = QtGui.QLabel("")
        self.tooltipEdit = QtGui.QLineEdit(self)

        layout.addWidget(self.label, 0, 0, 2, 5)
        layout.addWidget(self.propertyTypeLabel, 2, 0, 2, 6)
        layout.addWidget(self.listWidget, 4, 0, 1, 6)
        layout.addWidget(self.nameLabel, 5, 0, 1, 1)
        layout.addWidget(self.nameEdit, 5, 1, 1, 5)
        layout.addWidget(self.valueLabel, 6, 0, 1, 1)
        layout.addWidget(self.valueEdit, 6, 1, 1, 5)
        layout.addWidget(self.groupLabel, 7, 0, 1, 1)
        layout.addWidget(self.groupCombo, 7, 1 , 1, 5)
        layout.addWidget(self.tooltipLabel, 8, 0, 1, 1)
        layout.addWidget(self.tooltipPrependLabel, 8, 1, 1, 1)
        layout.addWidget(self.tooltipEdit, 8, 2, 1, 4)
        layout.addWidget(self.label2, 10, 0, 1, 5)
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok.__or__(QtGui.QDialogButtonBox.Cancel),
            QtCore.Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.setCenterButtons(True)
        addAnother = QtGui.QPushButton("Apply", self)
        self.buttons.addButton(addAnother, QtGui.QDialogButtonBox.ActionRole)
        addAnother.clicked.connect(self.addAnotherProperty)
        layout.addWidget(self.buttons, 11, 0, 1, 5)
        self.setLayout(layout)

    def addAnotherProperty(self):
        self.addAnotherProp = True
        self.accept()

    def onListWidgetCurrentItemChanged(self,current,previous):
        if previous and previous.text() in self.nameEdit.text():
            self.nameEdit.setText(self.nameEdit.text().replace(previous.text(),current.text()))

    def on_value_changed(self): #commented out for now because it throws exceptions even inside try: except: block
        pass
        #obj = FreeCAD.ActiveDocument.ActiveObject
        #val = self.valueEdit.text()
        #result = "Invalid expression as of yet"
        #if len(val) > 1 and val[0] == "=":
        #    try:
        #        result = obj.evalExpression(val[1:])
        #        self.label2.setStyleSheet('color: black')
        #    except:
        #        self.label2.setStyleSheet('color: red')
        #    self.label2.setText(str(result))

    def on_text_changed(self):
        cur = self.nameEdit.text()
        if len(cur) == 1:
            cur = cur.upper()
        elif len(cur) > 1:
            cur = cur[0].upper() + cur[1:]
        else:
            return
        self.nameEdit.setText(cur)
        self.on_edit_finished()

    def on_edit_finished(self):
        if ";" in self.nameEdit.text():
            hasValue = False
            propertyName = self.nameEdit.text()
            split = propertyName.split(';')
            propertyName = split[0].replace(' ','_')
            if len(propertyName)==0:
                propertyName = "Prop"
            if len(split)>1: #has a group name
                if len(split[1])>0: #allow for ;; empty string to mean use current group name
                    self.groupCombo.setCurrentText(split[1])
            if len(split)>2: #has a tooltip
                if len(split[2])>0:
                    self.tooltipEdit.setText(split[2])
            if len(split)==4: #has a value
                hasValue = True
                val = split[3]
            self.groupCombo.setEnabled(False)
            if hasValue:
                self.valueEdit.setText(val)
            self.valueEdit.setEnabled(False)
            self.tooltipEdit.setEnabled(False)
        else:
            self.groupCombo.setEnabled(True)
            self.valueEdit.setEnabled(True)
            self.tooltipEdit.setEnabled(True)
            propertyName = self.nameEdit.text()
        if hasattr(self.obj,'dd'+propertyName):
            self.label2.setText('Property name already exists')
        else:
            self.label2.setText('')


######################################################################################
# Add a dynamic property to the object


class DynamicDataAddPropertyCommandClass(DynamicDataBaseCommandClass):
    """Add Property Command"""
    global mostRecentTypes
    global mostRecentTypesLength

    def __init__(self):
        self.obj = None

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'AddProperty.svg'),
                'MenuText': "&Add Property",
                'Accel'   : "Ctrl+Shift+D,A",
                'ToolTip' : "Add a custom property to the DynamicData object"}

    def Activated(self):
        global mostRecentTypes
        global mostRecentTypesLength

        doc = FreeCAD.ActiveDocument
        obj = self.obj
        if not 'FeaturePython' in str(obj.TypeId):
            FreeCAD.Console.PrintError('DynamicData Workbench: Cannot add property to non-FeaturePython objects.\n')
            return
        doc.openTransaction("dd Add Property")
        #add the property
        #window = QtGui.QApplication.activeWindow()
        items = self.PropertyTypes
        recent = []
        pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")
        mostRecentTypesLength = pg.GetInt('mruLength',5)
        for ii in range(mostRecentTypesLength-1,-1,-1):
            if mostRecentTypes[ii]:
                recent.insert(0,mostRecentTypes[ii])
                pg.SetString('mru'+str(ii), mostRecentTypes[ii])

        dlg = MultiTextInput(obj)
        dlg.setWindowFlags(windowFlags)
        dlg.setWindowTitle("DynamicData")
        dlg.label.setText("Old-style name;group;tip;value syntax\nstill supported in Name field\n\nIn Value field:\nUse =expr for expressions, e.g. =Box.Height\n")
        items = recent+items
        dlg.listWidget.addItems(items)
        dlg.listWidget.setCurrentRow(0)
        item = items[0]
        vals=['']
        for ii in range(1,1000):
            vals.append(str(ii))
        idx = 0
        while hasattr(obj,'dd' + item + str(vals[idx])):
            idx += 1
        item + str(vals[idx])
        dlg.nameEdit.setText(item + vals[idx])

        if hasattr(obj,'dd'+ item + vals[idx]):
            dlg.label2.setText('Property name already exists')
        else:
            dlg.label2.setText('')
        dlg.nameEdit.selectAll()
        if "List" in item:
            dlg.valueLabel.setText("Values:")
            dlg.label.setText("List values should be semicolon delimited, e.g. 1;2;3;7")
        props = obj.PropertiesList
        groups = []
        groups.append(self.groupName)
        for p in props:
            cur_group = obj.getGroupOfProperty(p)
            if len(cur_group) > 0 and not cur_group in groups:
                groups.append(cur_group)
        dlg.groupCombo.addItems(groups)
        dlg.tooltipLabel.setText("Tooltip:")
        dlg.tooltipPrependLabel.setText("["+item+"]")

        ok = dlg.exec_()
        if not ok:
            return
        item = dlg.listWidget.currentItem().text()
        if not item in mostRecentTypes:
            mostRecentTypes.insert(0,item)
        else:
            mostRecentTypes.remove(item) #ensure it is at front of the list
            mostRecentTypes.insert(0,item)
        if len(mostRecentTypes)>mostRecentTypesLength:
            mostRecentTypes = mostRecentTypes[:mostRecentTypesLength]
        for ii in range(mostRecentTypesLength-1,-1,-1):
            if mostRecentTypes[ii]:
                pg.SetString('mru'+str(ii), mostRecentTypes[ii])
        if not ";" in dlg.nameEdit.text():
            self.propertyName = dlg.nameEdit.text() + ";" \
                              + dlg.groupCombo.currentText() + ";" \
                              + dlg.tooltipEdit.text() + ";" \
                              + dlg.valueEdit.text()
        else:
            self.propertyName = dlg.nameEdit.text()
        if len(self.propertyName)==0:
            self.propertyName=';;;' #use defaults

        if 'dd' in self.propertyName[:2] or 'Dd' in self.propertyName[:2]:
            self.propertyName = self.propertyName[2:] #strip dd temporarily
        cap = lambda x: x[0].upper() + x[1:] #credit: PradyJord from stackoverflow for this trick
        self.propertyName = cap(self.propertyName) #capitalize first character to add space between dd and self.propertyName
        self.tooltip='['+item+'] ' #e.g. [Float]
        val=None
        vals=[]
        hasVal = False
        listval = ''
        if ';' in self.propertyName:
            split = self.propertyName.split(';')
            self.propertyName = split[0].replace(' ', '_')
            if len(self.propertyName)==0:
                self.propertyName = self.defaultPropertyName
            if len(split)>1: #has a group name
                if len(split[1])>0: #allow for ;; empty string to mean use current group name
                    self.groupName = split[1]
            if len(split)>2: #has a tooltip
                if len(split[2])>0:
                    self.tooltip = self.tooltip + split[2]
            if len(split)>=4: #has a value
                if "=list(" in split[3]:
                    listval = split[3]
                    for ii in range(4, len(split)):
                        listval += ';' + split[ii]
                val = split[3]
                if len(val)>0:
                    hasVal = True
            if len(split)>4 and 'List' in item: #multiple values for list type property
                hasVal = True
                for ii in range(3,len(split)):
                    try:
                        if len(split[ii])>0:
                            vals.append(self.eval_expr(split[ii]))
                    except Exception as ex:
                        FreeCAD.Console.PrintError(f"dd: {ex}\n")
                        vals.append(split[ii])
        if hasattr(obj,'dd'+self.propertyName):
            FreeCAD.Console.PrintError('DyamicData: Unable to add property: dd'+self.propertyName+' because it already exists.\n')
            self.checkAddAnother(dlg)
            return
        p = obj.addProperty('App::Property'+item,'dd'+self.propertyName,str(self.groupName),self.tooltip)
        if hasVal and len(vals)==0:
            if val[0] == "=":
                try:
                    obj.setExpression('dd'+self.propertyName, val[1:])
                    obj.touch()
                    doc.recompute()
                    doc.commitTransaction()
                    self.checkAddAnother(dlg)
                    return
                except:
                    FreeCAD.Console.PrintWarning('DynamicData: Unable to set expreesion: '+str(val[1:])+'\n')
                    doc.commitTransaction()
                    self.checkAddAnother(dlg)
                    return
            try:
                atr = self.eval_expr(val)
            except:
                #try:
                #    atr = val
                #except:
                FreeCAD.Console.PrintWarning('DynamicData: Unable to set value: '+str(val)+'\n')
            try:
                if item == "Enumeration":
                    list2 = split[3:]
                    try:
                        setattr(p,'dd'+self.propertyName, list2)
                    except Exception:
                        FreeCAD.Console.PrintWarning("DynamicData: Unable to set list enumeration: "+str(list)+"\n")
                else:
                    setattr(p,'dd'+self.propertyName,atr)
            except:
                FreeCAD.Console.PrintWarning('DynamicData: Unable to set attribute: '+str(val)+'\n')
        elif hasVal and len(vals)>0:
            if listval:
                try:
                    obj.setExpression('dd'+self.propertyName, listval[1:]) #[1:] strips the "="
                    obj.touch()
                    doc.recompute()
                    doc.commitTransaction()
                    self.checkAddAnother(dlg)
                    return
                except:
                    FreeCAD.Console.PrintWarning('DynamicData: Unable to set expression: '+str(listval[1:])+'\n')
                    doc.commitTransaction()
                    self.checkAddAnother(dlg)
                    return
            try:
                setattr(p,'dd'+self.propertyName,list(vals))
            except:
                FreeCAD.Console.PrintWarning('DynamicData: Unable to set list attribute: '+str(vals)+'\n')
        obj.touch()
        doc.recompute()

        doc.commitTransaction()
        doc.recompute()
        self.checkAddAnother(dlg)
        return

    def checkAddAnother(self,dlg):
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier or dlg.addAnotherProp: #Ctrl+OK or Add another
            self.Activated()

    def IsActive(self):
        if not FreeCAD.ActiveDocument:
            return False
        selection = Gui.Selection.getSelection()
        if len(selection) == 1 and hasattr(selection[0],"DynamicData"):
            self.obj = selection[0]
            return True
        objs = [obj for obj in FreeCAD.ActiveDocument.Objects if hasattr(obj, "DynamicData")]
        if len(objs) == 1:
            self.obj = objs[0]
            return True
        return False

    def __init__(self):
        #global mostRecentTypes
        global mostRecentTypesLength
        import ast, locale
        import operator as op
        self.groupName="DefaultGroup"
        self.defaultPropertyName="Prop"
        self.tooltip="tip"

        pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")
        mostRecentTypesLength = pg.GetInt('mruLength',5)
        for ii in range(0, mostRecentTypesLength):
            mostRecentTypes.append(pg.GetString('mru'+str(ii),""))

        self.SEPARATOR = locale.localeconv()['decimal_point']
        self.SEPARATOR_STANDIN = 'p'
        self.DEGREES_INDICATOR = 'd'
        self.RADIANS_INDICATOR = 'r'

        # for evaluating math expressions in gui input text fields
        # credit "jfs" of stackoverflow for these 2 functions, which I modified for my needs
        # supported operators


        self.operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor, #ast.BitXor: op.pow would remap ^ to pow()
             ast.USub: op.neg}
        #add some constants and references that might be useful for users
        self.constants = {'pi':math.pi,'e':math.e, 'phi':16180339887e-10, 'golden':16180339887e-10,'golden_ratio':16180339887e-10,
             'inch':254e-1, 'in':254e-1,'inches':254e-1, 'thou':254e-4}
        self.references= {'version':'version'}
        self.maths = {'cos':'cos','acos':'acos','tan':'tan','atan':'atan','sin':'sin','asin':'asin','log':'log','tlog':'log10'}

    def eval_this(self,node):
        import ast
        import operator as op
        if isinstance(node, ast.Num): # <number>
            return node.n
        elif isinstance(node, ast.BinOp): # <left> <operator> <right>
            return self.operators[type(node.op)](self.eval_this(node.left), self.eval_this(node.right))
        elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
            return self.operators[type(node.op)](self.eval_this(node.operand))
    #provide support for constants and references
        elif node.id:
            if node.id in self.constants:
                return self.constants[node.id]
            elif node.id in self.references: #e.g. references[node.id] is a string, e.g. 'version' representing global variable version
                return globals()[self.references[node.id]]
            elif node.id[:3] in self.maths:
                func = getattr(math, self.maths[node.id[:3]])
                opstring = node.id[3:].replace(self.SEPARATOR_STANDIN,self.SEPARATOR)
                if opstring[-1:]==self.DEGREES_INDICATOR:
                    opstring = opstring[:-1]
                    return func(float(opstring)*math.pi/180.0)
                elif opstring[-1:]==self.RADIANS_INDICATOR:
                    opstring = opstring[:-1]
                    return func(float(opstring))
                else:
                    return func(float(opstring))
            elif node.id[:4] in self.maths:
                func = getattr(math, self.maths[node.id[:4]])
                opstring = node.id[4:].replace(self.SEPARATOR_STANDIN,self.SEPARATOR)
                if opstring[-1:]==self.DEGREES_INDICATOR:
                    opstring = opstring[:-1]
                    return func(float(opstring)*math.pi/180.0)
                elif opstring[-1:]==self.RADIANS_INDICATOR:
                    opstring = opstring[:-1]
                    return func(float(opstring))
                else:
                    return func(float(opstring))
            else:
                App.Console.PrintError('ast evaluator: unsupported token: '+node.id+'\n')
        else:
            raise TypeError(node)

    def eval_expr(self,expr):
        import ast
        import operator as op
        """
        >>> eval_expr('2^6')
        4
        >>> eval_expr('2**6')
        64
        >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
        -5.0
        """
        return self.eval_this(ast.parse(expr, mode='eval').body)

#Gui.addCommand("DynamicDataAddProperty", DynamicDataAddPropertyCommandClass())

########################################################################################
# Rename group

class DynamicDataMoveToNewGroupCommandClass(DynamicDataBaseCommandClass):
    """Move properties to new group"""

    def GetResources(self):
        return {'Pixmap'  : "",
                'MenuText': "Move to new &group",
                'Accel'   : "Ctrl+Shift+D,G",
                'ToolTip' : "Move dynamic properties to new group.\n\
This effectively renames a group if you move all properties.\n\
Only works with dynamic properties"}

    def getPropertiesOfGroup(self,obj,group):
        props = [p for p in obj.PropertiesList if bool(obj.getGroupOfProperty(p) == group or group == "<All groups>") and self.isDynamic(obj,p)]
        return self.getSelectedObjects(props, "Select properties to move to new group", checkAll=True)

    def Activated(self):
        doc = self.obj.Document
        selection = Gui.Selection.getSelection()
        #remove the property
        window = FreeCADGui.getMainWindow()
        items = self.getGroups(self.obj)
        if not items:
            FreeCAD.Console.PrintError(f"DynamicData::Error -- no groups of {self.obj.Label} may be renamed\n")
            return
        if len(items)==0:
            FreeCAD.Console.PrintMessage("DyanmicData: no properties.\n")
            return
        items.insert(0,"<All groups>")
        item,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Move properties to new group tool.\n\n\
This can be used to rename a group, by moving all properties to a new group.\n\
Select source group to pick properties from, or all groups to pick from all.\n', items, 0, False, windowFlags)
        if not ok:
            return
        else:
            props = self.getPropertiesOfGroup(self.obj, item)
            if props:
                toGroup = self.getGroups(self.obj,[item])
                items2 = ["<New group>"] + toGroup
                item2,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Move properties to new group tool\n\nSelect destination group\n'\
                            ,items2, 0, False, windowFlags)
                if not ok:
                    return
                if item2 == items2[0]:
                    newName,ok = QtGui.QInputDialog.getText(window, "Group name","Enter a new name for this group:",text="DefaultGroup")
                else:
                    newName = item2
                if not ok:
                    return
                doc.openTransaction("Move to new group")
                for prop in props:
                    try:
                        self.obj.setGroupOfProperty(prop, newName)
                        FreeCAD.Console.PrintMessage(f"Property {prop} move to group {newName}\n")
                    except Exception as ex:
                        FreeCAD.Console.PrintError(f"Cannot move {prop}, only dynamic properties are supported\n")
                doc.commitTransaction()
        #refresh property view
        if self.obj in selection:
            FreeCADGui.Selection.removeSelection(self.obj)
            FreeCADGui.Selection.addSelection(self.obj)
        doc.recompute()
        return

    def IsActive(self):
        if not FreeCAD.ActiveDocument:
            return False
        selection = Gui.Selection.getSelection()
        if len(selection) == 1 and self.getDynamicProperties(selection[0]) and self.getGroups(selection[0]):
            self.obj = selection[0]
            return True
        #where nothing is selected and there is only one dd object, use that object
        if len(selection) == 0:
            dds = [obj for obj in FreeCAD.ActiveDocument.Objects if hasattr(obj,"DynamicData")]
            if len(dds) == 1:
                self.obj = dds[0]
                return True
        return False
########################################################################################
# Rename a custom dynamic property

class DynamicDataRenamePropertyCommandClass(DynamicDataBaseCommandClass):
    """Rename Property Command"""
    def __init__(self):
        self.obj = None

    def GetResources(self):
        return {'Pixmap'  : '',
                'MenuText': "Re&name Property",
                'Accel'   : "Ctrl+Shift+D,N",
                'ToolTip' : "Rename a dynamic property"}

    def getProperty(self,obj):
        props = self.getDynamicProperties(obj)
        if props:
            items = props
            if len(items) == 1:
                return items[0]
            item, ok = QtGui.QInputDialog.getItem(FreeCADGui.getMainWindow(), "Rename", "Select property to rename:", items, editable=False)
            if not ok:
                return []
            return item
        else:
            FreeCAD.Console.PrintError(f"{obj.Label} has no dynamic properties to rename\n")
            return None

    def getOutExpr(self, obj, prop):
        """get the expression set for this property, if any"""
        #expr will be a list of tuples[(propname, expression)]
        expressions = obj.ExpressionEngine
        expr = ""
        for expression in expressions:
            if prop == expression[0]:
                expr = expression[1]
        return expr

    def getNewPropertyName(self, obj, prop):
        """get from user new name for this property, ensure no conflict"""
        already = [p for p in obj.PropertiesList] #already have these property names
        newName, ok = QtGui.QInputDialog.getText(FreeCADGui.getMainWindow(), "Rename", f"Enter new name for {prop}:", QtGui.QLineEdit.EchoMode.Normal, prop)
        if not ok:
            return ""
        while ok and newName in already:
            newName, ok = QtGui.QInputDialog.getText(FreeCADGui.getMainWindow(), "Rename", f"Property already exists.  Enter new name for {prop}:", QtGui.QLineEdit.EchoMode.Normal, prop)
        return newName if ok else ""

    def getInExprs(self, obj, prop):
        """get the incoming expressions bound to this property
           returns a list of tuples in the form: [(object, propertyname, expression),]
        """
        inExprs = []
        inobjs = [o for o in obj.InList]
        for inobj in inobjs:
            for expr in inobj.ExpressionEngine:
                if prop in expr[1]:
                    inExprs.append(tuple([inobj, expr[0], expr[1]]))
        return inExprs

    def Activated(self):
        doc = self.obj.Document
        prop = self.getProperty(self.obj) #string name of property
        if not prop:
            return
        outExpr = self.getOutExpr(self.obj, prop)
        if not outExpr:
            propval = getattr(self.obj, prop)
        newName = self.getNewPropertyName(self.obj, prop)
        if not newName:
            return

        inExprs = self.getInExprs(self.obj, prop)
        typeId = self.obj.getTypeIdOfProperty(prop)
        docu = self.obj.getDocumentationOfProperty(prop)
        group = self.obj.getGroupOfProperty(prop)
        doc.openTransaction(f"Rename {prop}")
        self.obj.addProperty(typeId, newName, group, docu)
        if outExpr:
            self.obj.setExpression(newName, outExpr)
        else:
            setattr(self.obj, newName, propval)
        for inExpr in inExprs:
            inExpr[0].setExpression(inExpr[1], inExpr[2].replace(prop,newName))
        self.obj.removeProperty(prop)
        doc.commitTransaction()
        if self.obj in FreeCADGui.Selection.getSelection():
            FreeCADGui.Selection.removeSelection(self.obj)
            FreeCADGui.Selection.addSelection(self.obj)
        doc.recompute()
        return

    def IsActive(self):
        if not FreeCAD.ActiveDocument:
            return False
        selection = Gui.Selection.getSelection()
        if len(selection) == 1 and self.getDynamicProperties(selection[0]):
            self.obj = selection[0]
            return True
        #where nothing is selected and there is only one dd object, use that object
        if len(selection) == 0:
            dds = [obj for obj in FreeCAD.ActiveDocument.Objects if hasattr(obj,"DynamicData")]
            if len(dds) == 1:
                self.obj = dds[0]
                return True
        return False

#Gui.addCommand("DynamicDataRenameProperty", DynamicDataRenamePropertyCommandClass())
########################################################################################
# Set the tooltip of a dynamic property

class DynamicDataSetTooltipCommandClass(DynamicDataBaseCommandClass):
    """Set Tooltip Command"""
    def __init__(self):
        self.obj = None

    def GetResources(self):
        return {'Pixmap'  : '',
                'MenuText': "Se&t Tooltip",
                'Accel'   : "Ctrl+Shift+D,T",
                'ToolTip' : "Set the tooltip of a dynamic property"}

    def getProperty(self,obj):
        props = self.getDynamicProperties(obj)
        if props:
            items = props
            if len(items) == 1:
                return items[0]
            item, ok = QtGui.QInputDialog.getItem(FreeCADGui.getMainWindow(), "Set tooltip", "Select property to set tooltip for:", items, editable=False)
            if not ok:
                return []
            return item
        else:
            FreeCAD.Console.PrintError(f"{obj.Label} has no dynamic properties whose tooltips may be set\n")

    def getNewTooltip(self, obj, prop):
        """get from user new tooltip for this property"""
        curTip = obj.getDocumentationOfProperty(prop)
        newTip, ok = QtGui.QInputDialog.getText(FreeCADGui.getMainWindow(), "Set tooltip", f"Enter new tooltip for {prop}:", QtGui.QLineEdit.EchoMode.Normal, curTip)
        if not ok:
            return curTip
        else:
            return newTip

    def Activated(self):
        doc = self.obj.Document
        prop = self.getProperty(self.obj) #string name of property
        if not prop:
            return
        docu = self.obj.getDocumentationOfProperty(prop)
        newTip = self.getNewTooltip(self.obj, prop)
        if newTip == docu:
            return
        doc.openTransaction(f"Set tooltip of {prop}")
        self.obj.setDocumentationOfProperty(prop, newTip)
        doc.commitTransaction()
        #refresh property view
        if self.obj in FreeCADGui.Selection.getSelection():
            FreeCADGui.Selection.removeSelection(self.obj)
            FreeCADGui.Selection.addSelection(self.obj)
        doc.recompute()
        return

    def IsActive(self):
        if not FreeCAD.ActiveDocument:
            return False
        selection = Gui.Selection.getSelection()
        if len(selection) == 1 and self.getDynamicProperties(selection[0]):
            self.obj = selection[0]
            return True
        #where nothing is selected and there is only one dd object, use that object
        if len(selection) == 0:
            dds = [obj for obj in FreeCAD.ActiveDocument.Objects if hasattr(obj,"DynamicData")]
            if len(dds) == 1:
                self.obj = dds[0]
                return True
        return False

#Gui.addCommand("DynamicDataSetTooltip", DynamicDataSetTooltipCommandClass())


########################################################################################
# Remove custom dynamic property


class DynamicDataRemovePropertyCommandClass(DynamicDataBaseCommandClass):
    """Remove Property Command"""

    def __init__(self):
        self.obj = None

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'RemoveProperty.svg'),
                'MenuText': "&Remove Property",
                'Accel'   : "Ctrl+Shift+D,R",
                'ToolTip' : "Remove a custom property from the DynamicData object"}

    def getProperties(self,obj):
        """get all dynamic properties, and let user select the ones to remove in a dialog"""
        props = [p for p in obj.PropertiesList if self.isDynamic(obj, p)]
        return self.getSelectedObjects(props, "Select dynamic properties to remove", checkAll=False)

    def Activated(self):
        doc = self.obj.Document
        selection = Gui.Selection.getSelection()
        #remove the property
        window = QtGui.QApplication.activeWindow()
        items = self.getProperties(self.obj)
        if len(items) == 0: #user canceled
            return
        doc.openTransaction("Remove properties")
        for item in items:
            try:
                self.obj.removeProperty(item)
            except Exception as ex:
                FreeCAD.Console.PrintError(f"DynamicData::Exception cannot remove {item}\n{ex}")
        doc.commitTransaction()
        if self.obj in selection: #refreshes property view
            FreeCADGui.Selection.removeSelection(self.obj)
            FreeCADGui.Selection.addSelection(self.obj)
        doc.recompute()
        return

    def IsActive(self):
        if not FreeCAD.ActiveDocument:
            return False
        selection = Gui.Selection.getSelection()
        if len(selection) == 1 and self.getDynamicProperties(selection[0]):
            self.obj = selection[0]
            return True
        #where nothing is selected and there is only one dd object, use that object
        if len(selection) == 0:
            dds = [obj for obj in FreeCAD.ActiveDocument.Objects if hasattr(obj,"DynamicData")]
            if len(dds) == 1:
                self.obj = dds[0]
                return True
        return False

#Gui.addCommand("DynamicDataRemoveProperty", DynamicDataRemovePropertyCommandClass())

########################################################################################
# Import aliases from spreadsheet


class DynamicDataImportAliasesCommandClass(DynamicDataBaseCommandClass):
    """Import Aliases Command"""

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'ImportAliases.svg'),
                'MenuText': "&Import Aliases",
                'ToolTip' : "Import aliases from selected spreadsheet(s) into selected dd object"}

    def Activated(self):

        doc = self.dd.Document
        selection = Gui.Selection.getSelectionEx()
        if not selection:
            return

        #sanity check
        window = QtGui.QApplication.activeWindow()
        items = ["Do the import, I know what I\'m doing","Cancel"]
        item, ok = QtGui.QInputDialog.getItem(window,'DynamicData: Sanity Check',
"""Warning: This will modify your spreadsheet.

It will import the aliases from the spreadsheet and reset them to
point to the dd object.  After the import is done you should make any changes
to the dd property rather than to the alias cell in the spreadsheet.

All imports come in as values, not as expressions.

For example: diameter=radius*2 imports as 10.0 mm, not as an expression radius*2

You should still keep your spreadsheet because other expressions referencing aliases in the
spreadsheet will still be referencing them.  The difference is now the spreadsheet cells
will be referencing the dd object.  Again, make any changes to the dd property, not to the spreadsheet.

For example:
Dependency graph:
before import: constraint -> spreadsheet
after import: constraint -> spreadsheet -> dd object

You can undo this operation using FreeCAD's Undo function, but you should probably
save your document before proceeding.""",
items, 0, False, windowFlags)
        if not ok or item == items[-1]:
            return
        doc.openTransaction("dd Import Aliases") #setup undo
        aliases=[]
        for sheet in self.sheets:
            for line in sheet.cells.Content.splitlines():
                if "<Cells Count=" in line or "</Cells>" in line:
                    continue
                if not "alias=" in line:
                    continue
                idx = line.find("alias=\"")+len("alias=\"")
                idx2 = line.find("\"",idx)
                if not line[idx:idx2][-1]=="_": #skip aliases that end in an underscore
                    aliases.append(line[idx:idx2])
                else:
                    FreeCAD.Console.PrintWarning('DynamicData: skipping alias \"'+line[idx:idx2]+'\" because it ends in an underscore (_).\n')

            for alias in aliases:
                atr = getattr(sheet,alias)
                if "Base.Quantity" in str(type(atr)):
                    #handle quantity types
                    propertyType = atr.Unit.Type #e.g. 'Length'
                    #handle inconsistencies in naming convention between unit types and property types
                    if 'Velocity' in propertyType:
                        propertyType='Speed'
                    userString = atr.UserString
                elif "'float\'" in str(type(atr)):
                    #handle float types
                    propertyType='Float'
                    userString=atr
                elif "'int\'" in str(type(atr)):
                    #handle int types (actually, just treat them as floats
                    #since many users no doubt will expect this behavior for imported aliases)
                    propertyType='Float'
                    userString=atr
                elif "unicode" in str(type(atr)) or '<class \'str\'>' in str(type(atr)):
                    #handle unicode string types
                    propertyType='String'
                    userString=atr
                else:
                    FreeCAD.Console.PrintError('DynamicData: please report: unknown property type error importing alias from spreadsheet ('+str(type(atr))+')\n')
                    continue

                name = self.fixName(alias)
                if not hasattr(self.dd, name): #avoid adding the same property again
                    self.dd.addProperty('App::Property'+propertyType, name, sheet.Label, propertyType)
                    setattr(self.dd,name,userString)
                    FreeCAD.Console.PrintMessage(f"DynamicData: adding property: {name} to {self.dd.Label}, resetting spreadsheet: \
                        {sheet.Label}.{alias} to point to {self.dd.Label}.{name}\n")
                    sheet.set(alias, f"={self.dd.Label}.{name}")
                else:
                    FreeCAD.Console.PrintWarning(f"DynamicData: skipping existing property: {name}\n")
                continue

        doc.commitTransaction()
        doc.recompute()
        if len(aliases) == 0:
            FreeCAD.Console.PrintMessage('DynamicData: No aliases found.\n')
            return
        return

    def IsActive(self):
        self.sheets = []
        self.dd = None
        selection = Gui.Selection.getSelection()
        if not selection:
            return
        self.sheets = [obj for obj in selection if obj.isDerivedFrom("Spreadsheet::Sheet")]
        dds = [obj for obj in selection if not obj in self.sheets]
        if len(dds) == 1:
            self.dd = dds[0]
        else:
            return False
        if len(self.sheets) == 0:
            return False

        return True

#Gui.addCommand("DynamicDataImportAliases", DynamicDataImportAliasesCommandClass())



########################################################################################
# Import named constraints from sketch


class DynamicDataImportNamedConstraintsCommandClass(DynamicDataBaseCommandClass):
    """Import Named Constraints Command"""

    def __init__(self):
        self.dd = None
        self.sketches = []

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'ImportNamedConstraints.svg'),
                'MenuText': "&Import Named Constraints",
                'ToolTip' : "Import named constraints from selected sketch(es) into selected dd object"}

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        # should never get here, so no need for this code -- command won't be active in these cases
        # if len(sketches)==0:
        #     #todo: handle no selected sketches.  For now, just return
        #     FreeCAD.Console.PrintMessage("DynamicData: No selected sketch(es)\n")
        #     return
        # if not self.dd:
        #     #todo: handle no dd object selected.  For now, just return
        #     FreeCAD.Console.PrintMessage("DynamicData: No selected dd object\n")
        #     return

        #sanity check
        window = QtGui.QApplication.activeWindow()
        items = ["Do the import, I know what I'm doing","Cancel"]
        item, ok = QtGui.QInputDialog.getItem(window,'DynamicData: Sanity Check',
"""Warning: This will modify your sketch.

It will import the named constraints from the sketch and reset them to
point to the dd object.  After the import is done you should make changes
to the dd object property rather than to the constraint itself.

All imports come in as values.

For example: diameter=radius*2 imports as 10.0 mm, not as an expression radius*2

For that reason, it might be necessary to rework some formulas in some cases.

This operation can be undone, but you should save your document before proceeding.""",
items, 0 , False, windowFlags)
        if not ok or item == items[-1]:
            return
        FreeCAD.ActiveDocument.openTransaction("dd Import Constraints") #setup undo
        constraints=[]
        for sketch in self.sketches:
            for con in sketch.Constraints:
                if not con.Name or con.Name[-1:]=='_': #ignore constraint names ending in underscore
                    continue
                if not con.Driving:
                    FreeCAD.Console.PrintWarning(f"\
DynamicData: Skipping reference mode constraint: {con.Name} because linking by expression would cause a cyclic \
dependency and linking by value would produce an incorrect value should the reference value change.\n")
                    continue
                constraints.append({'constraintName':con.Name,'value':con.Value,'constraintType':con.Type,'sketchLabel':sketch.Label, 'sketch':sketch})

        if len(constraints) == 0:
            FreeCAD.Console.PrintMessage('DynamicData: No named constraints found.\n')
            return

        for con in constraints:
            propertyType = "Length"
            value = con['value']
            if con['constraintType'] == 'Angle':
                propertyType = "Angle"
                value *= (180.0 / math.pi)

            name = self.fixName(con['constraintName'])
            if not self.isValidName(con['constraintName']):
                for idx,constraint in enumerate(sketch.Constraints):
                    if constraint.Name == con['constraintName']:
                        sketch.renameConstraint(idx, name)
                        FreeCAD.Console.PrintWarning(f"DynamicData: Renaming invalid constraint name: {con['constraintName']} to {name}\n")
                        break
            if not hasattr(self.dd,name): #avoid adding the same property again
                self.dd.addProperty(f"App::Property{propertyType}", name, con['sketchLabel'],f"[{propertyType}] constraint type: [{con['constraintType']}]")
                setattr(self.dd, name, value)
                FreeCAD.Console.PrintMessage(f"DynamicData: adding property: {name} to dd object\n")
                sketch = con['sketch']
                sketch.setExpression(f"Constraints.{name}", f"<<{self.dd.Label}>>.{name}")
            else:
                FreeCAD.Console.PrintWarning(f"DynamicData: skipping existing property: {name}\n")
        FreeCAD.ActiveDocument.commitTransaction()
        doc.recompute()
        return

    def IsActive(self):
        self.dd = None
        self.sketches = []
        doc = FreeCAD.ActiveDocument
        selection = Gui.Selection.getSelection()
        if not selection:
            return False
        self.sketches = [obj for obj in selection if obj.isDerivedFrom("Sketcher::SketchObject") and obj.Label[-1] != '_']
        if len(self.sketches) == 0:
            return False
        dds = [obj for obj in selection if not obj in self.sketches]
        if not len(dds) == 1:
            return False
        self.dd = dds[0]
        return True

#Gui.addCommand("DynamicDataImportNamedConstraints", DynamicDataImportNamedConstraintsCommandClass())


########################################################################################
# Copy Property To and/or From dd <--> other object


class DynamicDataCopyPropertyCommandClass(DynamicDataBaseCommandClass):
    """Copy Property Command"""
    class CopyDlg(QtGui.QDialog):
        def __init__(self, cmd, obj1, obj2):
            super(DynamicDataCopyPropertyCommandClass.CopyDlg, self).__init__(Gui.getMainWindow())
            self.setAttribute(QtCore.Qt.WA_WindowPropagation, True)
            self.setWindowTitle(f"DynamicData v{__version__} Copy / Set / Bind")
            icon = QtGui.QIcon(os.path.join(iconPath, 'CopyProperty.svg'))
            self.setWindowIcon(icon)
            self.applied = False #apply button clicked
            self.obj1 = obj1
            self.obj2 = obj2 if obj2 else obj1
            self.cmd = cmd
            self.blockSignals(True)
            self.layout = QtGui.QGridLayout()
            for ii in range(1,10):
                self.layout.setRowStretch(ii, 1)
            self.layout.setRowStretch(0, 0)
            self.setLayout(self.layout)
            label = self.obj1.Label
            name = self.obj1.Name
            same = bool(label == name)
            label = label if same else f"{label} ({name})"
            self.obj1Label = QtGui.QLabel(label)
            self.layout.addWidget(self.obj1Label, 0, 0, 1, 2)

            label = self.obj2.Label if self.obj2 else self.obj1.Label
            name = self.obj2.Name if self.obj2 else self.obj1.Name
            same = bool(label == name)
            label = label if same else f"{label} ({name})"
            self.obj2Label = QtGui.QLabel(label)
            self.layout.addWidget(self.obj2Label, 0, 3, 1, 2)

            self.obj1List = QtGui.QListWidget()
            self.obj1List.itemSelectionChanged.connect(self.updateStatus)
            self.layout.addWidget(self.obj1List, 1, 0, 9, 2)
            self.obj2List = QtGui.QListWidget()
            self.obj2List.itemSelectionChanged.connect(self.updateStatus)
            self.layout.addWidget(self.obj2List, 1, 3, 9, 2)
            self.fillUpList(self.obj1, self.obj1List, 1)
            self.fillUpList(self.obj2, self.obj2List, 2)

            self.btnGroup = QtGui.QButtonGroup()
            self.btnGroup.buttonClicked.connect(self.radioBtnClicked)
            self.copyRightBtn = QtGui.QRadioButton("Copy ->")
            self.copyRightBtn.setChecked(True)
            self.btnGroup.addButton(self.copyRightBtn)
            self.copyRightBtn.setToolTip(f"""
Arrow points in direction of data flow.
Creates copy of selected property in {self.obj1.Label} -> to new property of same type in {self.obj2.Label}""")
            self.copyRightBtn.setObjectName("copyRightBtn")
            self.layout.addWidget(self.copyRightBtn, 1, 2, 1, 1)
            self.copyLeftBtn = QtGui.QRadioButton("<- Copy")
            self.btnGroup.addButton(self.copyLeftBtn)
            self.copyLeftBtn.setToolTip(f"""
Arrow points in direction of data flow.
Creates new property in {self.obj1.Label} <- from selected property of {self.obj2.Label}""")
            self.copyLeftBtn.setObjectName("copyLeftBtn")
            self.layout.addWidget(self.copyLeftBtn, 2, 2, 1, 1)

            self.setRightBtn = QtGui.QRadioButton("Set ->")
            self.btnGroup.addButton(self.setRightBtn)
            self.setRightBtn.setToolTip(f"""
Arrow points in direction of data flow.
Sets selected existing property in {self.obj2.Label} to value of selected property in {self.obj1.Label}""")
            self.setRightBtn.setObjectName("setRightBtn")
            self.layout.addWidget(self.setRightBtn, 3, 2, 1, 1)
            self.setLeftBtn = QtGui.QRadioButton("<- Set")
            self.btnGroup.addButton(self.setLeftBtn)
            self.setLeftBtn.setToolTip(f"Sets selected existing property in {self.obj1.Label} to value of selected property in {self.obj2.Label}")
            self.setLeftBtn.setObjectName("setLeftBtn")
            self.layout.addWidget(self.setLeftBtn, 4, 2, 1, 1)

            self.bindRightBtn = QtGui.QRadioButton("Bind to ->")
            self.btnGroup.addButton(self.bindRightBtn)
            self.bindRightBtn.setToolTip(f"""
Arrow points in direction of binding, left is bound to right.
Bind selected property of {self.obj1.Label} to selected property of {self.obj2.Label} via Expressions""")
            self.bindRightBtn.setObjectName("bindRightBtn")
            self.layout.addWidget(self.bindRightBtn, 5, 2, 1, 1)
            self.bindLeftBtn = QtGui.QRadioButton("<- Bind to")
            self.btnGroup.addButton(self.bindLeftBtn)
            self.bindLeftBtn.setToolTip(f"""
Arrow points in direction of binding, right is bound to left.
Bind selected property of {self.obj2.Label} to selected property of {self.obj1.Label} via Expressions""")
            self.bindLeftBtn.setObjectName("bindLeftBtn")
            self.layout.addWidget(self.bindLeftBtn, 6, 2, 1, 1)

            self.breakBindRightBtn = QtGui.QRadioButton("Break binding ->")
            self.btnGroup.addButton(self.breakBindRightBtn)
            self.breakBindRightBtn.setToolTip(f"""
Arrow points to object being affected.
Break expression binding for selected property of {self.obj2.Label}""")
            self.breakBindRightBtn.setObjectName("breakBindRightBtn")
            self.layout.addWidget(self.breakBindRightBtn, 7, 2, 1, 1)
            self.breakBindLeftBtn = QtGui.QRadioButton("<- Break binding")
            self.btnGroup.addButton(self.breakBindLeftBtn)
            self.breakBindLeftBtn.setToolTip(f"""
Arrow points to object being affected.
Break expression binding for selected property of {self.obj1.Label}""")
            self.breakBindLeftBtn.setObjectName("breakBindLeftBtn")
            self.layout.addWidget(self.breakBindLeftBtn, 8, 2, 1, 1)

            self.statusLabel = QtGui.QLabel()
            self.statusLabel.setToolTip("Messages go here: blue text = normal message, red text = critical error in proposed action.")
            self.layout.addWidget(self.statusLabel, 11, 0, 2, 5)

            self.buttons = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Ok.__or__(QtGui.QDialogButtonBox.Cancel),
                QtCore.Qt.Horizontal, self)
            self.applyBtn = QtGui.QPushButton("Apply")
            self.buttons.addButton(self.applyBtn, QtGui.QDialogButtonBox.ApplyRole)
            self.buttons.accepted.connect(self.accept)
            self.buttons.rejected.connect(self.reject)
            self.applyBtn.clicked.connect(self.apply)
            self.layout.addWidget(self.buttons, 14, 0, 1, 3)
            self.blockSignals(False)
            self.updateStatus()

        @property
        def Obj1Item(self):
            """currently selected item, might be None"""
            return self.obj1List.currentItem()

        @property
        def Obj2Item(self):
            """currently selected item, might be None"""
            return self.obj2List.currentItem()

        @property
        def Obj1IsView(self):
            """boolean, true if obj1 selected property is a view property"""
            item = self.Obj1Item
            if not item:
                return False
            txt = item.text()
            return txt.startswith("(view) ")

        @property
        def Obj2IsView(self):
            """boolean, true if obj2 selected property is a view property"""
            item = self.Obj2Item
            if not item:
                return False
            txt = item.text()
            return txt.startswith("(view) ")

        @property
        def Obj1PropName(self):
            """property name selected in left list"""
            item = self.Obj1Item
            if not item:
                return None
            txt = item.text()
            if txt.startswith("(view) "):
                return txt[7:]
            else:
                return txt

        @property
        def Obj2PropName(self):
            """property name selected in right list"""
            item = self.Obj2Item
            if not item:
                return None
            txt = item.text()
            if txt.startswith("(view) "):
                return txt[7:]
            else:
                return txt

        @property
        def Obj1Group(self):
            """group of the currently selected property"""
            item = self.Obj1Item
            if not item:
                return None
            if self.Obj1IsView:
                obj = self.obj1.ViewObject
            else:
                obj = self.obj1
            grp = obj.getGroupOfProperty(self.Obj1PropName)
            return grp if grp else "Base"

        @property
        def Obj2Group(self):
            """group of the currently selected property"""
            item = self.Obj2Item
            if not item:
                return None
            if self.Obj2IsView:
                obj = self.obj2.ViewObject
            else:
                obj = self.obj2
            grp = obj.getGroupOfProperty(self.Obj2PropName)
            return grp if grp else "Base"

        @property
        def Obj1Value(self):
            """value of selected property"""
            item = self.Obj1Item
            if not item:
                return None
            if not self.Obj1IsView:
                return getattr(self.obj1, self.Obj1PropName)
            else:
                try:
                    return getattr(self.obj1.ViewObject, self.Obj1PropName)
                except:
                    return "No python counterpart"

        @property
        def Obj2Value(self):
            """value of selected property"""
            item = self.Obj2Item
            if not item:
                return None
            if not self.Obj2IsView:
                return getattr(self.obj2, self.Obj2PropName)
            else:
                try:
                    return getattr(self.obj2.ViewObject, self.Obj2PropName)
                except:
                    return "No python counterpart"

        @property
        def Obj1Type(self):
            """type id of selected property, with 'App::Property' prefix"""
            item = self.Obj1Item
            if not item:
                return None
            if not self.Obj1IsView:
                return self.obj1.getTypeIdOfProperty(self.Obj1PropName)
            else:
                return self.obj1.ViewObject.getTypeIdOfProperty(self.Obj1PropName)

        @property
        def Obj2Type(self):
            """type id of selected property, with 'App::Property' prefix"""
            item = self.Obj2Item
            if not item:
                return None
            if not self.Obj2IsView:
                return self.obj2.getTypeIdOfProperty(self.Obj2PropName)
            else:
                return self.obj2.ViewObject.getTypeIdOfProperty(self.Obj2PropName)

        @property
        def Obj1Expression(self):
            """expression engine value for this property, if any"""
            item = self.Obj1Item
            if not item:
                return None
            if self.Obj1IsView:
                return None
            expr = self.obj1.ExpressionEngine
            exp_dict = {xp[0]:xp[1] for xp in expr}
            if self.Obj1PropName in exp_dict:
                return exp_dict[self.Obj1PropName]
            else:
                return None

        @property
        def Obj2Expression(self):
            """expression engine value for this property, if any"""
            item = self.Obj2Item
            if not item:
                return None
            if self.Obj2IsView:
                return None
            expr = self.obj2.ExpressionEngine
            exp_dict = {xp[0]:xp[1] for xp in expr}
            if self.Obj2PropName in exp_dict:
                return exp_dict[self.Obj2PropName]
            else:
                return None

        @property
        def Obj1Tip(self):
            """documentation of property, tooltip shown"""
            item = self.Obj1Item
            if not item:
                return None
            if not self.Obj1IsView:
                return self.obj1.getDocumentationOfProperty(self.Obj1PropName)
            else:
                return self.obj1.ViewObject.getDocumentationOfProperty(self.Obj1PropName)

        @property
        def Obj2Tip(self):
            """documentation of property, tooltip shown"""
            item = self.Obj2Item
            if not item:
                return None
            if not self.Obj2IsView:
                return self.obj2.getDocumentationOfProperty(self.Obj2PropName)
            else:
                return self.obj2.ViewObject.getDocumentationOfProperty(self.Obj2PropName)

        def radioBtnClicked(self, button):
            #print(f"radio button clicked = {button.objectName()}")
            self.updateStatus()

        def updateStatus(self):
            """updates the status label to give a preview of the action to be performed"""
            if not hasattr(self, "btnGroup"):
                return #not fully initialized yet
            vobj1 = "" if not self.Obj1IsView else ".ViewObject"
            vobj2 = "" if not self.Obj2IsView else ".ViewObject"

            cyclicMatch1 = bool(self.obj2 in self.obj1.InListRecursive) #if true, obj2 depends on obj1, so obj1 cannot bind to obj2
            cyclicMatch2 = bool(self.obj1 in self.obj2.InListRecursive)
            cyclicMsg1 = f"\nCircular dependency because {self.obj2.Label} already depends on {self.obj1.Label}." if cyclicMatch1 else ""
            cyclicMsg2 = f"\nCircular dependency because {self.obj1.Label} already depends on {self.obj2.Label}." if cyclicMatch2 else ""

            typeMismatch = bool(self.Obj1Type != self.Obj2Type)
            typeMsg = f"\nType mismatch detected: {self.Obj1Type} and {self.Obj2Type}" if typeMismatch else ""
            typeClr = ["blue","red"][int(typeMismatch)]
            typeClr1 = ["blue","red"][int(typeMismatch or cyclicMatch1)]
            typeClr2 = ["blue","red"][int(typeMismatch or cyclicMatch2)]

            cyclicMatch1 = bool(self.obj2 in self.obj1.InListRecursive) #if true, obj2 depends on obj1, so obj1 cannot bind to obj2
            cyclicMatch2 = bool(self.obj1 in self.obj2.InListRecursive)
            cyclicMsg1 = f"\nCircular dependency because {self.obj2.Label} already depends on {self.obj1.Label}." if cyclicMatch1 else ""
            cyclicMsg2 = f"\nCircular dependency because {self.obj1.Label} already depends on {self.obj2.Label}." if cyclicMatch2 else ""
            cyclicClr1 = ["blue","red"][int(cyclicMatch1 or typeMismatch)]
            cyclicClr2 = ["blue","red"][int(cyclicMatch2 or typeMismatch)]

            copyLeftMsg = (f"Copy {self.obj2.Label}{vobj2}.{self.Obj2PropName} to a new property in {self.obj1.Label}","blue")
            copyRightMsg = (f"Copy {self.obj1.Label}{vobj1}.{self.Obj1PropName} to a new property in {self.obj2.Label}","blue")
            setLeftMsg = (f"Set {self.obj1.Label}{vobj1}.{self.Obj1PropName} to value of {self.obj2.Label}{vobj2}.{self.Obj2PropName}{typeMsg}",typeClr)
            setRightMsg = (f"Set {self.obj2.Label}{vobj2}.{self.Obj2PropName} to value of {self.obj1.Label}{vobj1}.{self.Obj1PropName}{typeMsg}",typeClr)
            if not vobj2:
                bindLeftMsg = (f"Bind {self.obj2.Label}.{self.Obj2PropName} to {self.obj1.Label}.{self.Obj1PropName}{typeMsg}{cyclicMsg2}",typeClr2)
            else:
                bindLeftMsg = (f"Cannot bind {self.obj2.Label}{vobj2}.{self.Obj2PropName} because it is a view object property.{typeMsg}","red")
            if not vobj1:
                bindRightMsg = (f"Bind {self.obj1.Label}.{self.Obj1PropName} to {self.obj2.Label}.{self.Obj2PropName}{typeMsg}{cyclicMsg1}",typeClr1)
            else:
                bindRightMsg = (f"Cannot bind {self.obj1.Label}{vobj1}.{self.Obj1PropName} because it is a view object property.","red")
            if self.Obj1Expression:
                breakBindLeftMsg = (f"Break binding of {self.obj1.Label}.{self.Obj1PropName}.","blue")
            else:
                breakBindLeftMsg = (f"No expression binding to break for {self.obj1.Label}.{self.Obj1PropName}.","red")
            if self.Obj1IsView:
                breakBindLeftMsg = (breakBindLeftMsg[0] + "\nView objects cannot be bound or unbound via expressions", "red")
            if self.Obj2Expression:
                breakBindRightMsg = (f"Break binding of {self.obj2.Label}.{self.Obj2PropName}.","blue")
            else:
                breakBindRightMsg = (f"No expression binding to break for {self.obj2.Label}.{self.Obj2PropName}.","red")
            if self.Obj2IsView:
                breakBindRightMsg = (breakBindRightMsg[0] + "\nView objects cannot be bound or unbound via expressions", "red")

            msg_map = {
                "copyLeftBtn" : copyLeftMsg,
                "copyRightBtn" : copyRightMsg,
                "setLeftBtn" : setLeftMsg,
                "setRightBtn" : setRightMsg,
                "bindLeftBtn" : bindLeftMsg,
                "bindRightBtn" : bindRightMsg,
                "breakBindLeftBtn" : breakBindLeftMsg,
                "breakBindRightBtn" : breakBindRightMsg,
            }
            radioBtn = self.btnGroup.checkedButton()
            msgTuple = msg_map[radioBtn.objectName()]
            self.statusLabel.setStyleSheet(f"color:{msgTuple[1]};")
            self.statusLabel.setText(msgTuple[0])

        def getNewPropertyName(self, obj, candidate):
            """When creating a new property and already there is a property with that
            same name, we can ask the user for a preferred new property name"""
            if not hasattr(obj, candidate):
                return candidate

            # Use regular expression to extract base name and number
            match = re.match(r'^(.*?)(\d*)$', candidate)
            base_name, number_suffix = match.groups() if match else (candidate, '')
            idx = int(number_suffix) if number_suffix else 1

            while hasattr(obj, f"{base_name}{idx}"):
                idx += 1

            new_candidate = f"{base_name}{idx}"

            new_name, ok = QtGui.QInputDialog.getText(self, "Attribute already exists", "Enter name for new property: ", text=new_candidate)
            if not new_name or not ok:
                return None

            return new_name
        def copyLeft(self):
            """copy the selected property from the list on the right to the object (self.obj1) on the left
            returns None if user aborts, False if there was some error, True on success
            """
            propName = self.getNewPropertyName(self.obj1, self.Obj2PropName)
            if not propName:
               return None
            try:
                self.obj1.addProperty(self.Obj2Type, propName, self.Obj2Group, self.Obj2Tip)
            except:
                FreeCAD.Console.PrintError(f"DynamicData: Error adding {propName} to {self.obj1.Label}")
                return False
            try:
                setattr(self.obj1, propName, self.Obj2Value)
                return True
            except:
                FreeCAD.Console.PrintError(f"DynamicData: Error setting {propName} to {self.Obj2Value}, but property was created.\n")
                return False

        def copyRight(self):
            """copy the selected property from the list on the left to the object (self.obj2) on the right
            returns None if user aborts, False if there was some error, True on success
            """
            propName = self.getNewPropertyName(self.obj2, self.Obj1PropName)
            if not propName:
               return None

            try:
                self.obj2.addProperty(self.Obj1Type, propName, self.Obj1Group, self.Obj1Tip)
            except:
                FreeCAD.Console.PrintError(f"DynamicData: Error adding {propName} to {self.obj2.Label}")
                return False
            try:
                setattr(self.obj2, propName, self.Obj1Value)
                return True
            except:
                FreeCAD.Console.PrintError(f"DynamicData: Error setting {propName} to {self.Obj1Value}, but property was created.\n")
                return False

        def setLeft(self):
            """sets an existing property of self.obj1 to the same value of selected property in right side list"""
            #first check that the property types are a match
            if self.Obj1Type != self.Obj2Type:
                FreeCAD.Console.PrintError(f"""
DynamicData: Type mismatch: {self.obj2.Label}.{self.Obj2PropName} is type {self.Obj2Type}
while {self.obj1.Label}.{self.Obj1PropName} is type {self.Obj1Type}""")
                return False
            #now check to see if the property is bound by an expression already
            if self.Obj1Expression:
                FreeCAD.Console.PrintWarning(f"""
DynamicData warning: {self.obj1.Label}.{self.Obj1PropName} was bound by an expression:\n{self.Obj1Expression}\nbut it has now been cleared.""")
                self.obj1.setExpression(self.Obj1PropName, None)
            try:
                if not self.Obj2IsView:
                    setattr(self.obj1, self.Obj1PropName, self.Obj2Value)
                else:
                    setattr(self.obj1.ViewObject, self.Obj1PropName, self.Obj2Value)
                return True
            except Exception as e:
                FreeCAD.Console.PrintError(f"DynamicData: error {e} setting {self.obj1.Label}.{self.Obj1PropName} to {self.Obj2Value}\n")
                return False

        def setRight(self):
            """sets an existing property of self.obj2 to the same value of selected property in left side list"""
            #first check that the property types are a match
            if self.Obj1Type != self.Obj2Type:
                FreeCAD.Console.PrintError(f"""
DynamicData: Type mismatch: {self.obj2.Label}.{self.Obj2PropName} is type {self.Obj2Type}
while {self.obj1.Label}.{self.Obj1PropName} is type {self.Obj1Type}""")
                return False
            #now check to see if the property is bound by an expression already
            if self.Obj2Expression:
                FreeCAD.Console.PrintWarning(f"""
DynamicData warning: {self.obj2.Label}.{self.Obj2PropName} was bound by an expression:\n{self.Obj2Expression}\nbut it has now been cleared.""")
                self.obj2.setExpression(self.Obj2PropName, None)
            try:
                if not self.Obj1IsView:
                    setattr(self.obj2, self.Obj2PropName, self.Obj1Value)
                else:
                    setattr(self.obj2.ViewObject, self.Obj2PropName, self.Obj1Value)
                return True
            except Exception as e:
                FreeCAD.Console.PrintError(f"DynamicData: error {e} setting {self.obj2.Label}.{self.Obj2PropName} to {self.Obj1Value}\n")
                return False

        def bindRight(self):
            """bind to the property on the right"""
            #check for a type mismatch
            if self.Obj1Type != self.Obj2Type:
                FreeCAD.Console.PrintError(f"""
DynamicData error: Type mismatch.  {self.obj1.Label}.{self.Obj1PropName} is type {self.Obj1Type} where
{self.obj2.Label}.{self.Obj2PropName} is type {self.Obj2Type}""")
                return False
            # check for cyclic dependency
            # objects in obj.InList and obj.InListRecursive are dependent on obj
            # since this command binds a property of obj1 to obj2 we must check
            # to see if obj2 is in obj1's inlist
            if self.obj2 in self.obj1.InListRecursive:
                FreeCAD.Console.PrintError(f"""
DynamicData error: Cannot bind  {self.obj1.Label}.{self.Obj1PropName} to {self.obj2.Label}.{self.Obj2PropName}
because this would create a cyclic dependency.""")
                return False
            if self.Obj1IsView:
                FreeCAD.Console.PrintError(f"""
DynamicData error: {self.obj1.Label}.ViewObject.{self.Obj1PropName} is a view object expression,
which cannot be bound by expression.\n""")
                return False
            FreeCAD.Console.PrintMessage(f"""
DynamicData: binding {self.obj1.Label}.{self.Obj1PropName} to {self.obj2.Label}.{self.Obj2PropName}""")
            self.obj1.setExpression(self.Obj1PropName, f"{self.obj2.Name}.{self.Obj2PropName}")
            return True

        def bindLeft(self):
            """bind to the property selected on the left"""
            #check for a type mismatch
            if self.Obj2Type != self.Obj1Type:
                FreeCAD.Console.PrintError(f"""
DynamicData error: Type mismatch.  {self.obj2.Label}.{self.Obj2PropName} is type {self.Obj2Type} where
{self.obj1.Label}.{self.Obj1PropName} is type {self.Obj1Type}""")
                return False
            # check for cyclic dependency
            # objects in obj.InList and obj.InListRecursive are dependent on obj
            # since this command binds a property of obj2 to obj1 we must check
            # to see if obj1 is in obj2's inlist
            if self.obj1 in self.obj2.InListRecursive:
                FreeCAD.Console.PrintError(f"""
DynamicData error: Cannot bind  {self.obj2.Label}.{self.Obj2PropName} to {self.obj1.Label}.{self.Obj1PropName}
because this would create a cyclic dependency.""")
                return False
            if self.Obj2IsView:
                FreeCAD.Console.PrintError(f"""
DynamicData error: {self.obj2.Label}.ViewObject.{self.Obj2PropName} is a view object expression,
which cannot be bound by expression.\n""")
                return False
            FreeCAD.Console.PrintMessage(f"""
DynamicData: binding {self.obj2.Label}.{self.Obj2PropName} to {self.obj1.Label}.{self.Obj1PropName}""")
            self.obj2.setExpression(self.Obj2PropName, f"{self.obj1.Name}.{self.Obj1PropName}")
            return True

        def breakBindLeft(self):
            """Clears the expression binding the property on the left that is bound to the property on the right"""
            # check if the property on the left is already bound or not
            # if it's not bound by an expression, then the user might have selected the wrong
            # radio button by mistake, so alert to the error and return
            if not self.Obj1Expression:
                FreeCAD.Console.PrintError(f"""
DynamicData error: {self.obj1.Label}.{self.Obj1PropName} is not bound by an expression.\n""")
                return False
            if self.Obj2IsView:
                FreeCAD.Console.PrintError(f"""
DynamicData error: {self.obj2.Label}.ViewObject.{self.Obj2PropName} is a view object expression,
which cannot be bound by expression.\n""")
                return False
            self.obj1.setExpression(self.Obj1PropName, None)
            return True

        def breakBindRight(self):
            """Clears the expression binding the property on the right that is bound to the property on the left"""
            # check if the property on the right is already bound or not
            # if it's not bound by an expression, then the user might have selected the wrong
            # radio button by mistake, so alert to the error and return
            if not self.Obj2Expression:
                FreeCAD.Console.PrintError(f"""
DynamicData error: {self.obj2.Label}.{self.Obj2PropName} is not bound by an expression.\n""")
                return False
            #check if this is a view object property, which cannot be bound by expression
            if self.Obj2IsView:
                FreeCAD.Console.PrintError(f"""
DynamicData error: {self.obj2.Label}.ViewObject.{self.Obj2PropName} is a view object expression,
which cannot be bound by expression.\n""")
                return False
            self.obj2.setExpression(self.Obj2PropName, None)
            return True


        def fillUpList(self, obj, objList, idx):
            pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")
            supportViewObjectProperties = pg.GetBool('SupportViewObjectProperties', False)
            blacklist = ["ExpressionEngine","Proxy","Shape","DynamicData"]
            props = self.cmd.getAllProperties(obj, supportViewObjectProperties, blacklist)
            for prop in props:
                item = QtGui.QListWidgetItem(prop)
                objList.addItem(item)
                objList.setCurrentItem(item)
                if idx == 1:
                    tip = f"[{self.Obj1Type}]\nGroup: {self.Obj1Group}\nTooltip: {self.Obj1Tip}\nvalue: {self.Obj1Value}\nExpr: {self.Obj1Expression}"
                elif idx == 2:
                    tip = f"[{self.Obj2Type}]\nGroup: {self.Obj2Group}\nTooltip: {self.Obj2Tip}\nvalue: {self.Obj2Value}\nExpr: {self.Obj2Expression}"
                item.setToolTip(tip)
            if props:
                objList.setCurrentRow(0)

        def accept(self):
            func_map = {
                "copyLeftBtn" : self.copyLeft,
                "copyRightBtn" : self.copyRight,
                "setLeftBtn" : self.setLeft,
                "setRightBtn" : self.setRight,
                "bindLeftBtn" : self.bindLeft,
                "bindRightBtn" : self.bindRight,
                "breakBindLeftBtn" : self.breakBindLeft,
                "breakBindRightBtn" : self.breakBindRight,
            }
            radioBtn = self.btnGroup.checkedButton()
            if radioBtn:
                func = func_map.get(radioBtn.objectName())
                self.obj1.Document.openTransaction(f"DynamicData: {func.__name__}")
                retval = func()
                if retval == None: #user aborted
                    self.obj1.Document.abortTransaction()
                    FreeCAD.Console.PrintMessage(f"DynamicData: {func.__name__} aborted by user\n")
                elif retval == False: #error, but already reported in func(), so don't repeat it here
                    self.obj1.Document.abortTransaction()
                else:
                    self.obj1.Document.commitTransaction()

            super().accept()

        def reject(self):
            print("rejected")
            super().reject()

        def apply(self):
            self.applied = True
            self.accept()

        ### end of CopyDlg class definition

    def __init__(self):
        self.obj1 = None
        self.obj2 = None

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'CopyProperty.svg'),
                'MenuText': "C&opy Property",
                'ToolTip' : "Copy/Set property values between selected objects"}


    def Activated(self):
        dlg = self.doDlg()
        while dlg.applied:
            dlg.deleteLater()
            dlg = self.doDlg()
        dlg.deleteLater()
        self.obj1.Document.recompute()

    def doDlg(self):
        dlg = DynamicDataCopyPropertyCommandClass.CopyDlg(self, self.obj1, self.obj2)
        dlg.exec_()
        return dlg

    def IsActive(self):
        self.obj1 = None
        self.obj2 = None
        selection = Gui.Selection.getSelection()
        if not selection:
            return False
        if len(selection) == 1:
            self.obj1 = selection[0]
            return True
        if len(selection) == 2:
            self.obj1 = selection[0]
            self.obj2 = selection[1]
            return True
        return False


Gui.addCommand("DynamicDataCreateObject", DynamicDataCreateObjectCommandClass())
Gui.addCommand("DynamicDataAddProperty", DynamicDataAddPropertyCommandClass())
Gui.addCommand("DynamicDataRemoveProperty", DynamicDataRemovePropertyCommandClass())
Gui.addCommand("DynamicDataEditEnumeration",DynamicDataEditEnumerationCommandClass())
Gui.addCommand("DynamicDataCreateConfiguration", DynamicDataCreateConfigurationCommandClass())
Gui.addCommand("DynamicDataMoveToNewGroup", DynamicDataMoveToNewGroupCommandClass())
Gui.addCommand("DynamicDataImportNamedConstraints", DynamicDataImportNamedConstraintsCommandClass())
Gui.addCommand("DynamicDataImportAliases", DynamicDataImportAliasesCommandClass())
Gui.addCommand("DynamicDataRenameProperty",DynamicDataRenamePropertyCommandClass())
Gui.addCommand("DynamicDataSetTooltip",DynamicDataSetTooltipCommandClass())
Gui.addCommand("DynamicDataSettings", DynamicDataSettingsCommandClass())
Gui.addCommand("DynamicDataCopyProperty", DynamicDataCopyPropertyCommandClass())

