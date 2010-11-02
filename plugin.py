'''
Created on Jul 30, 2009

@author: shareef
'''
import error

import wx

import os.path
import sys

pluginTypes = ['analysis', 'cluster', 'graph', 'IO', 'transforms']
loaded = dict([(type_, []) for type_ in pluginTypes])

def discoverPlugins():
    """
    Adds the plugins directory to the system path and interrogates it for 
    available plugins in the folders named in the module global pluginTypes list.
    
    :@raise error.PluginError: If the main plugin directory or any subdirectories are missing.
    :@rtype: dict
    :@return: A dictionary of plugins keyed on their type.
    """
    availablePlugins = {}
    pluginDir = 'plugins'
    #basePluginPath = sys.path[0]
    if sys.platform == 'win32':
        basePluginPath = sys.path[0].split('library.zip')[0]
    if sys.platform == 'darwin':
        basePluginPath = sys.path[0].split('find.app')[0]
    
    # make sure the plugins folder exists
    if not os.path.exists(os.path.join(basePluginPath, pluginDir)):
        raise error.PluginError("The \"plugins\" directory is missing, please place in the same folder as the FIND program file.")
        return
    
    if not basePluginPath in sys.path:
        sys.path.insert(0, basePluginPath)
    
    #TODO: look at recursive descent for module discovery
    # Accumulate available plugin modules
    errMsg = []
    for type_ in pluginTypes:
        path = os.path.join(basePluginPath, pluginDir, type_)
        if not os.path.exists(path):
            errMsg.append("The \"%s\" plugins directory is missing." % type_)
        else:
            availablePlugins[type_] = [fname[:-3] for fname in os.listdir(path) 
                                                  if fname.endswith(".py") and 
                                                   not fname.startswith("__init__")]
    
    # raise error with all missing plugin subdirectories
    if len(errMsg) > 0:
        raise error.PluginError('\n\t'.join(errMsg))
        return
    
    return availablePlugins

    
def importPlugins(plugins):
    """
    Imports the supplied plugins, storing their names in the module global
    'loaded' dictionary.
    
    :@type plugins: dict
    :@var plugins: A dictionary of available plugin files for import, 
                  keyed on plugin type.
    """
    global loaded
    for type_ in plugins:
        # typeMods will be a module reference containing all the modules for type_
        # Eg. module xcluster. Then typeMods.xcluster will be available.
        typeMods = __import__(''.join(['plugins.', type_]), fromlist=plugins[type_])
        for plugin in plugins[type_]:
            try:
                loaded[type_].append(eval('.'.join(['typeMods',plugin])))
            except Exception, err:
                sys.stderr.write("PLUGIN IMPORT ERROR:\n%s" % str(err))
    
    

import analysis.methods as aMthds
import cluster.dialogs as cDlgs
import cluster.methods as cMthds
from data import io
import plot.dialogs as pDlgs
import plot.methods as pMthds
import transforms.methods as tm
    
#TODO: move the special handling code for each plugin type to separate methods
def addPluginFunctionality(parent):
    """
    The main function of this method is to scan through all the discovered
    plugins and make the valid plugins available to FIND through the plugin
    architecture.
    
    As a by-product, each valid plugin is added to the Plugins menu on the 
    main menubar that this method also creates. All plugins are added, but 
    not all are available for interaction through the menu. These plugins 
    are disabled and are added only to inform the user that they were loaded.
    
    :@type parent: wx.Window
    :@param parent: The main FIND window 
    """
    pluginsMenu = wx.Menu()
    submenus = {}
    for type_ in pluginTypes:
        submenus[type_] = wx.Menu()
    
    # Add loaded plugins to the submenus
    for type_ in loaded:
        for module in loaded[type_]:
            try:
                pluginMethods = module.__all__
            # skip this module if it does not define __all__
            except AttributeError:
                continue
            # Handle special cases for various types
            
            # Analysis plugins
            if type_ == pluginTypes[0]:
                for method in pluginMethods:
                    aID = wx.NewId()
                    amethod, fIndependent = eval('module.'+method)()
                    doc = amethod.__doc__.split(';')
                    strID = doc[0].strip()
                    name = doc[1].strip()
                    descr = doc[2].strip()
                    aMthds.addPluginMethod((strID, aID, name, descr, amethod, True))
                    # Create the menu item
                    aitem = wx.MenuItem(submenus[type_], aID, name, descr)
                    if not fIndependent: 
                        aitem.Enable(False)
                    submenus[type_].AppendItem(aitem)
                    parent.Bind(wx.EVT_MENU, parent.OnAnalyze, id=aID)
            # Clustering plugins
            elif type_ == pluginTypes[1]:
                for method in pluginMethods:
                    cID = wx.NewId()
                    cmethod, cdialog = eval('module.'+method)()
                    doc = cmethod.__doc__.split(';')
                    name = doc[0].strip()
                    descr = doc[1].strip()
                    cMthds.addPluginMethod((cID, name, descr, cmethod, True))
                    cDlgs.addPluginDialog(cID, cdialog)
                    # Create the menu item
                    submenus[type_].Append(cID, name, descr)
                    parent.Bind(wx.EVT_MENU, parent.OnCluster, id=cID)
            # Plotting plugins
            elif type_ == pluginTypes[2]:
                for method in pluginMethods:
                    pID = wx.NewId()
                    pmethod, pdialog, dtypes = eval('module.'+method)()
                    doc = pmethod.__doc__.split(';')
                    strID = doc[0].strip()
                    name  = doc[1].strip()
                    descr = doc[2].strip()
                    pMthds.addPluginMethod((strID, pID, name, descr, pmethod, dtypes, True))
                    pDlgs.addPluginDialog(strID, pdialog)
                    # Create a disabled menu item to indicate plugin was loaded
                    item = wx.MenuItem(submenus[type_], pID, name, descr)
                    item.Enable(False)
                    submenus[type_].AppendItem(item)
            # I/O plugins
            elif type_ == pluginTypes[3]:
                for method in pluginMethods:
                    name, cls = eval('module.'+method)()
                    ci = cls('')
                    descr = ' '.join(name, 'plugin') if ci.__doc__ is None \
                            else ci.__doc__.strip().split('\n')[0]
                    io.addPluginMethod((name, wx.NewId(), cls, True))
                    # Create a disabled menu item to indicate plugin was loaded
                    item = wx.MenuItem(submenus[type_], wx.ID_ANY, name, descr)
                    item.Enable(False)
                    submenus[type_].AppendItem(item)
            # Transforms plugins
            elif type_ == pluginTypes[4]:
                pID = wx.NewId()
                tmethod, tscaleClass = eval('module.'+method)()
                doc = tmethod.__doc__.split(';')
                strID = doc[0].strip()
                name  = doc[1].strip()
                descr = doc[2].strip()
                tm.addPluginMethod((strID, pID, name, descr, tmethod, tscaleClass))
            
 
    # Add submenus to main menu
    for type_ in pluginTypes:
        if type_ == 'IO':
            pluginsMenu.AppendSubMenu(submenus[type_], type_)
        else:
            pluginsMenu.AppendSubMenu(submenus[type_], type_.capitalize())
            
    return pluginsMenu

