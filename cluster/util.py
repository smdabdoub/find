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
import wx

import StringIO


MAX_CLUSTERS = 15



class ClusterOptionsDialog(wx.Dialog):
    """
    Provides a base options dialog to specify a consistent interface for
    retrieving data from clustering-related dialogs
    """
    
    def getMethodArgs(self): 
        """
        Gather all options specified in the dialog.
        
        @rtype: dict
        @return: A dictionary of algorithm options.
        """
        pass
    
    def getStrMethodArgs(self): 
        """
        Define an equivalency between the variable form of algorithm options 
        and the full string representation of the options.
        
        @rtype: tuple
        @return: A tuple containing:
            - A dictionary equating the short form of method option names
            with the full string descriptions.
            - A dictionary containing translations for any argument values
            that are not easily understandable
        """
        pass
    
    def validate(self): 
        """
        Validates user input to the dialog.
        
        :@rtype: list
        :@return: A list of strings, one for each validation error. Empty if no errors. 
        """
        pass
    
    def cmdOK_click(self, event):
        """
        Call the form validation method and display any error messages.
        """
        msg = self.validate()
        if len(msg) > 0:
            dlg = wx.MessageDialog(None, '\n'.join(msg), 
                                   'Invalid input', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        event.Skip()
    
    def getApplySizer(self, parent):
        self.chkApplyToCurrentSuplot = wx.CheckBox(parent, wx.ID_ANY, 'Apply to current subplot')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.chkApplyToCurrentSuplot)
        return sizer
    
    def isApplyChecked(self):
        return self.chkApplyToCurrentSuplot.GetValue()
    


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
        newFACSData = FacsData('', currFACSData.labels, newData, parent=currFACSData.ID)
        newFACSData.displayname = datasetName
        newFACSData.selDims = currFACSData.selDims
        
        DataStore.add(newFACSData)


import scipy.spatial.distance as ssd
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
    closestDistSq = ssd.cdist(np.reshape(centers[0],(1,data.shape[1])), data, 'sqeuclidean')
    currPot = np.sum(closestDistSq)

    # Choose the other centers
    for _ in range(k-1):
        bestNewPot = bestNewIndex = -1
        # repeat several trials
        for _ in range(numLocalTrials):
            randVal = random.random() * currPot
            for index in xrange(n):
                if (randVal <= closestDistSq[0,index]):                
                    break
                else:
                    randVal -= closestDistSq[0,index]
                    
            # Compute new potential
            newPot = np.sum(np.minimum(ssd.cdist(np.reshape(data[index],(1,data.shape[1])), data, 'sqeuclidean'), closestDistSq))
            
            # store best results
            if (bestNewPot < 0 or newPot < bestNewPot):
                bestNewPot, bestNewIndex = newPot, index
    
        centers.append (data[bestNewIndex])
        currPot = bestNewPot
        closestDistSq = np.minimum(ssd.cdist(np.reshape(data[bestNewIndex],(1,data.shape[1])), data, 'sqeuclidean'), closestDistSq)        

    return centers

def distSq(a, b):
    """
    Returns the squared distance between two n-dimensional points in 
    Euclidean space.
    
    Note: This method should only be used if speed is not an issue. 
          The distance calculation methods in scipy.spatial.distance
          are faster and provide more flexibility.
    
    @type a: numpy.ndarray
    @param a: A numpy array of size n representing a point in n-dimensional space.
    @type b: numpy.ndarray
    @param b: A numpy array of size n representing a point in n-dimensional space.
    
    @rtype: float
    @return: The distance squared between points p1 and p2.
    """
    diff = a-b
    return np.sum(diff*diff)



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
    #TODO: unique1d is deprecated
    clustIDs = np.unique1d(ids)
    return [data[ids==id] for id in clustIDs]


def nonSymmetricClusterDistance(c1, c2):
    """
    Determine a more accurate cluster distance than simple Euclidean distance
    between cluster centers. This method is implemented as described in 
    Bakker Schut et al., Cytometry 1992. The basic equation is:
    
    dc_i(C_1, C_2) = d_{ij} - (SVH_{i1} + SVL_{i1} + SVH_{i2} + SVL_{i2})
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
    
    c1Avg = [np.mean(c1[:,i]) for i in range(dims)]
    c2Avg = [np.mean(c2[:,i]) for i in range(dims)]
    
    c1SV = nsSpreadValue(c1, c1Avg)
    c2SV = nsSpreadValue(c2, c2Avg)
    
    # Subtract each 
    dist = np.sum([abs(c1Avg[i] - c2Avg[i]) - (c1SV['h'][i] + c1SV['l'][i] + c2SV['h'][i] + c2SV['l'][i])
                for i in range(dims)])

    return dist


def nsSpreadValue(c, avg):
    """
    Calculate modified (for nonsymmetric clusters) spread values for clusters  
    as defined in Bakker Schut et al., Cytometry 1992. These are two values 
    defined for each cluster for each dimension as: SD/sqrt(N) where N is the 
    number of events higher and lower (respectively) than the cluster average 
    and SD is the Std. Dev. for those events. 
    
    :@type c: list
    :@param c: The list of n-dimensional arrays corresponding to points in 
               the cluster
    :@type avg: list
    :@param avg: The dimension-wise averages for c
    
    :@rtype: dict
    :@return: A dict with keys 'h' and 'l' containing the high and low spread 
              values as n-dimensional lists
    """
    dims = c.shape[1]
    if c.shape[0] > 1:
        cHs   = [c[:,i][np.greater(c[:,i],avg[i])] for i in range(dims)]
        cLs   = [c[:,i][np.less(c[:,i],avg[i])] for i in range(dims)]    
        cSVHs = [0 if not len(cHs[i]) > 0 else np.std(cHs[i])/len(cHs[i])**.5 for i in range(dims)]
        cSVLs = [0 if not len(cLs[i]) > 0 else np.std(cLs[i])/len(cLs[i])**.5 for i in range(dims)]
    else:
        cSVHs = np.zeros(dims)
        cSVLs = np.zeros(dims)
        
    return {'h': cSVHs, 'l': cSVLs}
    


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
                dist = nonSymmetricClusterDistance(dstsep[i], srcsep[j])
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
                
                 

def main():
    from data.io import loadDataFile
    f = loadDataFile('/data/537-Filter-Spin_MMC-Top.fcs')
    data = f[1]
    kinit(data, 200)
    


if __name__ == "__main__":
    import sys
    sys.exit(main())



