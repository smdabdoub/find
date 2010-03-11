from __future__ import with_statement
"""
"""
from data.store import DataStore, FacsData
from IO import fcs
from error import UnknownFileType 

import numpy as np
import wx

import os

FILE_INPUT = True
FILE_OUTPUT = False

methods = {}
methods['fcs'] = ('fcs', wx.NewId(), fcs.FCSreader, False)
#methods['csv'] = ('csv', loadCSV, FILE_INPUT, 'Comma Separated Values (*.csv)|*.csv', False)

def loadDataFile(filename):
    """
    Loads the given file by choosing the appropriate loading method, 
    and returns a tuple containing the column labels and the data matrix.
    
    @type filename: string
    @var filename: The path to a Flow Cytometry data file.
    @rtype: tuple
    @return: The column labels and the event data in a tuple.
    """
    fileType = filename.split('.')[-1]
    
    if (fileType in methods):
        c = methods[fileType][2](filename)
        return c.register()[FILE_INPUT]()
    
    raise UnknownFileType(filename)


#TODO: implement
def exportDataFile(eID, facs):
    """
    Passes the given FacsData instance to the specified IO class.
    
    :@type eID: int
    :@param eID: The int ID associated with the user-selected export format.
    :@type facs: data.store.FacsData
    :@param facs: The FacsData instance that will be handed to the IO method.
    """
    pass


def addPluginMethod(descriptor):
    """
    Adds an I/O method to the list of available methods.
    
    :@type descriptor: tuple
    :@param descriptor: A descriptor tuple as described in AvailableMethods()
    """
    global methods
    methods[descriptor[0]] = descriptor
    
def AvailableMethods():
    """
    Retrieve the list of available I/O methods in this module.
    
    @rtype: list of tuples
    @return: A list of descriptors with the following in order:
        - ID (str)
        - method
        - I/O ID: method is meant to input or output files (FILE_INPUT or FILE_OUTPUT)
        - file type (str): 'File type description (*.extension)|*.extension'
        - plugin flag
    """
    return methods

def getMethod(id):
    """
    Retrieve an I/O class by its ID.
    
    :@type id: int or str
    :@param id: The identifier for an I/O class.
    :@rtype: class
    :@return: The class associated with the ID, or None.
    """
    try:
        int(id)
    except ValueError:
        return methods[id][2]
        
    return methods[strID(id)][2]
    
    
def strID(methodID):
    """
    Get the sting ID  method by its ID.
    
    @type methodID: int
    @param methodID: One of the module-defined ID_* constants for the available methods.
    @rtype: string
    @return: The name of the specified plotting algorithm
    """
    if (methodID is not None):
        for id in methods:
            if methods[id][1] == methodID:
                return methods[id][0]


