'''
This module provides a central location for storage and retrieval of methods
for data transformations. 

@author: Shareef Dabdoub
'''
from transforms.log import log
from matplotlib import scale as mscale
import wx

methods = {}
methods['log'] = ('log', wx.NewId(), 'Logarithmic Transform', 
                  'Transforms data to a logarithmic scale', log, None, False)

def addPluginMethod(descriptor):
    """
    Adds a transform method to the list of available methods.
    
    :@type descriptor: tuple
    :@param descriptor: Each tuple contains the following information in order:
        - ID (str)
        - ID (int)
        - name (string)
        - description (string)
        - transform method
        - scale class (if applicable)
    """
    global methods
    descriptor = list(descriptor)
    descriptor.append(True)
    methods[descriptor[0]] = tuple(descriptor)
    
    # custom scales are available, see:
    # http://matplotlib.sourceforge.net/examples/api/custom_scale_example.html
    if descriptor[-2] is not None:
        mscale.register_scale(descriptor[-2])
    

def AvailableMethods():
    """
    Retrieve the list of available plotting algorithms in this module.
    
    @rtype: list of tuples
    @return: A list descriptor (:@see: addPluginMethod) tuples for each registered method. 
    """
    return methods

def getMethod(id):
    """
    Retrieve a plotting method by its ID.
    
    :@type id: int or str
    :@param id: The identifier for a transformation method. An int id is required
                for the wx event subsystem, but a string id is required as a 
                unique id for plugin authors to specify dependencies.
    :@rtype: method
    :@return: The method associated with the ID, or None.
    """
    try:
        int(id)
    except ValueError:
        return methods[id][-3]
        
    return methods[strID(id)][-3]


def strID(methodID):
    """
    Get the name of a plotting method by its ID.
    
    @type methodID: int
    @param methodID: One of the module-defined ID_* constants for the available methods.
    @rtype: string
    @return: The name of the specified plotting algorithm
    """
    if (methodID is not None):
        for id in methods:
            if methods[id][1] == methodID:
                return methods[id][0]