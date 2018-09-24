# -*- coding: utf-8 -*-
###################################################################################
#
#  DynamicDataCmd.py
#  
#  Copyright 2018 Mark Ganson <TheMarkster> mwganson at gmail
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
__date__    = "2018.09.24"
__version__ = "1.0"

from FreeCAD import Gui
from PySide import QtCore, QtGui

import FreeCAD, FreeCADGui, Part, os, math, re
__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )

keepToolbar = True
version = 1.0

def initialize():
    Gui.addCommand("DynamicDataCreateObject", DynamicDataCreateObjectCommandClass())
    Gui.addCommand("DynamicDataAddProperty", DynamicDataAddPropertyCommandClass())
    Gui.addCommand("DynamicDataRemoveProperty", DynamicDataRemovePropertyCommandClass())
    Gui.addCommand("DynamicDataSettings", DynamicDataSettingsCommandClass())
    pass

#######################################################################################
# Keep Toolbar active even after leaving workbench

class DynamicDataSettingsCommandClass(object):
    """Settings, currently only whether to keep toolbar after leaving workbench"""

    def __init__(self):
        pass        


    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'Settings.png') , # the name of an icon file available in the resources

            'MenuText': "&Settings" ,
            'ToolTip' : "Workbench settings dialog"}
 
    def Activated(self):
        doc = FreeCAD.ActiveDocument
        from PySide import QtGui
        window = QtGui.QApplication.activeWindow()
        pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")
        keep = pg.GetBool('KeepToolbar',True)
        items=["Keep the toolbar active","Do not keep the toolbar active"]
        item,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Settings\n\nKeep Toolbar after leaving workbench?\n\nCurrent setting = '+str(keep)+'\n',items,0,False)
        if ok and item == items[0]:
            keep = True
        elif ok and item==items[1]:
            keep = False
        pg.SetBool('KeepToolbar', keep)
        

        return
   
    def IsActive(self):
        return True


#Gui.addCommand("DynamicDataKeepToolbar", DynamicDataKeepToolbarCommandClass())


####################################################################################
# Create the dynamic data container object

class DynamicDataCreateObjectCommandClass(object):
    """Create Object command"""

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'CreateObject.png') ,
            'MenuText': "&Create Object" ,
            'ToolTip' : "Create the DynamicData object to contain the custom properties"}
 
    def Activated(self):
        doc = FreeCAD.ActiveDocument
        doc.openTransaction("CreateObject")
        a = doc.addObject("App::FeaturePython","dd")
        doc.recompute()
        a.addProperty("App::PropertyStringList","DynamicData").DynamicData=self.getHelp()
        doc.recompute()
        doc.commitTransaction()
        a.touch()
        doc.recompute()
        Gui.Selection.clearSelection()
        doc.recompute()
        Gui.Selection.addSelection(a) #select so the user can immediately add a new property
        doc.recompute()
        return
   
    def IsActive(self):
        if not FreeCAD.ActiveDocument:
            return False
        return True

    def getHelp(self):
        return ["Created with DynamicData workbench",
                "Workbench not required for use",
                "only for adding/removing properties",
                "which can be done via python console",


]

#Gui.addCommand("DynamicDataCreateObject", DynamicDataCreateObjectCommandClass())

######################################################################################
# Add a dynamic property to the object


