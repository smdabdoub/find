'''
Created on Aug 25, 2009

@author: shareef
'''
import data.handle as dh
from data.store import FacsData
from data.store import DataStore

import numpy as np
from numpy import random
import Pycluster as pc

import StringIO


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
        closestDistSq.append(distSq(x,centers[0]))
        currPot += closestDistSq[-1]

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

memo = {}
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
    global memo
    result = 0
    for i in range(len(p1)):
        sub = p1[i] - p2[i]
        if sub in memo:
            result += memo[sub]
        else:
            memo[sub] = sub**2
            result += memo[sub]

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
    clustIDs = np.unique1d(ids)
    return [data[ids==id] for id in clustIDs]


def nonSymmetricClusterDistance(c1, c2):
    """
    Determine a more accurate cluster distance than simple Euclidean distance
    between cluster centers. This method is implemented as described in 
    Bakker Schut et al., Cytometry 1992. The basic equation is:
    
    dc_i(C_1, C_2) = d_{ij} - (SVH_{i1} + SVL_{i1} + SVH_{i2} + SVL_{i2}
    d_{ij} = | avg_i1 - avg_i2 |
    
    The original purpose was to effect a cluster joining criterion that would 
    decrease with the number of particles to avoid large clusters absorbing
    smaller outlying clusters. Also, that neighboring less dense clusters
    would be readily merged. [Bakker Schut 1992]
    
    @type c1: array
    @param c1: A cluster from the data
    @type c2: array
    @param c2: A cluster from the data 
    
    @rtype: float
    @return: The distance between the two clusters as calculated by the algorithm
    """
    dims = c1.shape[1]
    
    # Calculate modified spread values. These are two values defined for each 
    # cluster for each dimension as: SD/sqrt(N) where N is the number of events 
    # higher and lower (respectively) than the cluster average
    c1Avg = [np.mean(c1[:,i]) for i in range(dims)]
    c2Avg = [np.mean(c2[:,i]) for i in range(dims)]
    
    # SVH: Spread Value High, SVL: Spread Value Low
    c1SVHs = [np.std(c1[:,i])/len(c1[:,i][np.greater(c1[:,i],c1Avg[i])])**.5 
              for i in range(dims)]
    c1SVLs = [np.std(c1[:,i])/len(c1[:,i][np.less(c1[:,i],c1Avg[i])])**.5 
              for i in range(dims)]

    c2SVHs = [np.std(c2[:,i])/len(c2[:,i][np.greater(c2[:,i],c2Avg[i])])**.5 
              for i in range(dims)]
    c2SVLs = [np.std(c2[:,i])/len(c2[:,i][np.less(c2[:,i],c2Avg[i])])**.5 
              for i in range(dims)]
    
    # Subtract each 
    dist = sum([abs(c1Avg[i] - c2Avg[i]) - (c1SVHs[i] + c1SVLs[i] + c2SVHs[i] + c2SVLs[i])
                for i in range(dims)])
    
    print dist

    return dist


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
    
    srcsep = separate(srcdata, srcids)
    dstsep = separate(dstdata, dstids)

    centerEQ = {}
    taken = []
    # Fill the map with the closest source center for each destination center
    for i,dc in enumerate(dstcenters):
        bestDist = -1
        for j,sc in enumerate(srccenters):
            if (j not in taken):
                dist = nonSymmetricClusterDistance(dstsep[i], srcsep[j])#distSq(sc, dc)
                if (bestDist < 0) or (dist < bestDist):
                    bestDist = dist
                    centerEQ[i] = j
        taken.append(centerEQ[i])
    
    # Renumber the cluster IDs in the destination to match the IDs of the closest src center
    tmp = [centerEQ[id] for id in dstids]
    DataStore.getData()[dst[0]].clustering[dst[1]] = tmp
            

def clusteringInfo(fData, id):
        """
        Creates a single string representing in a human-readable manner, the
        options used to perform a particular clustering.
        
        @type fData: FacsData
        @param fData: A FacsData instance containing the specified clustering 
        @type id: int
        @param id: The id of a clustering within the FacsData instance.
        @rtype: str
        @return: An easily understandable string representation of clustering options.
        """
        from cluster.dialogs import getClusterDialog
        dlg = getClusterDialog(fData.methodIDs[id], None)
        strOpts, strValues = dlg.getStrMethodArgs()
        dlg.Destroy()
        opts = fData.clusteringOpts[id]
        info = StringIO.StringIO()
        # create info string
        for opt in opts:
            info.write(strOpts[opt])
            info.write(': ')
            if (opt in strValues):
                info.write(strValues[opt][opts[opt]])
            else:
                info.write(opts[opt])
            info.write('\n')
        
        return info.getvalue()
                
                 
            






