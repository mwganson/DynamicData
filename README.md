# DynamicData Workbench
<img src="Resources/icons/DynamicDataLogo.png" alt="icon">

## Overview

With this workbench you can create custom FeaturePython objects (herein referred to as DynamicData dd objects) to serve as containers for custom properties.  These custom properties can then be used in much the same way as cells in a spreadsheet.  Users can refer to a custom property in a sketcher constraint (or from anywhere the Expression Engine can be accessed) the same way one might refer to a cell in a spreadsheet.  Take note that FCStd files containing these DynamicData dd objects <b>can be shared</b> with other users who do not have the DynamicData workbench installed on there systems and yet will still remain fully functional.  (But without the workbench installed those other users will not be able to add/remove properties unless it is done via scripting.)

## Commands

### Create Object
<img src="Resources/icons/CreateObject.png" alt="icon">
Creates a new DynamicData container object.

### Add Property
<img src="Resources/icons/AddProperty.png" alt="icon">
Adds a new custom property to the selected DynamicData container object.  (If no DynamicData object is selected in the tree view this command will be disabled.)<br/>
<br/>
Adding custom properties is a 2-step process.  First step is to select the property type from the drop down list.
<br/>
<img src="add_property_scr.png" alt="add property screenshot">
<br/>
<br/>
Second step is to give your new property a name and (optionally) a group name, tooltip, and initial value.
<img src="add_property_scr2.png" alt="add property screenshot 2">

### Remove Property
<img src="Resources/icons/RemoveProperty.png" alt="icon">

### Settings
<img src="Resources/icons/Settings.png" alt="icon">








#### Release notes: 

* v2018.09.19  2018.09.19:  Initial version
