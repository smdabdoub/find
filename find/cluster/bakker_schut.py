'''
Created on Mar 1, 2010

@author: shareef
'''
import util
import data.handle as dh

import numpy as np
from scipy.cluster.vq import kmeans2
import wx

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
        - numClusters: The number of clusters to form
            
    @rtype: tuple
    @return: A list where each element indicates the cluster membership of the 
        corresponding index in the original data and a message string
    """
    k = 1
    initClusters = 200
    msg = ''
    
    if 'numClusters' in kwargs.keys():
        k = int(kwargs['numClusters'])
    if 'initClusters' in kwargs.keys():
        initClusters = int(kwargs['numClusters'])
    
    #TODO: this transform should be moved to the transforms module (whenever I make it)
    # Log transform
    logData = np.log10(np.clip(data, a_min=0.00001, a_max=np.max(np.maximum.reduce(data))))
    
    # Choose large # (200 as suggested by authors) of non-random initial centers
    centers = util.kinit(logData, initClusters)
    
    # Run k-means
    _, ids = kmeans2(logData, np.array(centers), minit='matrix')
    
    # Merge clusters w/special comparison metric until user cluster # achieved
    clusters = util.separate(logData, ids)
    finalIDs = merge(k, ids, clusters)
    
    return finalIDs, msg
    

def merge(limit, ids, clusters, dist=None, minpair=None, newID=None):
    """
    Take a set of clusters and iteratively merge them together based on some 
    distance metric until the lower limit is reached.
    
    :@type limit: int
    :@param limit: The target number of clusters.
    :@type ids: list or array
    :@param ids: A list containing the cluster ID of each row of data.
    :@type clusters: list
    :@param clusters: A list of arrays, each containing the 
    """
    if (type(clusters) is not dict):
        tmp = {}
        for i, cluster in enumerate(clusters):
            tmp[i] = cluster
        clusters = tmp
        
    
    if len(clusters) <= limit:
        unique = np.unique(ids)
        saved = dict(zip(unique, range(len(unique))))
        # reassign cluster ids to a contiguous range
        for i, id in enumerate(ids):
            ids[i] = saved[id]
                
        return ids
    
    # calculate distance matrix
    if (dist is None):
        dist, minpair = distMatrix(clusters)
    else:
        dist, minpair = updateDistMatrix(clusters, dist, minpair, newID)
    
    # combine the two most similar clusters
    merged = dh.mergeData(minpair, clusters)
    
    # merge the minpair clusters and reassign their IDs to the new
    for i in minpair:
        del clusters[i]
    newID = np.max(ids) + 1
    clusters[newID] = merged
    
    for i, id in enumerate(ids):
        if id in minpair:
            ids[i] = newID 
    
    return merge(limit, ids, clusters, dist, minpair, newID)
    
    
        
    


def distMatrix(clusters):
    """
    Calculate the all-pairs distance matrix between the given clusters
    
    @type clusters: dict
    @param clusters:  The list of clusters to calculate the all-pairs distance 
                      matrix, keyed on cluster ID. The new cluster is assumed to be the last element. 
    @rtype: tuple
    @return: The all-pairs distance matrix and the pair with the overall minimum distance 
    """
    min = None; minpair = None
    dist = {}
    ids = np.sort(clusters.keys())
    for i in ids:
        dist[i] = {}
        for j in ids[i+1:ids.shape[0]]:
            dist[i][j] = util.nonSymmetricClusterDistance(clusters[i], clusters[j])
            if (min is None) or (dist[i][j] < min):
                min = dist[i][j]
                minpair = (i,j)
    
    return dist, minpair


def updateDistMatrix(clusters, matrix, remIDs, newID):
    """
    Selectively update the distance calculations by deleting the removed 
    clusters and adding calculations for the replacement cluster 
    
    :@type clusters: dict
    :@param clusters: The data split into clusters stored in numpy arrays, 
                      keyed on ID.
    :@type matrix: dict
    :@param matrix: A dict containing one dict for each cluster, keyed on the 
                    cluster id with the distance as the value.
    :@type remIDs: tuple
    :@param remIDs: The ids of the removed clusters.
    :@type newID: int
    :@param newID: The id of the replacement cluster.
    """
    # remove rows
    for i in remIDs:
        del matrix[i]
    
    for i in np.sort(clusters.keys()):
        # remove the old cluster distance calculations (columns)
        if i != newID:
            for j in remIDs:
                if j in matrix[i]:
                    del matrix[i][j]
            # calculate distances to the new cluster
            matrix[i][newID] = util.nonSymmetricClusterDistance(clusters[i], clusters[newID])
    
    # calculate the minpair: 
    # inner min finds the minpairs for each row, outer min finds overall minpair 
    minpair = min([(i,min(matrix[i], key=lambda z:matrix[i].get(z))) for i in matrix], 
                  key=lambda p: matrix.get(p[0]).get(p[1]))    
    
    # Add empty distance dict for later updates
    matrix[newID] = {}
    
    return matrix, minpair



#----------------------------------
# BAKKER SCHUT K-MEANS DIALOG CLASS
#----------------------------------
from cluster.util import ClusterOptionsDialog
from cluster.util import MAX_CLUSTERS
import display.formatters as f

class BakkerSchutKMeansDialog(ClusterOptionsDialog):
    """
    Provide an options dialog for the Bakker Schut k-means clustering algorithm 
    """
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Bakker Schut k-means Options', size=(300, 200))
        self.CenterOnParent()
        
        # create form controls
        self.txtNumClusters     = wx.TextCtrl(self, wx.ID_ANY, '', size=(50,20))
        self.txtNumInitClusters = wx.TextCtrl(self, wx.ID_ANY, '200', size=(50,20))
        
        # create a table of label-input controls
        self.formSizer = wx.FlexGridSizer(2, 2, vgap=20, hgap=10) #rows,cols,vgap,hgap
        self.formSizer.Add(wx.StaticText(self, -1, 'Number of final clusters:'), 1, wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtNumClusters, 1, wx.ALIGN_CENTER)
        self.formSizer.Add(wx.StaticText(self, -1, 'Number of starting clusters:'), 1, wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtNumInitClusters, 1, wx.ALIGN_CENTER)
        
        # create the button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL | wx.HELP)
        self.buttonSizer.AffirmativeButton.Bind(wx.EVT_BUTTON, super(BakkerSchutKMeansDialog, self).cmdOK_click)
        self.buttonSizer.HelpButton.Bind(wx.EVT_BUTTON, self.cmdHelp_Click)
        
        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.formSizer, 1, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.Add(self.getApplySizer(self), 0, wx.LEFT | wx.RIGHT | wx.TOP, 25)
        self.sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 10)
        self.SetSizer(self.sizer)
        
        
    def cmdHelp_Click(self, event):
        from display.help import HelpDialog
        HelpDialog(self, "Bakker Schut kmeans help", htmlfile="help/bakker_schut_kmeans_clustering.html").Show()
        
    
    def validate(self):
        intVal = f.IntFormatter()
        msg = []
        
        if not intVal.validate(self.txtNumClusters.Value):
            msg.append("Number of final clusters: A valid number must be entered.")
        else:
            val = int(self.txtNumClusters.Value)
            if val < 1 or val > MAX_CLUSTERS:
                msg.append("Number of clusters: A value between 1 and %d must be entered." % MAX_CLUSTERS)
        
        if not intVal.validate(self.txtNumInitClusters.Value):
            msg.append("Number of starting clusters: A valid number must be entered.")
        else:
            val = int(self.txtNumInitClusters.Value)
            if val < 10:
                msg.append("Number of starting clusters: A value greater than 10 must be entered")
        
        return msg
                

    
    def getMethodArgs(self):
        """
        Gather all options specified in the dialog.
        
        @rtype: dict
        @return: A dictionary of algorithm options.
        """
        options = {}
        options['numClusters'] = self._getNumClusters()
        options['numInitClusters'] = self._getNumInitClusters()
        return options
    
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
        options = {}
        options['numClusters'] = 'Number of final clusters'
        options['numInitClusters'] = 'Number of initial clusters'
        values = {}
        return (options, values)
        
        
    def _getNumClusters(self):
        """
        Retrieve the specified cluster target for the algorithm.
        
        @rtype: int
        @return: The final number of clusters the algorithm should settle on.
        """
        return int(self.txtNumClusters.GetValue())
    
    def _getNumInitClusters(self):
        """
        Retrieve the specified number of initial clusters the k-means algorithm should
        find.
        
        @rtype: int
        @return: The number of initial clusters the algorithm should find.
        """
        return int(self.txtNumInitClusters.GetValue())






def main():
    from data.io import loadDataFile
    f = loadDataFile('/data/537-Filter-Spin_MMC-Top.fcs')
    data = f[1]
    c = bakker_kMeans(data, numClusters=3)
    print c
    


if __name__ == "__main__":
    import sys
    sys.exit(main())
