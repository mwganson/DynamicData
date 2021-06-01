# DynamicData Workbench
<img src="Resources/icons/DynamicDataLogo.svg" alt="icon">

## Installation

Install via the Addon Manager in the Tools menu in FreeCAD version 0.17 and later.

## Overview

With this workbench you can create custom FeaturePython objects to serve as containers for custom properties.  These custom properties can then be used in much the same way as cells in a spreadsheet.  Users can refer to a custom property in a sketcher constraint (or from anywhere the Expression Engine can be accessed) the same way one might refer to a cell in a spreadsheet.  Take note that FCStd files containing these DynamicData dd objects <b>can be shared</b> with other users who do not have the DynamicData workbench installed on there systems and yet will still remain fully functional.  (But without the workbench installed those other users will not be able to add/remove properties unless it is done via scripting.)

### Example Video:
<img src="Resources/media/example.gif" alt="animated gif example">

### Create Object
<img src="Resources/icons/CreateObject.svg" alt="icon">
Creates a new DynamicData container object.

### Add Property
<img src="Resources/icons/AddProperty.svg" alt="icon">
Adds a new custom property to the selected DynamicData container object.  (If no DynamicData object is selected in the tree view this command will be disabled.)<br/>
<br/>
Adding custom properties is a 2-step process.  First step is to select the property type from the drop down list.<br/>
<br/>
<img src="Resources/media/add_property_scr.png" alt="add property screenshot">
<br/>
Second step is to give your new property a name and (optionally) a group name, tooltip, and an initial value.<br/>
<br/>
<b>Note: as of version 1.12 all tooltips now get [Type] prepended.  Example, if type is "Length" the tooltip would be something like "[Length] my tooltip".</b></br>
<br/>
<img src="Resources/media/add_property_scr2.png" alt="add property screenshot 2"><br/>
<br/>
Old style name;groupname;tooltip;value syntax is still supported in the Name field for those who wish to keep using it.<br/>
<br/>
All property names are prepended with "dd" automatically and the first letter is capitalized.  Thus, a name entered of "length" would be converted to "ddLength" and get displayed in the property view as "dd Length".  The purpose for this is to make it easier to reference your properties later on.  For example, if you wish to reference a DynamicData custom property from a sketch constraint you can enter "=dd.dd" (or click the expression engine "fx" icon and enter "dd.dd") to bring up a list of available custom properties: <br/>
<br/>
<img src="Resources/media/dd_constraint_reference_scr.png" alt="dd constraint reference screenshot"><br/>
<br/>
DynamicData has its own built-in evaluator, which can be used when entering values.  The actual value that gets placed into the property is the evaluated amount.  New, beginning with version 2.0, you can now enter FreeCAD expressions into the value field.  To signify to DynamicData that your entry is to be evaluated as a FreeCAD expression, prepend and equals sign (=) to the value.  If initializing a list type, such as IntegerList or FloatList, use something like =list(3;2;1) to initialize them.  For a list of type VectorList you can use the create() function integrated into the expression engine, see example below.  Create() works for types vector, placement, and rotation.<br/>
<br/>
Note: even though your value will be evaluated by the FreeCAD expression engine, you don't get the benefit of being prompted with autocompletions when entering it into the value field.<br/>
<br/>
Some examples:<br/>
<br/>
=(7/8)*25.4<br/>
=Cylinder.Radius*2<br/>
=list(3;2;1)<br/>
=list(create(<<vector>>; 2; 1; 2);create(<<vector>>; 0;0;0))<br/>
3*5<br/>
cos(pi)<br/>
golden_ratio<br/>
<br/>
For List property types, e.g. IntegerList or FloatList, you can separate the values by semicolons:<br/>
<br/>
3;5;9;12<br/>
or if using the expression engine:<br/>
=list(3;5;9;12)<br/>
<br/>

