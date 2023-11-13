# -*- coding: utf-8 -*-
###################################################################################
#
#  DynamicDataCmd.py
#
#  Copyright 2018-2019 Mark Ganson <TheMarkster> mwganson at gmail
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
__date__    = "2023.11.12"
__version__ = "2.54"
version = 2.54
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


def initialize():

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

propertyTypes =[
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
#    "Material",
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
    "Speed",
    "String",
    "StringList",
    "Vector",
    "VectorList",
    "VectorDistance",
    "Volume"]

nonLinkableTypes=[ #cannot be linked with setExpresion()
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
    #"Material",
    "MaterialList",
    "Matrix",
    "Path",
    "PlacementLink",
    "String",
    "StringList",
    "VectorList"]

xyzTypes = [#x,y,z elements must be linked separately
    "Direction",
    "Position",
    "Vector",
    "VectorDistance"]

#######################################################################################
# Keep Toolbar active even after leaving workbench

class DynamicDataSettingsCommandClass(object):
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

class DynamicDataCreateObjectCommandClass(object):
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

class DynamicDataCreateConfigurationCommandClass(object):
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
        return False


#Gui.addCommand("DynamicDataCreateConfiguration", DynamicDataCreateConfigurationCommandClass())


####################################################################################
# Edit an existing Enumeration property

class DynamicDataEditEnumerationCommandClass(object):
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


class DynamicDataAddPropertyCommandClass(object):
    """Add Property Command"""
    global mostRecentTypes
    global mostRecentTypesLength

    def __init__(self):
        self.obj = None

    def getPropertyTypes(self):
        return propertyTypes

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
        items = self.getPropertyTypes()
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

        vBoxLayout = QtGui.QVBoxLayout(self)
        vBoxLayout.addWidget(QtGui.QLabel(label))
        self.all = QtGui.QCheckBox("All")
        #self.all.setCheckState(QtCore.Qt.Checked) #set by caller
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
            scrollingLayout.addWidget(self.checkBoxes[-1])
        vBoxLayout.addWidget(buttons)

    def allStateChanged(self, arg):
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


########################################################################################
# Rename group


class DynamicDataMoveToNewGroupCommandClass(object):
    """Move properties to new group"""

    def GetResources(self):
        return {'Pixmap'  : "",
                'MenuText': "Move to new &group",
                'Accel'   : "Ctrl+Shift+D,G",
                'ToolTip' : "Move dynamic properties to new group.\n\
This effectively renames a group if you move all properties.\n\
Only works with dynamic properties"}

    def getGroups(self,obj,skipList=[]):
        props = [p for p in obj.PropertiesList if obj.getPropertyStatus(p) == [21]]
        groups = []
        for prop in props:
            group = obj.getGroupOfProperty(prop)
            if group and not group in groups and not group in skipList:
                groups.append(group)
        return groups

    def isDynamic(self,obj,prop):
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

    def getPropertiesOfGroup(self,obj,group):
        props = [p for p in obj.PropertiesList if bool(obj.getGroupOfProperty(p) == group or group == "<All groups>") and self.isDynamic(obj,p)]
        if props:
            dlg = SelectObjects(props,"Select properties to move to new group")
            dlg.all.setCheckState(QtCore.Qt.Checked)
            ok = dlg.exec_()
            if not ok:
                return []
        return dlg.selected

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        selection = Gui.Selection.getSelection()
        obj = self.obj
        #remove the property
        window = FreeCADGui.getMainWindow()
        items = self.getGroups(obj)
        if not items:
            FreeCAD.Console.PrintError(f"DynamicData::Error -- no groups of {obj.Label} may be renamed\n")
            return
        if len(items)==0:
            FreeCAD.Console.PrintMessage("DyanmicData: no properties.\n")
            return
        items.insert(0,"<All groups>")
        item,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Move properties to new group tool.\n\n\
This can be used to rename a group, by moving all properties to a new group.\n\
Select source group to pick properties from, or all groups to pick from all.\n',items,0,False,windowFlags)
        if not ok:
            return
        else:
            props = self.getPropertiesOfGroup(obj,item)
            if props:
                toGroup = self.getGroups(obj,[item])
                items2 = ["<New group>"] + toGroup
                item2,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Move properties to new group tool\n\nSelect destination group\n',items2,0,False,windowFlags)
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
                        obj.setGroupOfProperty(prop,newName)
                        FreeCAD.Console.PrintMessage(f"Property {prop} move to group {newName}\n")
                    except Exception as ex:
                        FreeCAD.Console.PrintError(f"Cannot move {prop}, only dynamic properties are supported\n")
                doc.commitTransaction()
        if obj in selection:
            FreeCADGui.Selection.removeSelection(obj)
            FreeCADGui.Selection.addSelection(obj)
        doc.recompute()
        return

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
########################################################################################
# Rename a custom dynamic property

