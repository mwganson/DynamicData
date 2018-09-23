# DynamicData Workbench

#### Developer:
* Mark Ganson &lt;TheMarkster&gt;: mwganson at gmail (https://github.com/mwganson)  

#### Installation

Starting from FreeCAD 0.17 it can be <strike>installed via the [Addon Manager]</strike>(https://github.com/FreeCAD/FreeCAD-addons) (from Tools menu)

#### Overview

With this workbench you can create custom FeaturePython objects (herein referred to as DynamicData dd objects) to serve as containers for custom properties.  These custom properties can then be used in much the same way as cells in a spreadsheet.  For example, one can refer to a custom property in a sketcher constraint the same way one might refer to a cell in a spreadsheet.  Take note that FCStd files containing these DynamicData dd objects <b>can be shared</b> with other users who do not have the DynamicData workbench installed on there systems and yet will still remain fully functional.

In many cases the dd object can take the place of a spreadsheet, but they can also be used to augment spreadsheets.  Advantages of these objects:
<ul>
<li>Model parameters may be modified in a more interactive manner since the 3d view remains visible as the custom properties are edited.</li>
<li>The custom properties are more flexible than spreadsheet cells in that there are more property types available whereas spreadsheet cells are limited to float and string types.  Often there is a more suitable property type available, such as using an Angle type instead of generic float or an Integer instead of a float.  Others include Speed, Force, Volume, Area, Acceleration, Distance, Length, to name a few.</li>
<li>Full power of the FreeCAD Expression Engine is available, including unit conversion and handling.</li>
<li>Through the use of group naming one can better organize properties into groups, example: properties could be arranged by sketch name (e.g. Sketch002), by subassembly name (e.g. motor assembly, transmission assembly, gear drive, etc.), or in any other manner the designer chooses.</li>
<li>List types can be used (example FloatList) as a means of consolidating and reducing the total number of properties, which said list items can then be accessed via indexing (e.g. =dd.ddMyFloatList[3] within a sketch constraint would access the 4th (0-indexed) item in the list).  (Take note that at the time of this writing there is a bug in the spreadsheet module preventing it from accessing indexed list items and having the cell automatically update when the list property is changed.)</li>
<li>Tooltips may be created for the property at the time it is added to the container, which said tooltip can serve as documentation for the use of the property.</li>
<li>StringList properties can provide multi-line documentation, which can be expanded and read when desired, but which will remain otherwise collapsed down to a single property line when not needed.</li>
<li>When the Keep Toolbar setting is true (default: true) the DynamicData toolbar will "follow" you as you go from workbench to workbench, thus users will not need to return to the DynamicData workbench in order to add/remove custom properties.</li>
</ul>






#### Release notes: 

* v2018.09.19  2018.09.19:  Initial version
