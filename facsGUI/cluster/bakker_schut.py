'''
Created on Mar 1, 2010

@author: shareef
'''
import util
import data.handle as dh

import numpy as np
from scipy.cluster.vq import whiten, vq, kmeans, kmeans2

def bakker_kMeans(data, **kwargs):
    """
    This is an implementation of the k-means algorithm designed specifically
    for flow cytometry data in the following paper:
    
    T.C.B. Schut, B.G.D. Grooth, and J. Greve, 
    "Cluster analysis of flow cytometric list mode data on a personal computer", 
    Cytometry,  vol. 14, 1993, pp. 649-659.

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
    msg = ''
    
    if 'numClusters' in kwargs.keys():
        k = int(kwargs['numClusters'])
    
    #TODO: this transform should be moved to the transforms module (whenever I make it)
    # Log transform
    logData = np.log10(np.clip(data, a_min=0.0001, a_max=np.max(np.maximum.reduce(data))))
    
    # Choose large # of non-random initial centers
    init = 200  # as suggested by the authors
    centers = util.kinit(logData, init)
    
    # Run k-means
    _, ids = kmeans2(logData, np.array(centers), minit='matrix')
    
    # Merge clusters w/special comparison metric until user cluster # achieved
    clusters = util.separate(logData, ids)
    final = merge(k, ids, clusters)
    
    return final, msg


def seedCenters(k, data):
    """
    """
    centers = [data[0]]
    
    for d in data:
        pass
    

def merge(limit, ids, clusters, dist=None):
    """
    Take a set of clusters and iteratively merge them together based on some 
    distance metric until the lower limit is reached
    """
    if len(clusters) <= limit:
        saved = dict(zip(np.unique(ids), range(len(clusters))))
        # reassign cluster ids to a contiguous range
        for i, id in enumerate(ids):
            ids[i] = saved[id]
                
        return ids
    
    # calculate distance matrix
    if (dist is None):
        dist, minpair = distMatrix(clusters)
    
    # combine the two most similar clusters
    merged = dh.mergeData(minpair, clusters)
    
    for i in minpair:
        del clusters[i]
    clusters.append(merged)
    newID = len(clusters) - 1
    
    for i, id in enumerate(ids):
        if id in minpair:
            ids[i] = newID 
    
    merge(limit, clusters, ids)
    
    
        
    


def distMatrix(clusters):
    """
    Calculate the all-pairs distance matrix between the given clusters
    
    @type clusters: list
    @param clusters:  The list of clusters to calculate the all-pairs distance matrix
    @rtype: tuple
    @return: The all-pairs distance matrix and the pair with the overall minimum distance 
    """
    n = len(clusters)
    min = -1; minpair = None
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            dist[i,j] = util.nonSymmetricClusterDistance(clusters[i], clusters[j])
            if min < 0 or dist[i,j] < min:
                min = dist[i,j]
                minpair = (i,j)
    
    return dist, minpair