class DynamicDataRenamePropertyCommandClass(object):
    """Rename Property Command"""
    def __init__(self):
        self.obj = None

    def GetResources(self):
        return {'Pixmap'  : '',
                'MenuText': "Re&name Property",
                'Accel'   : "Ctrl+Shift+D,N",
                'ToolTip' : "Rename a dynamic property"}

    def getDynamicProperties(self, obj):
        props = [p for p in obj.PropertiesList if self.isDynamic(obj,p)]
        return props

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
            FreeCAD.Console.PrintError(f"{obj.Label} has no dynamic properties\n")

    def isDynamic(self, obj, prop):
        if prop == "DynamicData":
            return False
        isSo = False
        try:
            oldGroup = obj.getGroupOfProperty(prop)
            obj.setGroupOfProperty(prop, "test")
            obj.setGroupOfProperty(prop, oldGroup)
            isSo = True
        except:
            isSo = False
        return isSo

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
        doc = FreeCAD.ActiveDocument
        obj = self.obj
        prop = self.getProperty(obj) #string name of property
        if not prop:
            return
        outExpr = self.getOutExpr(obj, prop)
        if not outExpr:
            propval = getattr(obj, prop)
        newName = self.getNewPropertyName(obj, prop)
        if not newName:
            return
        if not "dd" in newName[:2] or bool(newName[2:3] < "A" or newName[2:3] > "Z"):
            FreeCAD.Console.PrintWarning("Not all dd commands will function properly if you don't follow the dd naming convention of ddUppercase\n")
        inExprs = self.getInExprs(obj, prop)
        typeId = obj.getTypeIdOfProperty(prop)
        docu = obj.getDocumentationOfProperty(prop)
        group = obj.getGroupOfProperty(prop)
        obj.Document.openTransaction(f"Rename {prop}")
        obj.addProperty(typeId, newName, group, docu)
        if outExpr:
            obj.setExpression(newName, outExpr)
        else:
            setattr(obj, newName, propval)
        for inExpr in inExprs:
            inExpr[0].setExpression(inExpr[1], inExpr[2].replace(prop,newName))
        obj.removeProperty(prop)
        obj.Document.commitTransaction()
        if obj in FreeCADGui.Selection.getSelection():
            FreeCADGui.Selection.removeSelection(obj)
            FreeCADGui.Selection.addSelection(obj)
        doc.recompute()
        return

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

#Gui.addCommand("DynamicDataRenameProperty", DynamicDataRenamePropertyCommandClass())
########################################################################################
# Set the tooltip of a dynamic property

class DynamicDataSetTooltipCommandClass(object):
    """Set Tooltip Command"""
    def __init__(self):
        self.obj = None

    def GetResources(self):
        return {'Pixmap'  : '',
                'MenuText': "Se&t Tooltip",
                'Accel'   : "Ctrl+Shift+D,T",
                'ToolTip' : "Set the tooltip of a dynamic property"}

    def getDynamicProperties(self, obj):
        props = [p for p in obj.PropertiesList if self.isDynamic(obj,p)]
        return props

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
            FreeCAD.Console.PrintError(f"{obj.Label} has no dynamic properties\n")

    def isDynamic(self, obj, prop):
        if prop == "DynamicData":
            return False
        isSo = False
        try:
            oldGroup = obj.getGroupOfProperty(prop)
            obj.setGroupOfProperty(prop, "test")
            obj.setGroupOfProperty(prop, oldGroup)
            isSo = True
        except:
            isSo = False
        return isSo

    def getNewTooltip(self, obj, prop):
        """get from user new tooltip for this property"""
        curTip = obj.getDocumentationOfProperty(prop)
        newTip, ok = QtGui.QInputDialog.getText(FreeCADGui.getMainWindow(), "Set tooltip", f"Enter new tooltip for {prop}:", QtGui.QLineEdit.EchoMode.Normal, curTip)
        if not ok:
            return curTip
        else:
            return newTip

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        obj = self.obj
        prop = self.getProperty(obj) #string name of property
        if not prop:
            return
        docu = obj.getDocumentationOfProperty(prop)
        newTip = self.getNewTooltip(obj, prop)
        if newTip == docu:
            return
        obj.Document.openTransaction(f"Set tooltip of {prop}")
        obj.setDocumentationOfProperty(prop, newTip)
        obj.Document.commitTransaction()
        if obj in FreeCADGui.Selection.getSelection():
            FreeCADGui.Selection.removeSelection(obj)
            FreeCADGui.Selection.addSelection(obj)
        doc.recompute()
        return

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

#Gui.addCommand("DynamicDataSetTooltip", DynamicDataSetTooltipCommandClass())


########################################################################################
# Remove custom dynamic property


class DynamicDataRemovePropertyCommandClass(object):
    """Remove Property Command"""

    def __init__(self):
        self.obj = None

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'RemoveProperty.svg'),
                'MenuText': "&Remove Property",
                'Accel'   : "Ctrl+Shift+D,R",
                'ToolTip' : "Remove a custom property from the DynamicData object"}

    def getProperties(self,obj):
        props = [p for p in obj.PropertiesList if self.isDynamic(obj,p)]
        dlg = None
        if props:
            dlg = SelectObjects(props,"Select dynamic properties to remove")
            dlg.all.setCheckState(QtCore.Qt.Unchecked)
            ok = dlg.exec_()
            if not ok:
                return []
        return dlg.selected if dlg else []

    def isDynamic(self,obj,prop):
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

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        selection = Gui.Selection.getSelection()
        obj = self.obj
        #remove the property
        window = QtGui.QApplication.activeWindow()
        items = self.getProperties(obj)
        if len(items)==0:
            return
        obj.Document.openTransaction("Remove properties")
        for item in items:
            try:
                obj.removeProperty(item)
            except Exception as ex:
                FreeCAD.Console.PrintError(f"DynamicData::Exception cannot remove {item}\n{ex}")
        obj.Document.commitTransaction()
        if obj in selection:
            FreeCADGui.Selection.removeSelection(obj)
            FreeCADGui.Selection.addSelection(obj)
        doc.recompute()
        return

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

