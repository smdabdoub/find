"""
This module contains classes used for storing FACS data.

@author: Shareef Dabdoub
@organization: The Ohio State University
@organization: Nationwide Children's Hospital
"""

from operator import itemgetter

ID_DATA_ITEM = 0
ID_CLUSTERING_ITEM = 1
ID_TRANSFORMATION_ITEM = 2

class DataStore(object):
    """
    DataStore is meant to be used as a pseudo-database of FacsData objects.
    
    This class provides only class-level members so that it can be used without
    defining a specific instance or location.
    """
    _facsData = {}
    _selectedIndex = None
    
    def __init__(self):
        pass
    
    @classmethod
    def add(cls, data, id=None):
        """
        Adds a FacsData instance to the store.
        
        @type data: FacsData
        @param data: The new dataset to include in the store.
        """
        # set the ID for the data set
        if id is None:
            if cls._facsData:
                data.ID = cls.sortData()[-1][0] + 1
            else:
                data.ID = 0
        
        # add to the store 
        cls._facsData[data.ID] = data
        cls._selectedIndex = data.ID
        # update children list of parent
        if data.parent is not None:
            cls._facsData[data.parent].children.append(data.ID)
        
    @classmethod
    def addClustering(cls, methodID, clusterIDs, clusteringOpts):
        """
        Add a clustering of the currently selected data.
        
        @type methodID: int
        @param methodID: One of the L{cluster.methods} module-defined 
            ID_* constants for the available methods.
        @type clusterIDs: list
        @param clusterIDs:  A list where each element indicates the cluster 
            membership of the corresponding index in the original data.
        @type clusteringOpts: dict
        @param clusteringOpts: A dictionary of algorithm options.
        """
        cls._facsData[cls._selectedIndex].addClustering(methodID, clusterIDs, clusteringOpts)
    
    @classmethod
    def remove(cls, index):
        """
        Removes the FacsData instance at the specified index
        
        @type index: int
        @param index: The index of the FacsData instance to remove 
        """
        if (index in cls._facsData):
            fd = cls._facsData[index]
            # remove all children recursively
            for childID in fd.children:
                cls.remove(childID)
            # clear the children ID list
            del fd.children[:]
            # finally, delete the item itself
            del cls._facsData[index]
    
    @classmethod
    def removeAll(cls):
        """
        Removes all loaded data.
        """
        cls._facsData.clear()
        
    @classmethod
    def get(cls, key):
        return cls._facsData[key]

    @classmethod
    def getData(cls):
        """
        Retrieves all data in the store.
        
        @rtype: dict
        @return: A dictionary containing all the data currently in the store, keyed
                 on the data ID.
        """
        #print [(data.ID,data.filename) for data in cls._facsData.values()]
        return cls._facsData
    
    @classmethod
    def getCurrentDataSet(cls):
        """
        Retrieves the currently selected data set.
        
        @rtype: FacsData
        @return: The FacsData instance from the store as specified by the 
            currently selected index.
        """
        if (cls._selectedIndex is not None):
            try:
                cds = cls._facsData[cls._selectedIndex]
            except KeyError:
                cds = None
            
            return cds
    
    @classmethod
    def getCurrentIndex(cls):
        """
        Retrieves the index of the currently selected data set.
        
        @rtype: int
        @return: The index of the currently selected data set.
        """
        return cls._selectedIndex
    
    @classmethod
    def getToplevelParent(cls, index):
        parent = index
        
        while cls._facsData[parent].parent is not None:
            parent =  cls._facsData[parent].parent
            
        return cls._facsData[parent]
    
    @classmethod
    def selectDataSet(cls, index):
        """
        Set the currently selected data set to that of the given index.
        
        @type index: int
        @param index: The index of the data set to select.
        @rtype: FacsData
        @return: The specified FacsData instance.
        """
        if (index in cls._facsData):
            cls._selectedIndex = index
            return cls._facsData[cls._selectedIndex]

    @classmethod
    def size(cls):
        """
        Returns the number of data sets currently in the store.
        
        @rtype: int
        @return: The number of FacsData objects currently in the store.
        """
        return len(cls._facsData)
    
    @classmethod
    def view(cls):
        for id,data in cls.sortData():
            print data.filename
            print data.displayname
            print data.labels
            print data.selDims
            print '\tclusterings:'
            for i in data.clustering:
                print '\t\t-- methodID:',data.methodIDs[i]
                print '\t\t-- clusteringOpts:',data.clusteringOpts[i]
            print 

    @classmethod
    def sortData(cls):
        # sort the dict based on key (increasing [1 for decreasing?])
        return sorted(cls._facsData.iteritems(), key=itemgetter(0))


