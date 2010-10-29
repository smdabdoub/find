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
methods[ID_KMEANS] = (ID_KMEANS, 'k-means', 
                      'Cluster the data using the k-means algorithm', 
                      kmeans.kmeans, False)
methods[ID_BAKKER_SCHUT] = (ID_BAKKER_SCHUT, 'Bakker Schut k-means', 
                            """Cluster the data using the variant of the 
                               k-means algorithm designed for use with Flow 
                               Cytometry data and published by Bakker Schut 
                               et. al.""", 
                            bakker_schut.bakker_kMeans, False)
#methods[ID_AUTOCLASS] = (ID_AUTOCLASS, 'AutoClass', 
#                         'Cluster the data using the AutoClass algorithm', 
#                         None, False)


def addPluginMethod(descriptor):
    """
    Adds a clustering method to the list of available methods.
    
    @var descriptor: A tuple containing the method ID, short name, 
                     description, function reference, and plugin flag (True
    """
    global methods
    methods[descriptor[0]] = descriptor
    

def getAvailableMethods():
    """
    Retrieve the available clustering algorithms in this module.
    
    @rtype: dict of tuples
    @return: A dict of tuples keyed on the int method ID. Each tuple contains
             the following information in order:
        - method ID (int)
        - method name (string)
        - method description (string)
        - method
        - plugin flag
    """
    return methods

def getStringRepr(methodID):
    """
    Get the name of a clustering method by its ID.
    
    @type methodID: int
    @param methodID: One of the module-defined ID_* constants for the available methods.
    @rtype: string
    @return: The name of the specified clustering algorithm
    """
    if (methodID is not None):
        return methods[methodID][1]
    

def cluster(clusterType, data, **kwargs):
    """
    Intended to be a pass-through interface for performing different clustering algorithms.
    
    @type clusterType: integer
    @param clusterType: Specifies the type of clustering algorithm to use. 
        Module pre-defined constants such as ID_KMEANS can be used. 
    @type data: array
    @param data: The data to be clustered.
    @type kwargs: dict
    @param kwargs: Used to pass any arguments specific to a clustering algorithm.
        See the clustering algorithm method signatures for necessary arguments.
        Optional arguments can be found in the documentation for those methods.
    
    @rtype: tuple
    @return: A list where each element indicates the cluster membership of the 
        corresponding index in the original data and a string message
    """
    method = methods[clusterType][3]
    return method(data, **kwargs)