#Gui.addCommand("DynamicDataRemoveProperty", DynamicDataRemovePropertyCommandClass())

########################################################################################
# Import aliases from spreadsheet


class DynamicDataImportAliasesCommandClass(object):
    """Import Aliases Command"""

    def getProperties(self,obj):
        cell_regex = re.compile('^dd.*$') #all we are interested in will begin with 'dd'
        prop = []
        for p in obj.PropertiesList:
            if cell_regex.search(p):
                prop.append(p)
        return prop


    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'ImportAliases.svg'),
                'MenuText': "&Import Aliases",
                'ToolTip' : "Import aliases from selected spreadsheet(s) into selected dd object"}


    def Activated(self):


        sheets=[]
        dd = None
        doc = FreeCAD.ActiveDocument
        selection = Gui.Selection.getSelectionEx()
        cap = lambda x: x[0].upper() + x[1:] #credit: PradyJord from stackoverflow for this trick
        if not selection:
            return
        for sel in selection:
            obj = sel.Object
            if "Spreadsheet.Sheet" in str(type(obj)) and not obj.Label[-1:] == '_': #ignore spreadsheet label's ending in underscore
                sheets.append(obj)
            elif "FeaturePython" in str(type(obj)) and hasattr(obj,"DynamicData"):
                if not dd:
                    dd = obj
                else:
                    FreeCAD.Console.PrintMessage("Can only have one dd object selected for this operation\n")
                    return
        if len(sheets)==0:
            #todo: handle no selected spreadsheets.  For now, just return
            FreeCAD.Console.PrintMessage("DynamicData: No selected spreadsheet(s)\n")
            return
        if not dd:
            #todo: handle no dd object selected.  For now, just return
            FreeCAD.Console.PrintMessage("DynamicData: No selected dd object\n")
            return

        #sanity check
        window = QtGui.QApplication.activeWindow()
        items=["Do the import, I know what I\'m doing","Cancel"]
        item,ok = QtGui.QInputDialog.getItem(window,'DynamicData: Sanity Check',
'Warning: This will modify your spreadsheet. \n\
\n\
It will import the aliases from the spreadsheet and reset them to \n\
point to the dd object.  After the import is done you should make any changes \n\
to the dd property rather than to the alias cell in the spreadsheet. \n\
\n\
All imports come in as values, not as expressions.\n\
\n\
For example: diameter=radius*2 imports as 10.0 mm, not as an expression radius*2\n\
\n\
You should still keep your spreadsheet because other expressions referencing aliases in the\n\
spreadsheet will still be referencing them.  The difference is now the spreadsheet cells \n\
will be referencing the dd object.  Again, make any changes to the dd property, not to the spreadsheet.\n\
\n\
For example: \n\
Dependency graph:\n\
before import: constraint -> spreadsheet\n\
after import: constraint -> spreadsheet -> dd object\n\
\n\
You can partially undo this operation.  If undone, the changes to the spreadsheet will be \n\
reverted, but you will still need to manually remove the new properties from the dd object.\n\
The new properties will remain after the undo, but they will no longer reference anything. \n\
\n\
You should save your document before proceeding.\n',items,0,False,windowFlags)
        if not ok or item==items[-1]:
            return
        FreeCAD.ActiveDocument.openTransaction("dd Import Aliases") #setup undo
        aliases=[]
        for sheet in sheets:
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

                name = 'dd'+sheet.Label+'_'+cap(alias)
                if not hasattr(dd,name): #avoid adding the same property again
                    dd.addProperty('App::Property'+propertyType,name,'Imported from: '+sheet.Label, propertyType)
                    setattr(dd,name,userString)
                    FreeCAD.Console.PrintMessage('DynamicData: adding property: '+name+' to dd object, resetting spreadsheet: '+sheet.Label+'.'+alias+' to point to '+dd.Label+'.'+name+'\n')
                    sheet.set(alias,str('='+dd.Label+'.'+name))
                else:
                    FreeCAD.Console.PrintWarning('DynamicData: skipping existing property: '+name+'\n')
                continue

        FreeCAD.ActiveDocument.commitTransaction()
        doc.recompute()
        if len(aliases)==0:
            FreeCAD.Console.PrintMessage('DynamicData: No aliases found.\n')
            return

        return

    def IsActive(self):
        sheets=[]
        dd = None
        selection = Gui.Selection.getSelectionEx()
        if not selection:
            return
        for sel in selection:
            obj = sel.Object
            if "Spreadsheet.Sheet" in str(type(obj)) and not obj.Label[-1:] == '_': #ignore spreadsheet labels ending in underscore
                sheets.append(obj)
            elif "FeaturePython" in str(type(obj)) and hasattr(obj,"DynamicData"):
                if not dd:
                    dd = obj
                else:
                    return False #more than 1 dd object selected
        if len(sheets)==0:
            return False
        if not dd:
            return False
        return True

