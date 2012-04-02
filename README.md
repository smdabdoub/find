Flow Investigation using N-Dimensions 
=====================================

FIND is a program designed for analysis and visualization of 
Flow Cytometry data. FIND focuses specifically on automated population 
discovery (clustering) methods.

The main website for FIND is:

http://www.justicelab.org/find

Executables are available for OS X and Windows. FIND runs on Linux, 
but must be run from the source. Instructions for installing/running 
on each platform are below.

Documentation for using FIND as well as developing plugins can be read at:

http://find.readthedocs.org/


## Installation Instructions

### OS X

Copy the 'find' folder from the disk image to your Applications directory or wherever 
else you want to run it from. Make sure to keep the plugins directory in the same 
folder as the find app.

Plugins can be installed by copying the related files 
to the appropriate subdirectory under the plugins directory.

### Windows

The main FIND executable is located at:
find/find.exe

The plugins folder is located at:
find/plugins

Plugins can be installed by copying the related files
to the appropriate subdirectory under the plugins directory.

### Linux

FIND requires Python 2.7 and recent versions of the following Python libraries to 
run:

1. numpy (1.5)
2. scipy (0.9.0)
3. matplotlib (1.0)
4. wxPython (2.8 or 2.9)
5. Pycluster (1.50)

The FIND application is run with the following command:

> $> python find.py

Plugins can be installed by copying the related files to the appropriate subdirectory 
under the plugins directory. Make sure to keep the 'find' folder in the same 
directory as the plugins folder.


---
Version 0.3 of FIND is released under the GPLv3.

Please address any comments or questions to:

Shareef M. Dabdoub, Ph.D.  
dabdoub.2@osu.edu
