# DynamicData Workbench
<img src="Resources/icons/DynamicDataLogo.png" alt="icon">

## Overview

With this workbench you can create custom FeaturePython objects (herein referred to as DynamicData dd objects) to serve as containers for custom properties.  These custom properties can then be used in much the same way as cells in a spreadsheet.  Users can refer to a custom property in a sketcher constraint (or from anywhere the Expression Engine can be accessed) the same way one might refer to a cell in a spreadsheet.  Take note that FCStd files containing these DynamicData dd objects <b>can be shared</b> with other users who do not have the DynamicData workbench installed on there systems and yet will still remain fully functional.  (But without the workbench installed those other users will not be able to add/remove properties unless it is done via scripting.)

### Example Video:
<img src="Resources/media/example.gif" alt="animated gif example">

### Warning Message:
You might see this warning message in the report view: <b>"Enumeration index -1 is out of range, ignore it".</b>  This is a FreeCAD warning related to string properties, which can be safely ignored, as the warning itself suggests.

### Create Object
<img src="Resources/icons/CreateObject.png" alt="icon">
Creates a new DynamicData container object.

### Add Property
<img src="Resources/icons/AddProperty.png" alt="icon">
Adds a new custom property to the selected DynamicData container object.  (If no DynamicData object is selected in the tree view this command will be disabled.)<br/>
<br/>
Adding custom properties is a 2-step process.  First step is to select the property type from the drop down list.<br/>
<br/>
<img src="Resources/media/add_property_scr.png" alt="add property screenshot">
<br/>
Second step is to give your new property a name and (optionally) a group name, tooltip, and an initial value.</br>
<br/>
<img src="Resources/media/add_property_scr2.png" alt="add property screenshot 2"><br/>
<br/>
All property names are prepended with "dd" automatically and the first letter is capitalized.  Thus, a name entered of "length" would be converted to "ddLength" and get displayed in the property view as "dd Length".  The purpose for this is to make it easier to reference your properties later on.  For example, if you wish to reference a DynamicData custom property from a sketch constraint you can enter "=dd.dd" (or click the expression engine "fx" icon and enter "dd.dd") to bring up a list of available custom properties: <br/>
<br/>
<img src="Resources/media/dd_constraint_reference_scr.png" alt="dd constraint reference screenshot"><br/>
<br/>
In the same line edit widget where you enter the name of the property you may (optionally) include a new group name, tooltip, and set an initial value for the property.  Separate these with semicolons (;).  Some examples: <br/>
<br/>
<b>radius;Barrel Properties;radius of the barrel;200mm</b><br/>
<br/>
This would create a new property with the name "ddRadius" in the group named "Barrel Properties" with a tooltip "radius of the barrel" and an initial value of 200 mm.<br/>
<br/>
<b>height;;height of the barrel;12cm</b><br/>
<br/>
Assuming you created the first example (barrel radius) above the empty bit between the 2 semicolons tells the workbench to use the existing group name.  Thus, you would have a new property with name "ddHeight" in the group named "Barrel Properties" with a tooltip "height of the barrel" and an initial value of 12 cm.<br/>
<br/>
<b>depth;base dimensions;;32.5</b><br/>
<br/>
New property has name = "ddDepth" in group name "base dimensions" with no tooltip and an initial value of 32.5 mm (assuming you are using mm as your default units).<br/>
<br/>
<b>length</b><br/>
<br/>
New property has name = "ddLength" in group named "DefaultGroup" (unless the group name default has been changed by previously naming a new group name for a previous property this session) with no tooltip and initial value of 0 (or suitable initial value for other property types).<br/>
<br/>
The initial value has some fairly good expression evaluation built-in, but it doesn't use the expression engine to do the evaluations.  It uses its own expression evaluator.  If it fails, no problem, you will get a warning message in the report view and status bar, and you can just set your desired value using the property editor.<br/>
<br/>
<b>diameter;;;25.4*20*2</b><br/>
<br/>
Sets new property name = "ddDiameter" using default group name, no tooltip, and setting initial value to 25.4 * 20 * 2, which could be useful if you wanted to set a diameter of 40 inches, given a radius of 20 inches and your default units is set for mm.<br/>
<br/>
Using group names to organize your properties can be very useful where you have lots of properties in your model.  There is no way at this time to edit group names; they must be given at the time the property is added to the container object.  Properties will be listed in alphabetical order within the group name heirarchy.<br/>
<br/>
Tooltips can be very useful as reminders to yourself (and to others) of the use of the property.  This information is displayed when the user hovers the mouse over the property.  You can also include multi-line descriptions in the form of StringList property types.  (List types can be set to initial values by separating the initial values with semicolons.)<br/>
<br/>
Here is an example of initializing a FloatList type with a list of floating point values.  First, select FloatList as the property type, then when naming the new property:<br/>
<br/>
<b>mylist;group name for lists;my tooltip;0;2;3.1;e;4</b><br/>
<br/>
<img src="Resources/media/list_example_scr.png" alt="list example screenshot">
<br/>
Did you notice the value 'e'?  This is one of the constants the built-in expression evaluator understands to mean Euler's constant, E, the root of natural logarithms: 2.718...  Other constants recognized: pi (3.14...), phi (aliases: golden, golden ratio = 1.6180339887), inch (aliases: in, inches = 2.54), and thou (0.0254).  You would use inches, inch, and thou by multiplying them by a value you enter in inches where your default units in FreeCAD is set as mm.  <br/>
<br/>
Example: <b>myInchValue;myGroup;myTip;10*inches</b> <br/>
<br/>
(But, if you use 'in' instead of inch or inches, just use it as you would normally in FreeCAD's expression engine: 6in or 6 in.)<br/>
<br/>

### Remove Property
<img src="Resources/icons/RemoveProperty.png" alt="icon"><br/>
<br/>
Use this tool to remove a property previously added using the Add Property tool.  Select the property in the list you would like to remove.  You may also choose to remove all properties in one go. <b>(Care must be taken when removing properties because this action cannot be undone.)</b><br/>
<br/>
<img src="Resources/media/remove_property_scr.png" alt="remove property screenshot"><br/>
<br/>
### Settings
<img src="Resources/icons/Settings.png" alt="icon">
Use this to change workbench settings.

#### Keep Toolbar
Setting this to True (default is True) means the DynamicData toolbar will remain active even after switching away from the DynamicData workbench.<br/>
<br/>
You must always open the DynamicData workbench at least once per FreeCAD session in order to first initialize the workbench toolbar.  If you would like to have the DynamicData toolbar icons always available without need to visit the DynamicData workbench you may configure DynamicData as your default startup workbench so that whenever you start FreeCAD it opens in the DynamicData workbench. (Edit -> Preferences -> General -> Startup -> Autoload module after startup -> DynamicData.)<br/>
<br/>
There is also an option in the Edit -> Preferences -> Start -> Options section to load DynamicData after creating / opening an existing document from the start page.<br/>
<br/>







#### Release notes: 

* v2018.09.19  2018.09.19:  Initial version
