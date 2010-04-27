'''
Created on Mar 1, 2010

@author: shareef
'''
import numpy as np
from scipy.cluster.vq import whiten, vq, kmeans, kmeans2
import Pycluster as pc

def kmeans(data, **kwargs):
    """
    Perform k-means clustering on unstructured N-dimensional data.
    
    @type data: array
    @param data: The data to be clustered
    @type kwargs: dict
    @param kwargs: The following args are accepted:
        - numClusters: The number of clusters to form (returned number of clusters may be less than k).
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
    
    
    logData = np.log10(np.clip(data, a_min=0.0001, a_max=np.max(np.maximum.reduce(data))))
    if not initialCenters:
        (clusterIDs, err, nOpt) = pc.kcluster(logData, k, npass=npasses, method=method)
        msg = "Number of rounds optimal solution was found: %i" % nOpt
    else:
        print "Using manually chosen centers:\n", initialCenters
        (centroids, clusterIDs) = kmeans2(logData, np.array(initialCenters), minit='matrix')
    
    return clusterIDs, msg