### Remove Property
<img src="Resources/icons/RemoveProperty.svg" alt="icon"><br/>
<br/>
Use this tool to remove a property previously added using the Add Property tool.  Select the property in the list you would like to remove.  You may also choose to remove all properties in one go. <b>(Care must be taken when removing properties because this action cannot be undone.)</b><br/>
<br/>
<img src="Resources/media/remove_property_scr.png" alt="remove property screenshot"><br/>
<br/>
### Import Aliases
<img src="Resources/icons/ImportAliases.svg" alt="icon"><br/>
Use this to import aliases from selected spreadsheets as properties into selected dd object.</br>
<br/>
<b>Warning: selected spreadsheets will be modified.  The cells containing the aliases will reference
the dd object property. </b><br />
<br/>
To prevent a cell containing an alias from being imported you should end the alias name with an underscore (_).  When the workbench code sees an alias name that ends with an underscore it will skip that alias and display a warning message in the report view, informing the user that this alias was skipped.  Similarly, spreadsheets with labels ending in the underscore will likewise be skipped.</br>
<br/>
To use this feature, select your dd object and one or more spreadsheets to be imported, then invoke the command either from the menu or the toolbar.  New properties of various types, e.g. "Length" will be added to the dd object for each alias found.  The property type depends on who FreeCAD has interpreted the type to be, which is based on the units used in the cell contents.  For example, "10.5 mm" would be seen as a "Length" property type while "45 deg" would be seen as an "Angle" property type, "5 mi/h" would be seen as a "Speed" type, etc.  Note: there could be some inconsistencies between the unit types recognized by the spreadsheet code and the property type names used in FreeCAD.  Please report any errors to me via Direct Message "TheMarkster" on the FreeCAD forum.  As an example of this type of mismatch, "Speed" types are identified as "Velocity" in the spreadsheet, so a minor fix is needed (already done in version 1.41) in the DynamicData source code to account for this naming inconsistency.<br/>
<br/>
Once you have imported the aliases you should still keep the spreadsheet because other FreeCAD objects, example sketch constraints, that were referencing the aliases before the import will still be referencing them.  Difference is now the spreadsheet references the dd object property.  Keep the spreadsheet, but only make modifications to the values in the dd property editor.  Otherwise, the changes made in the spreadsheet will break the connection to the dd object property.<br/>
<br/>
Another important consideration is the imports are done by value and not by reference.  In other words, suppose you have an aliased cell with a formula such as "=B1 * A2 - C3".  The import will be whatever value that formula evaluates to *at the time of the import*.  If you later modify the contents of B1, A2, or C3, those changes *do not* get propagated to the dd object property.  In other words, if B1 * A2 - C3 evalates to 15.23, then 15.23 is what gets imported.  I've hesitated to include this feature mostly because of this issue that could come up, but I've decided to let the user decide for himself whether to use this or not.<br/>
<br/>
This operation can be partially undone using FreeCAD's undo toolbar command.  The undo operation will undo the changes made to the imported spreadsheet, resetting all cells back to their former state, but it will not remove the newly created properties from the dd object.  But while the properties remain they will no longer reference anything else in the document or be referenced by anything else in the document, so they will be harmless in that sense.  Still, it is recommended to save your document before using this feature.<br/>
<br/>

### Import Named Constraints
<img src="Resources/icons/ImportNamedConstraints.svg" alt="icon"><br/>
Use this to import named constraints from selected sketches as properties into selected dd object.<br/>
<br/>
<b>Warning: selected sketches will be modified.  All named constraints will reference the dd object property.</b><br/>
<br/>
To prevent a named constraint from being imported, append an underscore to the constraint name.  For example, a radius constraint named "myRadius_" will be ignored.  Similarly sketches with labels ending in an underscore are also ignored, e.g. "Sketch_" cannot be imported.<br/>
<br/>
To use this feature, select your dd object and one or more sketches to be imported, then invoke the command either from the menu or the toolbar.  New properties of type "Length" will be added to the dd object for each named constraint found except "Angle" type will be used for "Angle" constraint types.<br/>
<br/>
<b>Care should be taken if the constraint uses the expression engine because only the value of the expression is used, not the expression itself, which could be a formula or a reference to some other constraint, property, or spreadsheet alias.</b>  For example, suppose you have a constraint named "radius" with an expression "Sketch.length*2" with a value of 2.75mm.  This would create a new property in the dd object named ddSketchRadius with a value of 2.75mm and the constraint is now set to "dd.ddSketchRadius".  The upshot of this is if you change the value of the Sketch.length constraint the ddSketchRadius property is NOT updated.  In such cases you should alter the value of the ddSketchRadius property so that it once again references that length property, presumably now called ddSketchLength.<br/>
<br/>
This operation can now be partially undone (as of version 1.40).  If you use FreeCAD's Undo toolbar icon (or CTRL+Z on Windows) the sketch will be reset back to its former state before the import, but the newly created dd property objects will remain.  The new properties will not reference anything else and will not be reference by anything else, but the Undo operation does not delete properties.  It is suggested to make a backup copy of your .FCStd file before using this feature.<br/>
<br/>
### Copy Property
<img src="Resources/icons/CopyProperty.svg" alt="icon"><br/>
<br/>
<b>New feature in version 1.5</b>: Now you can parametrically link a copied or set property. Then when the source property changes, the copy will parametrically change with it.  You can still choose the non-parametric copy when setting/copying.  The parametric link can also be broken later using the Set/Copy command.  For some property types breaking the parametric link is trivial enough to do it manually, but for other types, such as Placement, it can be very tedious to do it manually.<br/>
<br/>
Copy a property from one object to another or within the same dd object.  Properties can only be copied to a dd object, but the source can be a non-dd object or a dd object (including copies from within the same dd object).  Can also be used to set the value of an existing property rather than creating a new property.  To use, just select the object containing the original property to be copied and the dd object that will contain the new property, then click the Copy Property icon.  You will be guided through the process with a series of dialogs.<br/>
<br/>
One potential application for this feature is to make copies of placement properties.  These copies can then be used to easily set the original objects Placement property to any of the values held by any of the placement copies.  For example, your model might include a lever that can be in any of 3 positions, say forward, neutral, and reverse.  Move it to the forward position, and then make a copy of the placement.  Move it to the neutral position, and do the same, ditto for the reverse position.  Your dd object could contain 3 placement properties: ddForward, ddNeutral, and ddReverse.<br/>
<br/>
#### Copy a property from another object to a dd object<br/>
<br/>
In this example we will copy a placement property from a Sphere to a dd object.  Select the Sphere and the dd object in the tree view, and then click the Copy Property icon in the toolbar (or select via the menu).  1) select the Copy property from Sphere --> to dd (dd) option and click OK.  2) You will be presented with a list of the properties available to be copied from the Sphere object, select the Placement property and click OK.  3) Give the new property to be created a new name or just click OK to accept the default name chosen for you.  (Note: if the new name you give conflicts with an existing property name in the dd object you will be prompted again for a new name, so if you see this multiple times it means there is a name conflict.)<br/>
<br/>
<img src="Resources/media/copy_property_scr.png" alt="copy property example screenshot"><br/>
<br/>
#### Set a property value <br/>
<br/>
The process for this is substantially the same as for copying a property except you will need to select an existing property in the target object to receive a new value rather than giving a name for a new property to be created.  It is important to match the property types when trying to copy the value from one property to another or else the operation is likely to fail.  (But note there are cases where it might work to copy a property value of one type to another property of a different type, for example, an Integer value can be copied to a Float property.)  There is no error checking being done to prevent you from trying to copy a value from one property type to another, but once the from property is chosen, then when selecting the to property to receive the value the properties that are of the same type as the from property will be displayed at the top of the selection list for your convenience.<br/>
<br/>