#Gui.addCommand("DynamicDataImportAliases", DynamicDataImportAliasesCommandClass())



########################################################################################
# Import named constraints from sketch


class DynamicDataImportNamedConstraintsCommandClass(object):
    """Import Named Constraints Command"""

    def getProperties(self,obj):
        cell_regex = re.compile('^dd.*$') #all we are interested in will begin with 'dd'
        prop = []
        for p in obj.PropertiesList:
            if cell_regex.search(p):
                prop.append(p)
        return prop


    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'ImportNamedConstraints.svg'),
                'MenuText': "&Import Named Constraints",
                'ToolTip' : "Import named constraints from selected sketch(es) into selected dd object"}


    def Activated(self):
        sketches=[]
        dd = None
        doc = FreeCAD.ActiveDocument
        selection = Gui.Selection.getSelectionEx()
        cap = lambda x: x[0].upper() + x[1:] #credit: PradyJord from stackoverflow for this trick
        if not selection:
            return
        for sel in selection:
            obj = sel.Object
            if "Sketcher.SketchObject" in str(type(obj)) and not obj.Label[-1:] == '_': #ignore sketch labels ending in underscore
                sketches.append(obj)
            elif "FeaturePython" in str(type(obj)) and hasattr(obj,"DynamicData"):
                if not dd:
                    dd = obj
                else:
                    FreeCAD.Console.PrintMessage("Can only have one dd object selected for this operation\n")
                    return
        if len(sketches)==0:
            #todo: handle no selected sketches.  For now, just return
            FreeCAD.Console.PrintMessage("DynamicData: No selected sketch(es)\n")
            return
        if not dd:
            #todo: handle no dd object selected.  For now, just return
            FreeCAD.Console.PrintMessage("DynamicData: No selected dd object\n")
            return

        #sanity check
        window = QtGui.QApplication.activeWindow()
        items=["Do the import, I know what I\'m doing","Cancel"]
        item,ok = QtGui.QInputDialog.getItem(window,'DynamicData: Sanity Check',
'Warning: This will modify your sketch. \n\
It will import the named constraints from the sketch and reset them to \n\
point to the dd object.  After the import is done you should make changes \n\
to the dd object property rather than to the constraint itself. \n\
\n\
All imports come in as values.\n\
\n\
For example: diameter=radius*2 imports as 10.0 mm, not as an expression radius*2\n\
\n\
For that reason, it might be necessary to rework some formulas in some cases \n\
in order to maintain the parametricity of your model. \n\
\n\
This operation can be partially undone.  The sketch will be reset, but you will \n\
still need to remove the newly created properties from the dd object.  The properties \n\
will still be there, but they won\'t be linked to anything. \n\
\n\
You should save your document before proceeding\n',items,0,False,windowFlags)
        if not ok or item==items[-1]:
            return
        FreeCAD.ActiveDocument.openTransaction("dd Import Constraints") #setup undo
        constraints=[]
        for sketch in sketches:
            for con in sketch.Constraints:
                if not con.Name or con.Name[-1:]=='_': #ignore constraint names ending in underscore
                    continue
                if ' ' in con.Name:
                    FreeCAD.Console.PrintWarning('DynamicData: skipping \"'+con.Name+'\" Spaces invalid in constraint names.\n')
                    continue
                if not con.Driving:
                    FreeCAD.Console.PrintWarning('DynamicData: skipping \"'+con.Name+'\" Reference constraints skipped.\n')
                    continue
                constraints.append({'constraintName':con.Name,'value':con.Value,'constraintType':con.Type,'sketchLabel':sketch.Label, 'sketch':sketch})
                #try:
                #    pass
                #    #sketch.setExpression('Constraints.'+con.Name, dd.Label+'.dd'+sketch.Label+cap(con.Name))
                #except:
                #    FreeCAD.Console.PrintError('DynamicData: Exception setting expression for '+con.Name+' (skipping)\n')
                #    constraints.pop() #remove the constraint that gave the error
        if len(constraints)==0:
            FreeCAD.Console.PrintMessage('DynamicData: No named constraints found.\n')
            return

        for con in constraints:
            propertyType = "Length"
            value = con['value']
            if con['constraintType']=='Angle':
                propertyType="Angle"
                value *= (180.0/math.pi)
            name = 'dd'+con['sketchLabel']+cap(con['constraintName'])
            if not hasattr(dd,name): #avoid adding the same property again
                dd.addProperty('App::Property'+propertyType,name,'Imported from:'+con['sketchLabel'],'['+propertyType+'] constraint type: ['+con['constraintType']+']')
                setattr(dd,name,value)
                FreeCAD.Console.PrintMessage('DynamicData: adding property: '+name+' to dd object\n')
                sketch = con['sketch']
                sketch.setExpression('Constraints.'+con['constraintName'], dd.Label+'.dd'+sketch.Label+cap(con['constraintName']))
            else:
                FreeCAD.Console.PrintWarning('DynamicData: skipping existing property: '+name+'\n')
        FreeCAD.ActiveDocument.commitTransaction()
        doc.recompute()
        return

    def IsActive(self):
        sketches=[]
        dd = None
        doc = FreeCAD.ActiveDocument
        selection = Gui.Selection.getSelectionEx()
        if not selection:
            return
        for sel in selection:
            obj = sel.Object
            if "Sketcher.SketchObject" in str(type(obj)) and not obj.Label[-1:] == '_': #ignore sketch labels ending in underscore
                sketches.append(obj)
            elif "FeaturePython" in str(type(obj)) and hasattr(obj,"DynamicData"):
                if not dd:
                    dd = obj
                else:
                    return False #more than 1 dd object selected
        if len(sketches)==0:
            return False
        if not dd:
            return False
        return True