class DynamicDataAddPropertyCommandClass(object):
    """Add Property Command"""


    def getPropertyTypes(self):
        return (
        "Length",
        "Float",
        "FloatList",
        "Integer",
        "IntegerList",
        "Precision",
        "String",
        "Angle",
        "Distance",
        "Path",
        "File",
        "FileIncluded",
        "IntegerConstraint",
        "Percent",
        "FloatConstraint",
        "Font",
        "Bool",
        "Color",
        "MaterialList",
        "Quantity",
        "QuantityConstraint",
        "Area",
        "Volume",
        "Speed",
        "Acceleration",
        "Force",
        "Pressure",
        "Link",
        "LinkChild",
        "LinkGlobal",
        "LinkList",
        "LinkListChild",
        "LinkListGlobal",
        "Matrix",
        "Vector",
        "VectorDistance",
        "Position",
        "Direction",
        "Placement",
        "PlacementLink",)

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'AddProperty.png') ,
            'MenuText': "&Add Property" ,
            'ToolTip' : "Add a custom property to the DynamicData object"}

    def Activated(self):

        doc = FreeCAD.ActiveDocument
        obj = Gui.Selection.getSelectionEx()[0].Object
        if not 'FeaturePython' in str(obj.TypeId):
            FreeCAD.Console.PrintError('DynamicData Workbench: Cannot add property to non-FeaturePython objects.\n')
            return
        doc.openTransaction("AddProperty")
        #add the property
        window = QtGui.QApplication.activeWindow()
        items = self.getPropertyTypes()
        item,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Add Property Tool\n\nSelect Property Type',items,0,False)
        if not ok:
            return
        else:
            self.propertyName,ok = QtGui.QInputDialog.getText(window,'Property Name', 
'Enter Property Name;[group name];[tool tip];[value]\n\
\n\
(\'dd\' will be prepended to the name)\n\
\n\
(Separate with semicolons)\n\
(Use 2 semicolons (;;) to keep same group name)\n\
(Group name; tool tip; value are optional)\n\
\n\
Examples:\n\
\n\
radius\n\
depth;base dimensions;depth of base plate;50\n\
width;;width of base plate;150\n\
\n\
Current group name: '+str(self.groupName)+'\n')
            if not ok or len(self.propertyName)==0:
                return
            else:
                if 'dd' in self.propertyName[:2] or 'Dd' in self.propertyName[:2]:
                    self.propertyName = self.propertyName[2:] #strip dd temporarily
                cap = lambda x: x[0].upper() + x[1:] #credit: PradyJord from stackoverflow for this trick
                self.propertyName = cap(self.propertyName) #capitalize first character to add space between dd and self.propertyName
                self.tooltip=item #e.g. App::PropertyFloat
                val=None
                hasVal = False
                if ';' in self.propertyName:
                    split = self.propertyName.split(';')
                    self.propertyName = split[0]
                    if len(split)>1: #has a group name
                        if len(split[1])>0: #allow for ;; empty string to mean use current group name
                            self.groupName = split[1]
                    if len(split)>2: #has a tooltip
                        self.tooltip = split[2]
                    if len(split)>3: #has a value
                        val = split[3]
                        hasVal = True
                p = obj.addProperty('App::Property'+item,'dd'+self.propertyName,str(self.groupName),self.tooltip)
                if hasVal:
                    try:
                        atr = self.eval_expr(val)
                    except:
                        try:
                            atr = val
                        except:
                            FreeCAD.Console.PrintWarning('DynamicData: Unable to set value: '+str(val)+'\n')
                    try:
                        setattr(p,'dd'+self.propertyName,atr)
                    except:
                        FreeCAD.Console.PrintWarning('DynamicData: Unable to set value: '+str(val)+'\n')
                          
                obj.touch()
                doc.recompute()

        doc.commitTransaction()
        doc.recompute()
        return
   
    def IsActive(self):
        if not FreeCAD.ActiveDocument:
            return False
        selection = Gui.Selection.getSelectionEx()
        if not selection:
            return False
        if not hasattr(selection[0].Object,"DynamicData"):
            return False

        return True

    def __init__(self):
        import ast, locale
        import operator as op
        self.groupName="DynamicData"
        self.propertyName="prop"
        self.tooltip="tip"

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
        return self.eval_(ast.parse(expr, mode='eval').body)

    def eval_(self,node):
        import ast
        import operator as op
        if isinstance(node, ast.Num): # <number>
            return node.n
        elif isinstance(node, ast.BinOp): # <left> <operator> <right>
            return self.operators[type(node.op)](self.eval_(node.left), self.eval_(node.right))
        elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
            return operators[type(node.op)](eval_(node.operand))
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
                App.Console.PrintMessage(u'unsupported token: '+node.id+u'\n')
        else:
            raise TypeError(node)

#Gui.addCommand("DynamicDataAddProperty", DynamicDataAddPropertyCommandClass())

########################################################################################
# Remove custom dynamic property


class DynamicDataRemovePropertyCommandClass(object):
    """Remove Property Command"""

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'RemoveProperty.png') ,
            'MenuText': "&Remove Property" ,
            'ToolTip' : "Remove a custom property from the DynamicData object"}

    def getProperties(self,obj):
        cell_regex = re.compile('^dd.*$') #all we are interested in will begin with 'dd'
        prop = []
        for p in obj.PropertiesList: 
            if cell_regex.search(p):
                prop.append(p)
        return prop

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        selection = Gui.Selection.getSelectionEx()
        if not selection:
            return
        obj = selection[0].Object
        doc.openTransaction("RemoveProperty")
        #remove the property
        window = QtGui.QApplication.activeWindow()
        items = self.getProperties(obj)
        if len(items)==0:
            FreeCAD.Console.PrintMessage("DyanmicData: no properties to remove.  Add some properties first.\n")
            return
        items.insert(0,"<Remove all properties>")
        item,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Remove Property Tool\n\nSelect property to remove',items,0,False)
        if not ok:
            return
        if item==items[0]:
            for ii in range(1,len(items)):
                obj.removeProperty(items[ii])
        else:
            obj.removeProperty(item)
        doc.recompute()
        doc.commitTransaction()
        return
   
    def IsActive(self):
        if not FreeCAD.ActiveDocument:
            return False
        selection = Gui.Selection.getSelectionEx()
        if not selection:
            return False
        obj = selection[0].Object
        if len(self.getProperties(obj))==0:
            return False
        if not hasattr(selection[0].Object,"DynamicData"):
            return False

        return True

#Gui.addCommand("DynamicDataRemoveProperty", DynamicDataRemovePropertyCommandClass())

initialize()