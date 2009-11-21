"""
This module contains methods or interfaces to methods for automatic
data clustering. All algorithms should be called through the use of the 
C{cluster()} method so that a consistent return can be maintained.

@author: Shareef Dabdoub
@organization: The Ohio State University
@organization: Nationwide Children's Hospital
"""

import numpy
from scipy.cluster.vq import whiten, vq, kmeans, kmeans2
import Pycluster as pc
import random
import wx

__all__ = ['cluster','kmeans','kinit','ID_KMEANS']

#TODO: consider assigning these from a generator function starting well
#      outside the range of the beginning of the wx.NewId() range (100)
#      so as not to depend on the wx method for generating reliably static
#      method IDs.
ID_KMEANS = wx.NewId()
ID_AUTOCLASS = wx.NewId()

methods = {}

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
    Retrieve the list of available clustering algorithms in this module.
    
    @rtype: list of tuples
    @return: A list of tuples. Each tuple containing the following information in order:
        - method ID (int)
        - method name (string)
        - method description (string)
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

def kmeans(data, **kwargs):
    """
    Perform k-means clustering on unstructured N-dimensional data.
    
    @type data: array
    @param data: The data to be clustered
    @type kwargs: dict
    @param kwargs: The following args are accepted:
        - k: The number of clusters to form (returned number of clusters may be less than k).
        - npasses: The number of times the k-means clustering algorithm is performed, 
        each time with a different (random) initial condition.
        - method: describes how the center of a cluster is found: 
            - method=='a': arithmetic mean.
            - method=='m': median.
        - initialCenters: a set of points that should be used as the initial
                          cluster centers
            
    @rtype: tuple
    @return: A list where each element indicates the cluster membership of the 
        corresponding index in the original data and a message string
    """
    k = 1
    npasses = 1
    method = 'a'
    initialCenters = None
    smartCenters = False
    msg = ''
    
    if 'numClusters' in kwargs.keys():
        k = int(kwargs['numClusters'])
    if 'npasses' in kwargs.keys():
        npasses = int(kwargs['npasses'])
    if 'method' in kwargs.keys():
        method = kwargs['method']
    if 'initialCenters' in kwargs.keys():
        initialCenters = kwargs['initialCenters']
    if 'smartCenters' in kwargs.keys():
        smartCenters = kwargs['smartCenters']
        
    if not initialCenters:
        (clusterIDs, err, nOpt) = pc.kcluster(data, k, npass=npasses, method=method)
        msg = "Number of rounds optimal solution was found: %i" % nOpt
    else:
        print "Using manually chosen centers:\n", initialCenters
        (centroids, clusterIDs) = kmeans2(data, numpy.array(initialCenters), minit='matrix')
        print "Final centroids: ", centroids
    
    return clusterIDs, msg



methods[ID_KMEANS] = (ID_KMEANS, 'k-means', 
                      'Cluster the data using the k-means algorithm', 
                      kmeans, False)
#methods[ID_AUTOCLASS] = (ID_AUTOCLASS, 'AutoClass', 
#                         'Cluster the data using the AutoClass algorithm', 
#                         None, False)

