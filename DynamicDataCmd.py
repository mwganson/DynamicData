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
__date__    = "2019.06.29"
__version__ = "1.42"
version = 1.42
mostRecentTypes=[]
mostRecentTypesLength = 5 #will be updated from parameters


from FreeCAD import Gui
from PySide import QtCore, QtGui

import FreeCAD, FreeCADGui, Part, os, math, re
__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )

keepToolbar = True



def initialize():

    Gui.addCommand("DynamicDataCreateObject", DynamicDataCreateObjectCommandClass())
    Gui.addCommand("DynamicDataAddProperty", DynamicDataAddPropertyCommandClass())
    Gui.addCommand("DynamicDataRemoveProperty", DynamicDataRemovePropertyCommandClass())
    Gui.addCommand("DynamicDataImportNamedConstraints", DynamicDataImportNamedConstraintsCommandClass())
    Gui.addCommand("DynamicDataImportAliases", DynamicDataImportAliasesCommandClass())
    Gui.addCommand("DynamicDataSettings", DynamicDataSettingsCommandClass())
    Gui.addCommand("DynamicDataCopyProperty", DynamicDataCopyPropertyCommandClass())


#######################################################################################
# Keep Toolbar active even after leaving workbench

class DynamicDataSettingsCommandClass(object):
    """Settings, currently only whether to keep toolbar after leaving workbench"""
    global mostRecentTypes

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
        mostRecentTypesLength = pg.GetInt('mruLength',5)
        items=["Keep the toolbar active","Do not keep the toolbar active","Change length ("+str(mostRecentTypesLength)+") of most recently used type list"]
        item,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Settings\n\nSelect the settings option\n',items,0,False)
        if ok and item == items[0]:
            keep = True
            pg.SetBool('KeepToolbar', keep)
        elif ok and item==items[1]:
            keep = False
            pg.SetBool('KeepToolbar', keep)
        elif ok and item==items[2]:
            count,ok = QtGui.QInputDialog.getInt(window,'DynamicData','Settings\n\nHow many items in most recently used type list?\n\nCurrent setting = '+str(mostRecentTypesLength)+'\n',mostRecentTypesLength,0,20,1)
            if ok:
                pg.SetInt('mruLength',count)
                mostRecentTypesLength = count
                mostRecentTypes = []


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
        #doc.openTransaction("CreateObject")
        a = doc.addObject("App::FeaturePython","dd")
        doc.recompute()
        a.addProperty("App::PropertyStringList","DynamicData").DynamicData=self.getHelp()
        doc.recompute()
        setattr(a.ViewObject,'DisplayMode',['0']) #avoid enumeration -1 warning
        #doc.commitTransaction()
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
        return ["Created with DynamicData (v"+str(version)+") workbench.",
                "This is a simple container object built",
                "for holding custom properties.  Worbench",
                "installation is not required to use the",
                "container object -- instead only for",
                "adding / removing custom properties.",
                "(But this can also be done via scripting.)"
]

#Gui.addCommand("DynamicDataCreateObject", DynamicDataCreateObjectCommandClass())

######################################################################################
# Add a dynamic property to the object