#Gui.addCommand("DynamicDataImportNamedConstraints", DynamicDataImportNamedConstraintsCommandClass())


########################################################################################
# Copy Property To and/or From dd <--> other object


class DynamicDataCopyPropertyCommandClass(object):
    """Copy Property Command"""

    def getProperties(self,obj):
        cell_regex = re.compile('^dd.*$') #all we are interested in will begin with 'dd'
        prop = []
        for p in obj.PropertiesList:
            if cell_regex.search(p):
                prop.append(p)
        return prop


    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'CopyProperty.svg'),
                'MenuText': "C&opy Property",
                'ToolTip' : "Copy/Set property values between selected objects"}


    def Activated(self):
        breakOnly = False #only break existing parametric link if True
        other = None #other object to copy properties either to or from
        other2 = None #allow set value from one non-dd to other non-dd
        dd = None
        dd2 = None
        doc = FreeCAD.ActiveDocument
        selection = Gui.Selection.getSelectionEx()
        if len(selection) != 1 and len(selection) != 2:
            return False
        for sel in selection:
            obj = sel.Object
            if "FeaturePython" in str(type(obj)) and hasattr(obj,"DynamicData"):
                if not dd:
                    dd = obj
                else:
                    dd2 = obj
            else:
                if not other:
                    other = obj
                else:
                    other2 = obj

        MODE_CANCEL = -1
        MODE_COPY_OBJ_TO_DD = 0
        MODE_SET_OBJ_TO_DD = 1
        MODE_SET_DD_TO_OBJ = 2
        MODE_COPY_DD_TO_DD2 = 3
        MODE_COPY_DD2_TO_DD = 4
        MODE_SET_DD_TO_DD2 = 5
        MODE_SET_DD2_TO_DD = 6
        MODE_SET_OBJ_TO_OBJ2 = 7
        MODE_SET_OBJ2_TO_OBJ = 8
        MODE_UNLINK_DD = 9
        MODE_UNLINK_OBJ = 10
        MODE_COPY_DD_TO_DD = 11
        MODE_SET_DD_TO_DD = 12
        #this is just to avoid exceptions in generating ops strings
        no_dd = no_dd2 = no_other = no_other2 = False
        if not dd:
            no_dd = True
            dd = other
        if not dd2:
            no_dd2 = True
            dd2 = dd or other
        if not other:
            no_other = True
            other = dd
        if not other2:
            no_other2 = True
            other2 = dd or other
        ops = { MODE_COPY_OBJ_TO_DD:"Copy property from "+other.Label+" --> to new dd ("+dd.Label+") property",
                MODE_SET_OBJ_TO_DD:"Set property value from "+other.Label+" --> to existing dd ("+dd.Label+") property",
                MODE_SET_DD_TO_OBJ:"Set property value from dd ("+dd.Label+") --> to existing "+other.Label +" property",
                MODE_SET_OBJ_TO_OBJ2:"Set property value from "+other.Label+" --> to existing "+other2.Label+" property",
                MODE_SET_OBJ2_TO_OBJ:"Set property value from "+other2.Label+" --> to existing "+other.Label+" property",
                MODE_COPY_DD_TO_DD2:"Copy property from dd ("+dd.Label+") --> to new dd ("+dd2.Label+") property",
                MODE_COPY_DD2_TO_DD:"Copy property from dd ("+dd2.Label+") --> to new dd ("+dd.Label+") property",
                MODE_SET_DD_TO_DD2:"Set property value from dd ("+dd.Label+") --> to existing dd ("+dd2.Label+") property",
                MODE_SET_DD2_TO_DD:"Set property value from dd ("+dd2.Label+") --> to exiting dd ("+dd.Label+") property",
                MODE_COPY_DD_TO_DD:"Copy existing property to new property",
                MODE_SET_DD_TO_DD:"Set existing property from existing property",
                MODE_UNLINK_DD:"Break existing parametric link of existing dd ("+dd.Label+") property",
                MODE_UNLINK_OBJ:"Break existing parametric link of existing ("+obj.Label+") property",
                MODE_CANCEL:"Cancel"}
        if no_dd:
            dd = None
        if no_dd2:
            dd2 = None
        if no_other:
            other = None
        if no_other2:
            other2 = None

        if dd and not dd2 and not other:
            dd2 = dd #allow for copying within the same dd object

        if other and dd:
            modes=[ops[MODE_COPY_OBJ_TO_DD], ops[MODE_SET_OBJ_TO_DD], ops[MODE_SET_DD_TO_OBJ], ops[MODE_CANCEL]]

        elif other and other2:
            modes=[ops[MODE_SET_OBJ_TO_OBJ2], ops[MODE_SET_OBJ2_TO_OBJ], ops[MODE_CANCEL]]

        elif dd and dd2:
            modes = [ops[MODE_COPY_DD_TO_DD2], ops[MODE_COPY_DD2_TO_DD], ops[MODE_SET_DD_TO_DD2], ops[MODE_SET_DD2_TO_DD], ops[MODE_CANCEL]]

        if dd == dd2 and not other and not other2:
            modes=[ops[MODE_COPY_DD_TO_DD], ops[MODE_SET_DD_TO_DD], ops[MODE_UNLINK_DD], ops[MODE_CANCEL]]

        if len(selection) == 1 and other and not dd:
            modes=[ops[MODE_UNLINK_OBJ], ops[MODE_CANCEL]]

        if len(selection) == 1 and not other and dd:
            modes=[ops[MODE_UNLINK_DD], ops[MODE_SET_DD_TO_DD], ops[MODE_COPY_DD_TO_DD], ops[MODE_CANCEL]]

        window = QtGui.QApplication.activeWindow()
        mode,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Select mode of operation',modes,0,False,windowFlags)
        if not ok:
            return
        if mode==ops[MODE_CANCEL]:
            return
        if mode == ops[MODE_COPY_OBJ_TO_DD] or mode == ops[MODE_COPY_DD_TO_DD2] or mode == ops[MODE_COPY_DD2_TO_DD]:
            if mode == ops[MODE_COPY_DD_TO_DD2]:
                fromObj = dd
                toObj = dd2
            elif mode == ops[MODE_COPY_DD2_TO_DD]:
                fromObj = dd2
                toObj = dd
            elif mode == ops[MODE_COPY_OBJ_TO_DD]:
                fromObj = other
                toObj = dd
            #make a copy of the property and add it to the dd object
            properties = self.getProperty(fromObj,allowMultiple=True)
            if not properties:
                return #user canceled
            fromProperty = properties[0]
            for property in properties:
                cap = lambda x: x[0].upper() + x[1:] #credit: PradyJord from stackoverflow for this trick
                name = property['name']
                if 'dd' in name[:2] or 'Dd' in name[:2]:
                    name = name[2:]
                name = 'dd'+cap(name)
                propertyType = property['type']
                if not propertyType:
                    return #user canceled
                name,ok=QtGui.QInputDialog.getText(window,'DynamicData','Enter the name for the new property\n',text=name, flags=windowFlags)
                if 'dd' in name[:2] or 'Dd' in name[:2]:
                    name = name[2:]
                if not ok:
                    return
                name = 'dd'+cap(name)
                while hasattr(toObj,name):
                    name,ok=QtGui.QInputDialog.getText(window,'DynamicData','A property with that name already exists.  \n\
Enter the name for the new property\n',text=name, flags=windowFlags)
                    if not ok:
                        return
                    if 'dd' in name[:2] or 'Dd' in name[:2]:
                        name = name[2:]
                    name = 'dd'+cap(name)
                doc.openTransaction("dd CopyProperty")
                try:
                    toObj.addProperty('App::Property'+propertyType.replace('(ViewObject)',''), name,'Copied from: '+fromObj.Label,'['+propertyType+']')
                    toProperty = {'name':name,'type':propertyType,'value':property['value']}
                except:
                    FreeCAD.Console.PrintError('DynamicData: Exception trying to add property ('+property['name']+')\n')
                try:
                    if propertyType=='String':
                        setattr(toObj,name,str(property['value']))
                    else:
                        setattr(toObj,name,property['value'])
                except:
                    FreeCAD.Console.PrintError('DynamicData: Exception trying to set property value ('+str(property['value'])+')\nCould be a property type mismatch.\n')
                doc.commitTransaction()
                doc.recompute()
                self.makeParametric(fromObj, fromProperty, toObj, toProperty)
        elif mode == ops[MODE_SET_OBJ_TO_DD] or mode==ops[MODE_SET_DD_TO_OBJ] or mode==ops[MODE_SET_DD_TO_DD2] \
                    or mode==ops[MODE_SET_DD2_TO_DD] or mode==ops[MODE_SET_OBJ_TO_OBJ2] or mode == ops[MODE_SET_OBJ2_TO_OBJ] \
                    or mode==ops[MODE_UNLINK_DD] or mode==ops[MODE_UNLINK_OBJ]:
            if mode == ops[MODE_UNLINK_DD]:
                fromObj = dd
                toObj = dd
                breakOnly = True
            elif mode == ops[MODE_UNLINK_OBJ]:
                fromObj = other
                toObj = other
                breakOnly = True
            elif mode == ops[MODE_SET_OBJ_TO_DD]:
                fromObj = other
                toObj = dd
            elif mode == ops[MODE_SET_DD_TO_OBJ]:
                fromObj = dd
                toObj = other
            elif mode == ops[MODE_SET_DD_TO_DD2]:
                fromObj = dd
                toObj = dd2
            elif mode == ops[MODE_SET_DD2_TO_DD]:
                fromObj = dd2
                toObj = dd
            elif mode == ops[MODE_SET_OBJ_TO_OBJ2]:
                fromObj = other
                toObj = other2
            elif mode == ops[MODE_SET_OBJ2_TO_OBJ]:
                fromObj = other2
                toObj = other
            #here we just set the value of an existing property
            if breakOnly:
                fromProperty = self.getProperty(fromObj, '\nChoose the property of '+fromObj.Label+' to unlink\n')
            else:
                fromProperty = self.getProperty(fromObj,'\nChoose the FROM property of '+fromObj.Label+'\n')
            if not fromProperty:
                return
            fromProperty=fromProperty[0] #returns a list, but only valid for copy modes, not set modes
            if not breakOnly:
                toProperty = self.getProperty(toObj,'\n\nPrevious Selection: '+fromObj.Label+':'+fromProperty['name']+' ('+str(fromProperty['value'])+')\n\nChoose the TO property of '+toObj.Label+'\n', matchType=fromProperty['type'].replace('(ViewObject)',''))
                if not toProperty:
                    return #user canceled
                toProperty=toProperty[0]
            else:
                toProperty = fromProperty
            if not toProperty:
                return
            if not breakOnly:
                doc.openTransaction("dd SetProperty")
                try:
                    if '(ViewObject)' in toProperty['type']:
                        setattr(toObj.ViewObject, toProperty['name'],fromProperty['value'])
                    else:
                        setattr(toObj,toProperty['name'],fromProperty['value'])
                except:
                    FreeCAD.Console.PrintError(\
'DynamicData: Exception trying to set property value ('+str(fromProperty['value'])+')\n\
Could be a property type mismatch\n\
\n\
From Object: '+fromObj.Label+', From Property: '+fromProperty['name']+', type: '+fromProperty['type']+'\n\
To Object: '+toObj.Label+', To Property: '+toProperty['name']+', type: '+toProperty['type']+'\n')
                doc.commitTransaction()
                doc.recompute()
                self.makeParametric(fromObj, fromProperty, toObj, toProperty)
            else: #break only
                self.makeParametric(fromObj, fromProperty, toObj, toProperty, breakOnly=True)


        doc.recompute()
        return

    def makeParametric(self,fromObj,fromProperty,toObj,toProperty,breakOnly=False):
        """create a parametric link using toObj.setExpression()
        fromProperty and toProperty are dict objects with keys:
        'name', 'type', and 'value' eg: {'name':'Height','type':'Length','value': 8 mm}
        this function only gets called after a successful copy/set operation
        copy operation is when new property was created in toObj
        set operation is when existing property value was changed in toObj"""

        #User might not want to do this, but we check to see if we can do it before asking
        if toProperty['type'] in nonLinkableTypes:
            return
        #ViewObject does not have setExpression(), so do not try to parametrically link
        if '(ViewObject)' in fromProperty['type'] or '(ViewObject)' in toProperty['type']:
            return
        breakLink = False
        if not breakOnly:
            window = QtGui.QApplication.activeWindow()
            items = ["Create parametric link", "Make simple non-parametric copy by value","Break parametric link"]
            item,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Create parametric link?',items,0,False,windowFlags)
            if not ok:
                return
            elif item==items[1]:
                return
            elif item==items[-1]: #break parametric link
                breakLink=True
        else:
            breakLink = True

        #only set parametric link in non-dd objects
        if hasattr(toObj, "DynamicData"):
            tmpObj = fromObj
            fromObj = toObj
            toObj = tmpObj
            tmpProp = fromProperty
            fromProperty = toProperty
            toProperty = tmpProp

        #handle xyzTypes first
        if fromProperty['type'] in xyzTypes:
            try:
                if not breakLink:
                    toObj.setExpression(toProperty['name']+'.x',fromObj.Name+'.'+fromProperty['name']+'.x')
                    toObj.setExpression(toProperty['name']+'.y',fromObj.Name+'.'+fromProperty['name']+'.y')
                    toObj.setExpression(toProperty['name']+'.z',fromObj.Name+'.'+fromProperty['name']+'.z')
                else: #break the parametric link
                    toObj.setExpression(toProperty['name']+'.x', None)
                    toObj.setExpression(toProperty['name']+'.y', None)
                    toObj.setExpression(toProperty['name']+'.z', None)
            except:
                FreeCAD.Console.PrintError(\
'DynamicData: Exception trying to parametrically link ('+str(fromProperty['value'])+')\n\
Could be a property type mismatch\n\
\n\
From Object: '+fromObj.Label+', From Property: '+fromProperty['name']+', type: '+fromProperty['type']+'\n\
To Object: '+toObj.Label+', To Property: '+toProperty['name']+', type: '+toProperty['type']+'\n')
            return

        #handle placement types
        if fromProperty['type'] in 'Placement':
            try:
                if not breakLink:
                    toObj.setExpression(toProperty['name']+'.Base.x',fromObj.Name+'.'+fromProperty['name']+'.Base.x')
                    toObj.setExpression(toProperty['name']+'.Base.y',fromObj.Name+'.'+fromProperty['name']+'.Base.y')
                    toObj.setExpression(toProperty['name']+'.Base.z',fromObj.Name+'.'+fromProperty['name']+'.Base.z')
                    toObj.setExpression(toProperty['name']+'.Rotation.Angle',fromObj.Name+'.'+fromProperty['name']+'.Rotation.Angle')
                    toObj.setExpression(toProperty['name']+'.Rotation.Axis.x',fromObj.Name+'.'+fromProperty['name']+'.Rotation.Axis.x')
                    toObj.setExpression(toProperty['name']+'.Rotation.Axis.y',fromObj.Name+'.'+fromProperty['name']+'.Rotation.Axis.y')
                    toObj.setExpression(toProperty['name']+'.Rotation.Axis.z',fromObj.Name+'.'+fromProperty['name']+'.Rotation.Axis.z')
                else: #break parametric link
                    toObj.setExpression(toProperty['name']+'.Base.x', None)
                    toObj.setExpression(toProperty['name']+'.Base.y', None)
                    toObj.setExpression(toProperty['name']+'.Base.z', None)
                    toObj.setExpression(toProperty['name']+'.Rotation.Angle', None)
                    toObj.setExpression(toProperty['name']+'.Rotation.Axis.x', None)
                    toObj.setExpression(toProperty['name']+'.Rotation.Axis.y', None)
                    toObj.setExpression(toProperty['name']+'.Rotation.Axis.z', None)
            except:
                FreeCAD.Console.PrintError(\
'DynamicData: Exception trying to parametrically link ('+str(fromProperty['value'])+')\n\
Could be a property type mismatch\n\
\n\
From Object: '+fromObj.Label+', From Property: '+fromProperty['name']+', type: '+fromProperty['type']+'\n\
To Object: '+toObj.Label+', To Property: '+toProperty['name']+', type: '+toProperty['type']+'\n')
            return

        #handle all other general types
        try:
            if not breakLink:
                toObj.setExpression(toProperty['name'],fromObj.Name+'.'+fromProperty['name'])
            else: #break the link
                toObj.setExpression(toProperty['name'], None)
        except:
            FreeCAD.Console.PrintError(\
'DynamicData: Exception trying to parametrically link ('+str(fromProperty['value'])+')\n\
Could be a property type mismatch\n\
\n\
From Object: '+fromObj.Label+', From Property: '+fromProperty['name']+', type: '+fromProperty['type']+'\n\
To Object: '+toObj.Label+', To Property: '+toProperty['name']+', type: '+toProperty['type']+'\n')
        return

    def getProperty(self,obj,msg='',allowMultiple=False,matchType=''):
        """ask user which property and return it or None
           property will be in the form of a list of dictionary objects
           with keys 'type', 'name', 'value' """
        available = []
        pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")
        supportViewObjectProperties = pg.GetBool('SupportViewObjectProperties', True)
        propertiesList = obj.PropertiesList
        whiteList=['Proxy','ExpressionEngine','DynamicData','Label','Shape']
        for prop in propertiesList:
            if prop in whiteList:
                continue
            p = getattr(obj,prop)