### Settings
<img src="Resources/icons/Settings.svg" alt="icon">
Use this to change workbench settings.

#### Keep Toolbar
Setting this to True (default is True) means the DynamicData toolbar will remain active even after switching away from the DynamicData workbench.  This value is stored in FreeCAD's parameters, accessible via Tools menu -> Edit Parameters.  This parameter is a Boolean type in BaseApp -> Preferences -> Mod -> DynamicData -> KeepToolbar.<br/>
<br/>
You must always open the DynamicData workbench at least once per FreeCAD session in order to first initialize the workbench toolbar.  If you would like to have the DynamicData toolbar icons always available without need to visit the DynamicData workbench you may configure DynamicData as your default startup workbench so that whenever you start FreeCAD it opens in the DynamicData workbench. (Edit -> Preferences -> General -> Startup -> Autoload module after startup -> DynamicData.)<br/>
<br/>
There is also an option in the Edit -> Preferences -> Start -> Options section to load DynamicData after creating / opening an existing document from the start page.<br/>
<br/>
#### Support ViewObject Properties
If this is True you will be able also to access properties in the view tab.  View tab properties will have (ViewObject) prepended to their property types in the selection dialog.  Manipulating these properties is the same as for the data tab properties except the view tab properties do not support parametric linking.<br/>
<br/>
#### Add to active container on creation
If this is True when you create a new dd object it will be added to the currently active container, if there is one active.  The container can be either a Part container or a Body (Part Design) container.  If you do not wish for the dd object to be in one of the containers you can always drag it out by dropping onto the document name in the tree view.  (But the opposite will not work for Part Design Body containers -- the dd object must be placed into the Body container upon creation of the dd object.)  Note: this does not change the scope of the dd object properties, which will always be global.<br/>

#### Change length of most recently used type list
When you add a new property type you are presented with a list of property types to select from. This list is sorted alphabetically beginning with "Acceleration".  But before we get to the "Acceleration" property type we have at the top of the list the most recently used property types, which are sorted in the order of most recently used.  This setting allows you to choose how many of the most recently used property types you want listed before we get to the rest of the alphabetized list.  A setting of 0 here would disable the most recently used list.  Default is 5.  Maximum is 25.  This value is stored in FreeCAD's parameters, accessible via Tools menu -> Edit Parameters.  This parameter is an Integer type in BaseApp -> Preferences -> Mod -> DynamicData -> mruLength.<br/>
<br/>


