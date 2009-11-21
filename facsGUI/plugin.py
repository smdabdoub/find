'''
Created on Jul 30, 2009

@author: shareef
'''

import imp
import os
import os.path
import sys

pluginTypes = ['cluster', 'analysis', 'stats', 'graph', 'IO']
loaded = dict([(type_, []) for type_ in pluginTypes])

def discoverPlugins():
    """
    Adds the plugins directory to the system path and interrogates it for 
    available plugins in the folders named in the module global pluginTypes list.
    
    @rtype: dict
    @return: A dictionary of plugins keyed on their type.
    """
    # TODO: Figure out what the path looks like on Win and add cases.
    availablePlugins = {}
    pluginDir = 'plugins'
    #basePluginPath = sys.path[0]
    if sys.platform == 'win32':
        basePluginPath = sys.path[0].split('library.zip')[0]
    if sys.platform == 'darwin':
        basePluginPath = sys.path[0].split('find.app')[0]
    
    if not basePluginPath in sys.path:
        sys.path.insert(0, basePluginPath)
    
    #TODO: look at recursive descent for module discovery
    # Accumulate available plugin modules
    for type_ in pluginTypes:
        path = os.path.join(basePluginPath, pluginDir, type_)
        availablePlugins[type_] = [fname[:-3] for fname in os.listdir(path) 
                                              if fname.endswith(".py") and 
                                               not fname.startswith("__init__")]
    return availablePlugins

    
def importPlugins(plugins):
    """
    Imports the supplied plugins, storing their names in the module global
    'loaded' dictionary.
    
    @type plugins: dict
    @var plugins: A dictionary of available plugin files for import, 
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
    
    