class FacsData(object):
    """
    The FacsData class holds all information regarding a single FACS dataset.
    """
    def __init__(self, filename, labels, data, annotations={}, analysis=None, parent=None):
        self.filename = filename
        self.displayname = filename
        self.labels = labels
        self.data = data
        self.annotations = annotations
        self.analysis = analysis
        self.ID = None
        self.parent = parent
        self.children = []
        self.selDims = []
        self.nodeExpanded = False
         
        #TODO: move all this to the Clustering class
        # Clustering information 
        self.methodIDs = {}
        self.clustering = {}
        self.clusteringOpts = {}
        self.clusteringSelDims = {}
        # TODO: move this to a dict keyed on ID in the tree class
        self.infoExpanded = {}       # an unpleasant hack to store the node state in the tree menu of the GUI
        
        self.selectedClustering = None
        
    
    def getDefaultTransform(self, dim=0):
        """
        Retrieves (if available) the amplification method (linear or log) 
        used in capturing the flow data.
        
        :@type dim: int
        :@param dim: The index of the desired dimension
        :@rtype: str
        :@return: The amplification method used for capture. None otherwise.
        """
        if 'defXform' in self.annotations:
            if type(self.annotations['defXform']) is list:
                if dim < len(self.annotations['defXform']):
                    return self.annotations['defXform'][dim]
            else:
                return self.annotations['defXform']
    
        
    def addClustering(self, methodID, clusterIDs, clusteringOpts, cID=None):
        """
        Adds an alternate clustering of the data.
        
        @type methodID: int
        @param methodID: One of the L{cluster.methods} module-defined ID_* constants for the available methods.
        @type clusterIDs: list
        @param clusterIDs:  A list where each element indicates the cluster membership of the 
            corresponding index in the original data.
        @type clusteringOpts: dict
        @param clusteringOpts: A dictionary of algorithm options.
        """
        clustID = cID if (cID is not None) else len(self.clustering)
        
        self.methodIDs[clustID] = methodID
        self.clustering[clustID] = clusterIDs
        self.clusteringOpts[clustID] = clusteringOpts
        self.infoExpanded[clustID] = False
        self.selectedClustering = clustID
        # copy the selDims array
        newSelDims = []
        for d in self.selDims:
            newSelDims.append(d)
        self.clusteringSelDims[clustID] = newSelDims
    
    
    def removeClustering(self, id):
        """
        Removes the specified clustering of the data.
        
        @type id: int
        @param id: The ID of the specific clustering to remove.
        """
        if (id in self.clustering):
            del self.methodIDs[id]
            del self.clustering[id]
            del self.clusteringOpts[id]
            del self.infoExpanded[id]
            del self.clusteringSelDims[id]
            if (self.selectedClustering == id):
                try:
                    self.selectedClustering = self.clustering.keys()[-1]
                except IndexError:
                    self.selectedClustering = None
    
                
    def getCurrentClustering(self):
        if (self.selectedClustering is not None):
            return self.clustering[self.selectedClustering]
            
    def selectClustering(self, id):
        """
        Sets the currently selected clustering.
        
        @type id: int
        @param id: The ID of the specific clustering to select.
        """
        if (id in self.clustering):
            self.selectedClustering = id

    CurrentClustering = property(getCurrentClustering, selectClustering,
                                 doc="""Property for dealing with the currently  
                                        selected clustering of this data set.""")
    
        
        

class Clustering(object):
    """
    This class represents a particular grouping of a data set into clusters
    of related events (n-dimensional points)
    """
    def __init__(self, ID, labels, methodID, opts, dims):
        self.ID = ID
        self.labels = labels
        self.methodID = methodID
        self.opts = opts
        self.selDims = dims
        
        
        
        
        
        
        


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