#### Release notes:<br/>
* 2021.05.31 (version 2.3)<br/>
** in adding new property dialog put current group in an editable combo box
* 2021.05.17 (version 2.24)<br/>
** put cancel option at top of remove properties menu to help avoid accidentally deleting all properties
* 2021.05.16 (version 2.23)<br/>
** fix bug in spreadsheet import alias (prepend = sign to redirected spreadsheet cells)
* 2020.09.10 (version 2.22)<br/>
** fix update checker (and test)
* 2020.09.10 (version 2.21)<br/>
** testing check updater function
* 2020.09.10 (version 2.2)<br/>
** enable check for updates on workbench startup
* 2020.08.25 (version 2.1)<br/>
** enable undo and redo for adding/removing properties
* 2020.08.24 (version 2.01)<br/>
** slight modification to label in property creation dialog
* 2020.08.13 (version 2.0)<br/>
** adds ability to handle expressions in value box during property creation
** to use, prepend "=" to the value, for example:
** =(7/8)*25.4
** =Cylinder.Radius*2
* 2020.08.12 (Version 1.95)<br/>
** Change default shortcuts from Ctrl+D,A to Ctrl+Shift+D,A due to conflict with Ctrl+D tree display properties
* 2020.08.05 (version 1.94)<br/>
** support property type LinkSubList
* 2020.08.04 (version 1.93)<br/>
** switched to svg icons for those with higher def displays
* 2020.08.02 (version 1.92)<br/>
** changed default shortcuts due to potential conflicts
** Ctrl+D,C -- create new dd object
** Ctrl+D,A -- add new property to dd object
** Ctrl+D,R -- remove property from dd object
** Ctrl+D,S -- open settings
* 2020.08.01 (version 1.91)<br/>
** add default shortcuts:
** D,D,C (or ddc) create new dd object
** D,D,A (or dda) add new property to dd object
** D,D,R (or ddr) remove existing property from dd object
** D,D,S (or dds) open settings
* 2020.07.22 (version 1.90)<br/>
** add option to put new dd object into current active container (part or body)
** improve settings by add asterisk (*) before currently set option
* 2020.07.20 (version 1.83)<br/>
** fix a bug where creating new body caused properties to no longer get added to dd object
* 2020.07.12 (version 1.82)<br/>
** fix a bug related to evaluating some values
* 2020.06.23 (version 1.81)<br/>
** check for existing property name before creating property
* 2020.06.23 (version 1.80)<br/>
** add support for VectorList type (requires recent build of 0.19)
* 2020.03.01 (version 1.76)<br/>
** bugfix: import constraints was giving error when linking to new dd property
* 2020.03.01 (version 1.75)<br/>
** make create parametric links option default when copying/setting
** create parametric links only in the non-dd objects when copying
* 2020.02.27 (version 1.74)<br/>
** maintenance issue due to code changes in spreadsheet workbench
** treats int types as floats since that will likely be users'
** expectations for handling values, such as 10.0 as float not int
* 2019.08.13 (version 1.73)<br/>
** bugfix -- typo
* 2019.08.08 (version 1.72)<br/>
** make simple copy default instead of parametric link
** bugfix with copy all when user cancels midway<br/>
* 2019.08.08 (version 1.71)<br/>
** remove unused help button from dialogs
** fix recent types list -- sigh<br/>
* 2019.08.08 (version 1.70)<br/>
** revamp add property dialog<br/>
* 2019.08.06 (version 1.61)<br/>
** fix but (yet again) in most recent types list
* 2019.07.27 (version 1.60)<br/>
** add support for ViewObject properties<br/>
* 2019.07.26 (version 1.50)<br/>
** add ability create parametric links when setting/copying<br/>
* 2019.07.17 (version 1.44)<br/>
** do not import non-driving reference mode constraints<br/>
* 2019.07.05 (version 1.43)<br/>
** fixed bug in resetting length of mru list<br/>
* 2019.06.30 (version 1.42)<br/>
** fixed bug in mru list<br/>
** added setting for length of mru (0-25)<br/>
* 2019.06.29 (version 1.41)<br/>
** minor bug fix<br/>
* 2019.06.29 (version 1.40)<br/>
** adds spreadsheet alias import feature<br/>
** adds undo capability to sketch import feature<br/>
* 2018.10.03 (version 1.31)<br/>
** transparent background icons<br/>
* 2018.10.02 (version 1.30)<br/>
** Add copy/set property<br/>
* 2018.09.27 (version 1.20)<br/>
** Add sketch import<br/>
* 2018.09.25 (version 1.11)<br/>
** bugfixes, handle empty names better<br/>
* 2018.09.24 (version 1.1)<br/> 
** Add 5 most recently used types to top of property type list, sort remainder.<br/>
** Display version information in DynamicData string property <br/>
* v2018.09.19  2018.09.19:  Initial version<br/>