#            strType = str(type(p))
#            types = self.getPropertyTypes()
#            typeFound = False;
            typeId = obj.getTypeIdOfProperty(prop)[13:] #strip "App::Property" from beginning
            if typeId in self.getPropertyTypes():
                available.append({'type':typeId,'value':p,'name':prop})
        if supportViewObjectProperties:
            viewPropertiesList = obj.ViewObject.PropertiesList
            for vprop in viewPropertiesList:
                if vprop in whiteList:
                    continue
                vp = getattr(obj.ViewObject,vprop)
                strType = str(type(vp))
                types = self.getPropertyTypes()
                typeFound = False;
                typeId = obj.ViewObject.getTypeIdOfProperty(vprop)[13:] #strip "App::Property" from beginning
                if typeId in self.getPropertyTypes():
                    available.append({'type':'(ViewObject)'+typeId,'value':vp,'name':vprop})

        items=[]
        moved=[]
        for ii in range(0,len(available)):
            a = available[ii]
            items.append("name: "+a['name']+", type: "+a['type']+", value: "+str(a['value']))
            if matchType==a['type'].replace('(ViewObject)',''): #put same types at top of list
                items.insert(0,items[-1])
                items.pop(-1)
                moved.append(ii)
        for mm in range(0,len(moved)): #arrange available list to match items list
            available.insert(0,available[moved[mm]])
            available.pop(moved[mm])

        if allowMultiple:
            items.append("<copy all>")
        items.append("<cancel>")
        window = QtGui.QApplication.activeWindow()
        item,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Copy/Set Property Tool\n\nSelect property to copy\n'+msg,items,0,False,windowFlags)
        if not ok or item==items[-1]:
            return None
        if allowMultiple and item==items[-2]:
            return available
        return [available[items.index(item)]]

    def IsActive(self):
        other = None #other object to copy properties either to or from
        dd = None
        selection = Gui.Selection.getSelectionEx()
        if len(selection) == 1:
            return True #only can break parametric link with only 1 object selected
        if len(selection) != 1 and len(selection) != 2:
            return False
        for sel in selection:
            obj = sel.Object
            if "FeaturePython" in str(type(obj)) and hasattr(obj,"DynamicData"):
                dd = obj
        if not dd and not len(selection)==2:
            return False
        return True

    def getPropertyTypes(self):
        return propertyTypes


#Gui.addCommand("DynamicDataCopyProperty", DynamicDataCopyPropertyCommandClass())


initialize()
