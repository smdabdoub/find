"""
This module contains methods or interfaces to methods for automatic
data clustering. All algorithms should be called through the use of the 
C{cluster()} method so that a consistent return can be maintained.

@author: Shareef Dabdoub
@organization: The Ohio State University
@organization: Nationwide Children's Hospital
"""
import bakker_schut
import kmeans

import wx

ID_KMEANS = wx.NewId()
ID_BAKKER_SCHUT = wx.NewId()
ID_AUTOCLASS = wx.NewId()

methods = {}
methods['kmeans'] = (ID_KMEANS, 'kmeans', 'k-means', 
                      'Cluster the data using the k-means algorithm', 
                      kmeans.kmeans, False)
methods['bskmeans'] = (ID_BAKKER_SCHUT, 'bskmeans', 'Bakker Schut k-means', 
                            """Cluster the data using the variant of the 
                               k-means algorithm designed for use with Flow 
                               Cytometry data and published by Bakker Schut 
                               et. al.""", 
                            bakker_schut.bakker_kMeans, False)
#methods['autoclass'] = (ID_AUTOCLASS, 'autoclass', 'AutoClass', 
#                         'Cluster the data using the AutoClass algorithm', 
#                         None, False)


def addPluginMethod(descriptor):
    """
    Adds a clustering method to the list of available methods.
    
    @var descriptor: A tuple containing the method ID, short name, 
                     description, function reference, and plugin flag (True
    """
    global methods
    methods[descriptor[1]] = descriptor
    

def getAvailableMethods():
    """
    Retrieve the list of available clustering algorithms in this module.
    
    @rtype: list of tuples
    @return: A list of tuples. Each tuple containing the following information in order:
        - method ID (int)
        - method name (string)
        - method description (string)
    """
    return methods


def _getMethodTuple(id):
    """
    Acts as a central location for retrieving information on methods.
    
    Note: Only meant for use by methods in this module.
    """
    try:
        id = strID(int(id))
    except ValueError:
        pass
        
    if id in methods:
        return methods[id]



def strID(intID):
    """
    Get the string ID of a clustering method by its int ID.
    
    @type id: int
    @param id: One of the module-defined ID_* constants for the available methods.
    @rtype: string
    @return: The string ID of the specified clustering algorithm
    """
    for id in methods:
        if methods[id][0] == intID:
            return methods[id][1]
        


def getStringRepr(id):
    """
    Get the name of a clustering method by its ID.
    
    @type id: int
    @param id: One of the module-defined ID_* constants for the available methods.
    @rtype: string
    @return: The name of the specified clustering algorithm
    """
    t = _getMethodTuple(id)
    if t is not None:
        return t[2]



def getMethod(id):
    """
    Retrieve a plotting method by its ID.
    
    :@type id: int or str
    :@param id: The identifier for a plotting method. An int id is required
                for the wx event subsystem, but a string id is required as a 
                unique id for plugin authors to specify dependencies on 
                plotting methods.
    :@rtype: method
    :@return: The method associated with the ID, or None.
    """
    t = _getMethodTuple(id)
    if t is not None:
        return t[-2]
    
       

def cluster(id, data, **kwargs):
    """
    Intended to be a pass-through interface for performing different clustering algorithms.
    
    @type id: int or str
    @param id: Specifies the type of clustering algorithm to use.
    @type data: numpy array
    @param data: The data to be clustered.
    @type kwargs: dict
    @param kwargs: Used to pass any arguments specific to a clustering algorithm.
        See the clustering algorithm method signatures for necessary arguments.
        Optional arguments can be found in the documentation for those methods.
    
    @rtype: tuple
    @return: A list where each element indicates the cluster membership of the 
        corresponding index in the original data and a string message
    """
    method = getMethod(id)
    return method(data, **kwargs)