#from IO.dbdict import dbopen
import shelve
def saveState(dir, filename, plots, currentPlotID, selectedAxes, grid):
    """
    Save a representation of the system state: All the loaded data sets, 
    their clusterings, any transformations or analyses (future), 
    and all plots.
    
    The state is saved in JSON format based on a dict of the following form:
    
    data: list of IDs
    binfile: the filename of the binary file used to store all the actual data
    data-dID: dict of settings belonging to a FacsData instance
    clust-dID-cID: a dict of attributes belonging to a clustering
    plots: list of plot IDs
    ppID: dict of 
    current-data: dID
    current-subplot: pID
    
    @type dir: str
    @param dir: The directory under which to save the project
    @type filename: str
    @param filename: The filename to be associated with the save files
    @type plots: list
    @param plots: A list containing the Subplot instances currently 
                  in the project
    @type currentPlotID: int
    @param currentPlotID: The list index of the currently selected Subplot
    @type selectedAxes: tuple
    @param selectedAxes: An n-tuple listing the currently selected plot axes
    @type grid: tuple
    @param grid: rows x columns in the main figure (grid size)
    """ 
    store = shelve.open(os.path.join(dir, filename))
    #store = dbopen(os.path.join(dir, filename), 'c', format='csv')
    # The actual numeric data will be stored in a separate binary file using
    # the numpy savez() method allowing for efficient storage/retrieval of data
    binfile = '%s.npz' % filename
    bindata = {}
    
    store['data'] = DataStore.getData().keys()
    store['binfile'] = binfile
    for dID in DataStore.getData():
        fdata = DataStore.get(dID)
        dStr = 'data-%s' % dID
        dfname = fdata.filename if (fdata.filename is not '') else binfile
        bindata[dStr] = fdata.data
        store[dStr] = {'filename':     dfname,
                       'displayname':  fdata.displayname, 
                       'labels':       fdata.labels, 
                       'ID':           fdata.ID,
                       'parent':       fdata.parent,
                       'children':     fdata.children,
                       'selDims':      fdata.selDims,
                       'clustering':   fdata.clustering.keys(),
                       'nodeExpanded': fdata.nodeExpanded,
                       'selectedClustering': fdata.selectedClustering}
        # clusterings
        for cID in fdata.clustering:
            cStr = 'clust-%i-%i' % (dID, cID)
            csett = {'method':            fdata.methodIDs[cID],
                     'opts':              fdata.clusteringOpts[cID],
                     'clusteringSelDims': fdata.clusteringSelDims[cID],
                     'infoExpanded':      fdata.infoExpanded[cID]}
            store[cStr] = csett
            bindata[cStr] = fdata.clustering[cID]
            
        # transformations
    
    # plots
    splots = []
    for plot in plots:
        pStr = 'p%i' % plot.n
        d = dict(plot.__dict__)
        d['axes'] = None
        store[pStr] = dict(d) 
        splots.append(pStr)
        
    store['plots'] = list(splots)
        
    # other
    store['current-data'] = DataStore.getCurrentIndex()
    store['current-subplot'] = currentPlotID
    store['selected-axes'] = selectedAxes
    store['grid'] = grid
    
    # write out settings data
    store.close()
    # write out numeric data to binary file
    np.savez(os.path.join(dir, binfile), **bindata)
    

def loadState(dir, filename):
    """
    Restore the system state as stored to disk.
    
    @type dir: string
    @param path: The directory under which the the saved system state is stored
    @type filename: str
    @param filename: The name of the saved project file (.find)
    @rtype: tuple
    @return: A list of subplot settings (dicts) retrieved from the file,
             The index of the currently selected subplot,
             The currently selected axes,
             The number of rows and columns in the figure (grid size)
    """
    store = shelve.open(os.path.join(dir, filename))
    #store = dbopen(os.path.join(dir, filename))
    datakeys = store['data']
    bindata = np.load(os.path.join(dir,store['binfile']))
    
    # Parse data sets
    for dID in datakeys:
        dStr = 'data-%s' % dID
        dsett = store[dStr]
        fdata = FacsData(dsett['filename'], dsett['labels'], bindata[dStr], dsett['parent'])
        fdata.displayname = dsett['displayname']
        fdata.ID = dsett['ID']
        fdata.children = dsett['children']
        fdata.selDims = dsett['selDims']
        fdata.nodeExpanded = dsett['nodeExpanded']
        # Parse clusterings
        for cID in dsett['clustering']:
            cStr = 'clust-%i-%i' % (dID, cID)
            csett = store[cStr]
            clusterIDs = bindata[cStr]
            fdata.addClustering(csett['method'], clusterIDs, csett['opts'], cID)
            fdata.clusteringSelDims[cID] = csett['clusteringSelDims']
            fdata.infoExpanded[cID] = csett['infoExpanded']
        
        DataStore.add(fdata, dID)

    # Subplots
    plots = []
    for pStr in store['plots']:
        plots.append(store[pStr])
        
        
    DataStore.selectDataSet(store['current-data'])
                
    return plots, store['current-subplot'], store['selected-axes'], store['grid']
        

#TODO: remove this and the associated menu item...replace with save/load above 
def exportClustering(path, fdata, cID):
    """
    Store the specified clustering to disk in an easily retrievable, human
    readable format.
    
    @type path: string
    @param path: the path and filename at which to store the data
    @type fdata: FacsData
    @param fdata: the dataset that the clustering is of
    @type cID: int
    @param cID: The ID of the desired clustering to export 
    """
    with open(path, 'w') as clust:
        method = fdata.methodIDs[cID]
        opts = str(fdata.clusteringOpts[cID])
        # header: filename, number of events, clustering method and options
        clust.write('file:%s\nevents:%i\nmethodID:%i\noptions:%s\n' % 
                    (fdata.filename, len(fdata.data), method, opts))
        # write the cluster assignments
        for item in fdata.clustering[cID]:
            clust.write('%i\n' % item)
         


























    