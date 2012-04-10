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

### Windows

The zip file contains a self-extracting installer that will guide you through the installation 
process. Once FIND has been installed, the main executable is located at:

<install dir.>/find.exe

and the plugins folder is located at:
<install dir.>/plugins

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

## Plugins

FIND provides an API for programmers to extend the functionality of the application. 
Documentation and examples on creating plugins for use with FIND can be found at:

http://find.readthedocs.org/en/latest/devman/index.html

Currently all plugins are available for download on the official website at:

http://www.justicelab.org/find/plugins/

If you would like to publish a FIND plugin on the official site, please use the contact 
information at the end of this document.

New plugins can be installed by copying the related files to the appropriate subdirectory 
under the plugins directory. Make sure to keep the plugins directory in the same location 
as the find executable (find.py in the case of *nix).


---
Version 0.3 of FIND is released under the GPLv3.

Please address any comments or questions to:

Shareef M. Dabdoub, Ph.D.  
dabdoub.2@osu.edu
