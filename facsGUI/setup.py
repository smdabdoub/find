"""
This file is used to generate standalone packaged "executables" for both 
the Windows and OS X operating systems through use of py2exe and py2app 
respectively 

Usage:
    python setup.py py2exe
    OR
    python setup.py py2app
"""
import sys
if sys.platform == "win32":
    from distutils.core import setup
    import py2exe
    
    import matplotlib
    
    setup(
        windows=[{"script" : "find.py"}],
        options={'py2exe': {'includes' : ['matplotlib.backends', 'matplotlib.figure', 'numpy', 'matplotlib.backends.backend_wxagg'],
                            'excludes': ['_gtkagg', '_tkagg', '_agg2', '_cairo', '_cocoaagg', '_fltkagg', '_gtk', '_gtkcairo'],
                            'dll_excludes': ['libgdk-win32-2.0-0.dll', 'libgdk-pixbuf-2.0-0.dll', 'libgobject-2.0-0.dll']}
                            },
        data_files=matplotlib.get_py2exe_datafiles()
    )

if sys.platform == "darwin":
    from setuptools import setup
    
    APP = ['find.py']
    DATA_FILES = []
    OPTIONS = {'argv_emulation': False}
    
    setup(
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