class DynamicDataAddPropertyCommandClass(object):
    """Add Property Command"""
    global mostRecentTypes
    global mostRecentTypesLength


    def getPropertyTypes(self):
        return [
        "Acceleration",
        "Angle",
        "Area",
        "Bool",
        "Color",
        "Direction",
        "Distance",
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
        "MaterialList",
        "Matrix",
        "Path",
        "Percent",
        "Placement",
        "PlacementLink"
        "Position",
        "Precision",
        "Pressure",
        "Quantity",
        "QuantityConstraint",
        "Speed",
        "String",
        "StringList",
        "Vector",
        "VectorDistance",
        "Volume",]

    def GetResources(self):
        return {'Pixmap'  : os.path.join( iconPath , 'AddProperty.png') ,
            'MenuText': "&Add Property" ,
            'ToolTip' : "Add a custom property to the DynamicData object"}

    def Activated(self):
        global mostRecentTypes
        global mostRecentTypesLength

        doc = FreeCAD.ActiveDocument
        obj = Gui.Selection.getSelectionEx()[0].Object
        if not 'FeaturePython' in str(obj.TypeId):
            FreeCAD.Console.PrintError('DynamicData Workbench: Cannot add property to non-FeaturePython objects.\n')
            return
        #doc.openTransaction("dd Add Property")
        #add the property
        window = QtGui.QApplication.activeWindow()
        items = self.getPropertyTypes()
        pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")
        mostRecentTypesLength = pg.GetInt('mruLength',5)
        for ii in range(mostRecentTypesLength-1,-1,-1):
            if mostRecentTypes[ii]:
                items.insert(0,mostRecentTypes[ii])
                pg.SetString('mru'+str(ii), mostRecentTypes[ii])
        item,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Add Property Tool\n\nSelect Property Type',items,0,False)
        if not ok:
            return
        else:
            if not item in mostRecentTypes:
                mostRecentTypes.insert(0,item)
            else:
                mostRecentTypes.remove(item) #ensure it is at front of the list
                mostRecentTypes.insert(0,item)
            if len(mostRecentTypes)>mostRecentTypesLength:
                mostRecentTypes = mostRecentTypes[:mostRecentTypesLength]
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
            if not ok:
                return
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
            if ';' in self.propertyName:
                split = self.propertyName.split(';')
                self.propertyName = split[0].replace(' ','_')
                if len(self.propertyName)==0:
                    self.propertyName = self.defaultPropertyName
                if len(split)>1: #has a group name
                    if len(split[1])>0: #allow for ;; empty string to mean use current group name
                        self.groupName = split[1]
                if len(split)>2: #has a tooltip
                    if len(split[2])>0:
                        self.tooltip = self.tooltip + split[2]
                if len(split)==4: #has a value
                    val = split[3]
                    if len(val)>0:
                        hasVal = True
                if len(split)>4 and 'List' in item: #multiple values for list type property
                    hasVal = True
                    for ii in range(3,len(split)):
                        try:
                            if len(split[ii])>0:
                                vals.append(self.eval_expr(split[ii]))
                        except:
                            vals.append(split[ii])

            p = obj.addProperty('App::Property'+item,'dd'+self.propertyName,str(self.groupName),self.tooltip)
            if hasVal and len(vals)==0:
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
                    FreeCAD.Console.PrintWarning('DynamicData: Unable to set attribute: '+str(val)+'\n')
            elif hasVal and len(vals)>0:
                try:
                    setattr(p,'dd'+self.propertyName,vals)
                except:
                    FreeCAD.Console.PrintWarning('DynamicData: Unable to set list attribute: '+str(vals)+'\n')
            obj.touch()
            doc.recompute()

        #doc.commitTransaction()
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
        global mostRecentTypes
        global mostRecentTypesLength
        import ast, locale
        import operator as op
        self.groupName="DefaultGroup"
        self.defaultPropertyName="Prop"
        self.tooltip="tip"

        pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/DynamicData")
        mostRecentTypesLength = pg.GetInt('mruLength',5)
        for ii in range(mostRecentTypesLength-1,-1,-1):
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
        #doc.openTransaction("RemoveProperty")
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
        #doc.commitTransaction()
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
        return {'Pixmap'  : os.path.join( iconPath , 'ImportAliases.png') ,
            'MenuText': "&Import Aliases" ,
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
You should save your document before proceeding.\n',items,0,False)
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
                    sheet.set(alias,str(dd.Label+'.'+name))
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
        doc = FreeCAD.ActiveDocument
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
        return {'Pixmap'  : os.path.join( iconPath , 'ImportNamedConstraints.png') ,
            'MenuText': "&Import Named Constraints" ,
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
You should save your document before proceeding\n',items,0,False)
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
                constraints.append({'constraintName':con.Name,'value':con.Value,'constraintType':con.Type,'sketchLabel':sketch.Label})
                try:
                    sketch.setExpression('Constraints.'+con.Name, dd.Label+'.dd'+sketch.Label+cap(con.Name))
                except:
                    FreeCAD.Console.PrintError('DynamicData: Exception setting expression for '+con.Name+' (skipping)\n')
                    constraints.pop() #remove the constraint that gave the error
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
        return {'Pixmap'  : os.path.join( iconPath , 'CopyProperty.png') ,
            'MenuText': "C&opy Property" ,
            'ToolTip' : "Copy/Set property values between selected objects"}


    def Activated(self):
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
        #if not dd:
        #    return False
        if dd and not dd2 and not other:
            dd2 = dd #allow for copying within the same dd object
        if other and not other2:
            modes = ["Copy property from "+other.Label+" --> to dd ("+dd.Label+")",
                     "Set property value from "+other.Label+" --> to dd ("+dd.Label+")",
                     "Set property value from dd ("+dd.Label+") --> to "+other.Label,
                    "Cancel"
                    ]

            MODE_COPY_OBJ_TO_DD = 0
            MODE_SET_OBJ_TO_DD = 1
            MODE_SET_DD_TO_OBJ = 2
            MODE_COPY_DD_TO_DD2 = -1
            MODE_COPY_DD2_TO_DD = -1
            MODE_SET_DD_TO_DD2 = -1
            MODE_SET_DD2_TO_DD = -1
            MODE_SET_OBJ_TO_OBJ2 = -1
            MODE_SET_OBJ2_TO_OBJ = -1
        elif other and other2:
            modes = ["Set property value from "+other.Label+" --> to "+other2.Label,
                    "Set property value from "+other2.Label+" --> to "+other.Label,
                    "Cancel"]
            MODE_SET_OBJ_TO_OBJ2 = 0
            MODE_SET_OBJ2_TO_OBJ = 1
            MODE_COPY_OBJ_TO_DD = -1
            MODE_SET_OBJ_TO_DD = -1
            MODE_SET_DD_TO_OBJ = -1
            MODE_COPY_DD_TO_DD2 = -1
            MODE_COPY_DD2_TO_DD = -1
            MODE_SET_DD_TO_DD2 = -1
            MODE_SET_DD2_TO_DD = -1

        elif dd and dd2:
            modes = ["Copy property from dd ("+dd.Label+") --> to dd ("+dd2.Label+")",
                     "Copy property from dd ("+dd2.Label+") --> to dd ("+dd.Label+")",
                     "Set property value from dd ("+dd.Label+") --> to dd ("+dd2.Label+")",
                     "Set property value from dd ("+dd2.Label+") --> to dd ("+dd.Label+")",
                     "Cancel"]
                    
            MODE_COPY_DD_TO_DD2 = 0
            MODE_COPY_DD2_TO_DD = 1
            MODE_SET_DD_TO_DD2 = 2
            MODE_SET_DD2_TO_DD = 3
            MODE_COPY_OBJ_TO_DD = -1
            MODE_SET_OBJ_TO_DD = -1
            MODE_SET_DD_TO_OBJ = -1
            MODE_SET_OBJ_TO_OBJ2 = -1
            MODE_SET_OBJ2_TO_OBJ = -1


        if dd == dd2 and not other and not other2:
            modes=["Copy property","Set property value","Cancel"]
            MODE_COPY_DD_TO_DD2 = 0
            MODE_COPY_DD2_TO_DD = -1
            MODE_SET_DD_TO_DD2 = 1
            MODE_SET_DD2_TO_DD = -1
            MODE_COPY_OBJ_TO_DD = -1
            MODE_SET_OBJ_TO_DD = -1
            MODE_SET_DD_TO_OBJ = -1
            MODE_SET_OBJ_TO_OBJ2 = -1
            MODE_SET_OBJ2_TO_OBJ = -1

        window = QtGui.QApplication.activeWindow()
        mode,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Select mode of copy operation',modes,0,False)
        if not ok:
            return
        if mode==modes[-1]:
            return
        if mode == modes[MODE_COPY_OBJ_TO_DD] or mode == modes[MODE_COPY_DD_TO_DD2] or mode == modes[MODE_COPY_DD2_TO_DD]:
            if mode == modes[MODE_COPY_DD_TO_DD2]:
                fromObj = dd
                toObj = dd2
            elif mode == modes[MODE_COPY_DD2_TO_DD]:
                fromObj = dd2
                toObj = dd
            elif mode == modes[MODE_COPY_OBJ_TO_DD]:
                fromObj = other
                toObj = dd
            #make a copy of the property and add it to the dd object
            properties = self.getProperty(fromObj,allowMultiple=True)
            if not properties:
                return #user canceled
            for property in properties:
                cap = lambda x: x[0].upper() + x[1:] #credit: PradyJord from stackoverflow for this trick
                name = property['name']
                if 'dd' in name[:2] or 'Dd' in name[:2]:
                    name = name[2:]
                name = 'dd'+cap(name)
                propertyType = property['type']
                if not propertyType:
                    return #user canceled
                name,ok=QtGui.QInputDialog.getText(window,'DynamicData','Enter the name for the new property\n',text=name)
                if 'dd' in name[:2] or 'Dd' in name[:2]:
                    name = name[2:]
                name = 'dd'+cap(name)
                if not ok:
                    return
                while hasattr(toObj,name):
                    name,ok=QtGui.QInputDialog.getText(window,'DynamicData','A property with that name already exists.  \n\
Enter the name for the new property\n',text=name)
                    if not ok:
                        return
                    if 'dd' in name[:2] or 'Dd' in name[:2]:
                        name = name[2:]
                    name = 'dd'+cap(name)

                try:
                    toObj.addProperty('App::Property'+propertyType, name,'Copied from: '+fromObj.Label,'['+propertyType+']')
                except:
                    FreeCAD.Console.PrintError('DynamicData: unable to add property ('+property['name']+')\n')
                try:
                    if propertyType=='String':
                        setattr(toObj,name,str(property['value']))
                    else:
                        setattr(toObj,name,property['value'])
                except:
                    FreeCAD.Console.PrintError('DynamicData: unable to set property value ('+str(property['value'])+')\nCould be a property type mismatch.\n')
        elif mode == modes[MODE_SET_OBJ_TO_DD] or mode==modes[MODE_SET_DD_TO_OBJ] or mode==modes[MODE_SET_DD_TO_DD2] \
                    or mode==modes[MODE_SET_DD2_TO_DD] or mode==modes[MODE_SET_OBJ_TO_OBJ2] or mode == modes[MODE_SET_OBJ2_TO_OBJ]:
            if mode == modes[MODE_SET_OBJ_TO_DD]:
                fromObj = other
                toObj = dd
            elif mode == modes[MODE_SET_DD_TO_OBJ]:
                fromObj = dd
                toObj = other
            elif mode == modes[MODE_SET_DD_TO_DD2]:
                fromObj = dd
                toObj = dd2
            elif mode == modes[MODE_SET_DD2_TO_DD]:
                fromObj = dd2
                toObj = dd
            elif mode == modes[MODE_SET_OBJ_TO_OBJ2]:
                fromObj = other
                toObj = other2
            elif mode == modes[MODE_SET_OBJ2_TO_OBJ]:
                fromObj = other2
                toObj = other
            #here we just set the value of an existing property
            fromProperty = self.getProperty(fromObj,'\nChoose the FROM property\n')
            if not fromProperty:
                return
            fromProperty=fromProperty[0] #returns a list, but only valid for copy modes, not set modes
            toProperty = self.getProperty(toObj,'\nChoose the TO property\n',matchType=fromProperty['type'])
            if not toProperty:
                return
            toProperty=toProperty[0]

            try:
                setattr(toObj,toProperty['name'],fromProperty['value'])
            except:
                FreeCAD.Console.PrintError(\
'DynamicData: unable to set property value ('+str(fromProperty['value'])+')\n\
Could be a property type mismatch\n\
\n\
From Object: '+fromObj.Label+', From Property: '+fromProperty['name']+', type: '+fromProperty['type']+'\n\
To Object: '+toObj.Label+', To Property: '+toProperty['name']+', type: '+toProperty['type']+'\n')

        doc.recompute()
        return
   
    def getProperty(self,obj,msg='',allowMultiple=False,matchType=''):
        """ask user which property and return it or None
           property will be in the form of a list of dictionary objects
           with keys 'type', 'name', 'value' """
        available = []
        propertiesList = obj.PropertiesList
        whiteList=['Proxy','ExpressionEngine','DynamicData','Label','Shape']
        for prop in propertiesList:
            if prop in whiteList:
                continue
            p = getattr(obj,prop)
            strType = str(type(p))
            types = self.getPropertyTypes()
            typeFound = False;
            typeId = obj.getTypeIdOfProperty(prop)[13:] #strip "App::Property" from beginning
            if typeId in self.getPropertyTypes():
                available.append({'type':typeId,'value':p,'name':prop})
        items=[]
        moved=[]
        for ii in range(0,len(available)):
            a = available[ii]
            items.append("name: "+a['name']+", type: "+a['type']+", value: "+str(a['value']))
            if matchType==a['type']: #put same types at top of list
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
        item,ok = QtGui.QInputDialog.getItem(window,'DynamicData','Copy/Set Property Tool\n\nSelect property to copy\n'+msg,items,0,False)
        if not ok or item==items[-1]:
            return None
        if allowMultiple and item==items[-2]:
            return available
        return [available[items.index(item)]]

    def IsActive(self):
        other = None #other object to copy properties either to or from
        dd = None
        doc = FreeCAD.ActiveDocument
        selection = Gui.Selection.getSelectionEx()
        if len(selection) != 1 and len(selection) != 2:
            return False
        for sel in selection:
            obj = sel.Object
            if "FeaturePython" in str(type(obj)) and hasattr(obj,"DynamicData"):
                dd = obj
            else:
                other = obj
        if not dd and not len(selection)==2:
            return False
        return True

    def getPropertyTypes(self):
        return [
        "Acceleration",
        "Angle",
        "Area",
        "Bool",
        "Color",
        "Direction",
        "Distance",
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
        "MaterialList",
        "Matrix",
        "Path",
        "Percent",
        "Placement",
        "PlacementLink"
        "Position",
        "Precision",
        "Pressure",
        "Quantity",
        "QuantityConstraint",
        "Speed",
        "String",
        "StringList",
        "Vector",
        "VectorDistance",
        "Volume",]


#Gui.addCommand("DynamicDataCopyProperty", DynamicDataCopyPropertyCommandClass())


initialize()