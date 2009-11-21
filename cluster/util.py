'''
Created on Aug 25, 2009

@author: shareef
'''
import data.handle as dh
from data.store import FacsData
from data.store import DataStore

import numpy
from numpy import random
import Pycluster as pc


def isolateClusters(selection, datasetName):
    """
    Create a new data set from a selection of clusters.
    
    @type selection: list
    @var selection: The indices of the clusters to be merged.
    @type datasetName: str
    @var datasetName: The display name for the new data set.
    """
    if (len(selection) > 0):
        currFACSData = DataStore.getCurrentDataSet()
        if (datasetName == ""):
            datasetName = currFACSData.displayname
        clusters = separate(currFACSData.data, currFACSData.getCurrentClustering())
        # merge selected clusters
        newData = dh.mergeData(selection, clusters)
        # assign new data set to the store
        newFACSData = FacsData('', currFACSData.labels, newData, currFACSData.ID)
        newFACSData.displayname = datasetName
        
        DataStore.add(newFACSData)


def kinit (data, k, numLocalTrials=10):
    """
    Attempts to choose optimal cluster centers for use with the k-means algorithm [Arthur 2007].
    
    Chooses a number of centers from the data set as follows:
        - One center is chosen randomly.
        - Now repeat numCenters-1 times:
            - Repeat numLocalTries times:
                - Add a point x with probability proportional to the distance squared 
                  from x to the closest existing center.
            - Add the point chosen above that results in the smallest potential.
            
    Concepts and some code from: U{http://blogs.sun.com/yongsun/entry/k_means_and_k_means}
    
    Original Paper: 
    
    D. Arthur and S. Vassilvitskii, B{k-means++: the advantages of careful seeding}, 
    Proceedings of the eighteenth annual ACM-SIAM symposium on Discrete algorithms,  
    New Orleans, Louisiana: Society for Industrial and Applied Mathematics, 2007, pp. 1027-1035.
    
    Original C++ implementation: U{http://www.stanford.edu/~darthur/}

    @type data: array
    @param data: The data points from which to choose centers.
    @type k: integer
    @param k: The number of centers to choose.
    @type numLocalTrials: integer
    @param numLocalTrials: The number of times to search for the best 
        potential when adding a new center.
    
    @rtype: list
    @return: A list of points representing pseudo-optimal cluster centers.
    """
    # init k seeds according to kmeans++
    n = data.shape[0]

    # Choose one random center and calc the distSq to the rest of the points
    centers = [data[random.randint(n)]]
    closestDistSq = []; currPot = 0
    for x in data:
        tmp = distSq(x-centers[0])
        closestDistSq.append(tmp)
        currPot += tmp

    # Choose the other centers
    for _ in range(k-1):
        bestNewPot = bestNewIndex = -1
        # repeat several trials
        for _ in range(numLocalTrials):
            randVal = random.random() * currPot
            for index in xrange(n):
                if (randVal <= closestDistSq[index]):                
                    break
                else:
                    randVal -= closestDistSq[index]
                    
            # Compute new potential
            newPot = sum([min(distSq(data[i], data[index]), closestDistSq[i]) for i in xrange(n)])
            
            # store best results
            if (bestNewPot < 0 or newPot < bestNewPot):
                bestNewPot, bestNewIndex = newPot, index
    
        centers.append (data[bestNewIndex])
        currPot = bestNewPot
        closestDistSq = [min(distSq(data[i], data[bestNewIndex]), closestDistSq[i]) for i in xrange(n)]        

    return centers


def distSq(p1, p2):
    """
    Returns the squared distance between two points in Euclidean space.
    
    Both points must have the same dimensionality.
    
    @type p1: list
    @param p1: A list of size n representing a point in n-dimensional space.
    @type p2: list
    @param p2: A list of size n representing a point in n-dimensional space.
    
    @rtype: float
    @return: The distance squared between points p1 and p2.
    """
    result = 0;
    for i in range(len(p1)):
        result += (p1[i] - p2[i])**2

    return result


def separate(data, ids):
    """
    Separates the data into different arrays for each cluster based on the given cluster membership list.
    
    @type data: array
    @param data: The original unstructured data.
    @type ids: list
    @param ids: A list the same size as B{data}, containing cluster membership identifiers. 
        These identifiers indicate which cluster the data point at the same index in B{data} belongs to.
    
    @rtype: list
    @return: A list of array objects representing clusters.
    """
    clustIDs = numpy.unique1d(ids)
    return [data[ids==id] for id in clustIDs]



def reassignClusterIDs(src, dst):
    """
    Given the cluster centers for two clusterings, determine the centers most 
    similar to each other and reassign the cluster ids to match.
    """
    srcFCS = DataStore.getData()[src[0]]
    dstFCS = DataStore.getData()[dst[0]]
    
    srcdata = srcFCS.data
    if srcFCS.selDims:
        srcdata = dh.filterData(srcFCS.data, srcFCS.selDims)
    srcids = srcFCS.clustering[src[1]]
    srccenters = pc.clustercentroids(srcdata, clusterid=srcids)[0]
    
    dstdata = dstFCS.data
    if dstFCS.selDims:
        dstdata = dh.filterData(dstFCS.data, dstFCS.selDims)
    dstids = dstFCS.clustering[dst[1]]
    dstcenters = pc.clustercentroids(dstdata, clusterid=dstids)[0]
    
    print "src centroids: ", srccenters
    print "dst centroids: ", dstcenters

    centerEQ = {}
    taken = []
    # Fill the map with the closest source center for each destination center
    for i,dc in enumerate(dstcenters):
        bestDist = -1
        for j,sc in enumerate(srccenters):
            if (j not in taken):
                dist = distSq(sc, dc)
                if (bestDist < 0) or (dist < bestDist):
                    bestDist = dist
                    centerEQ[i] = j
        taken.append(centerEQ[i])
    
    # Renumber the cluster IDs in the destination to match the IDs of the closest src center
    tmp = [centerEQ[id] for id in dstids]
    DataStore.getData()[dst[0]].clustering[dst[1]] = tmp
            
                
                
                 
            






