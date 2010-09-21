"""
"""
from data.store import DataStore, FacsData, FigureStore, Figure
from IO import fcs
from error import UnknownFileType 

import numpy as np
import wx

import os

FILE_INPUT = True
FILE_OUTPUT = False

methods = {}
methods['fcs'] = ('fcs', wx.NewId(), fcs.FCSreader, False)

def loadDataFile(filename, window=None):
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
        c = methods[fileType][2](filename, window=window)
        return c.register()[FILE_INPUT]()
    
    raise UnknownFileType(filename)


def exportDataFile(eID, filename, fcData, window=None):
    """
    Passes the given FacsData instance to the specified IO class.
    
    :@type eID: int
    :@param eID: The int ID associated with the user-selected export format.
    :@type facs: data.store.FacsData
    :@param facs: The FacsData instance that will be handed to the IO method.
    """
    c = getMethod(eID)(filename, fcData, window=window)
    c.register()[FILE_OUTPUT]()


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



import shelve
def saveState(dir, filename, figures, currentFigureID, plots, currentPlotID, selectedAxes, grid):
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
    @type figures: list
    @param figures: A list of the Figure instances 
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
                       'annotations':  fdata.annotations, 
                       'analysis':     fdata.analysis, 
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
    
    
    # figures
    sfigs = []
    for figID in figures:
        fig = figures[figID]
        fStr = 'f%i' % figID
        d = dict(fig.__dict__)
        if figID == currentFigureID:  # copy displayed plots to current Figure
            splots = packSubplots(store, figID, plots)
        else:
            splots = packSubplots(store, figID, fig.subplots)
        
        d['subplots'] = splots
        store[fStr] = d
        
        sfigs.append(fStr)        
        
    store['figures'] = list(sfigs)

    # other
    store['current-data'] = DataStore.getCurrentIndex()
    store['current-figure'] = currentFigureID
    store['current-subplot'] = currentPlotID
    store['selected-axes'] = selectedAxes
    store['grid'] = grid
    
    # write out settings data
    store.close()
    # write out numeric data to binary file
    np.savez(os.path.join(dir, binfile), **bindata)
    


#TODO: Load Figures properly
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
    
    try:
        bindata = np.load(os.path.join(dir,store['binfile']))
    except IOError:
        bindata = None
    
    # Parse data sets
    for dID in datakeys:
        dStr = 'data-%s' % dID
        dsett = store[dStr]
        fdata = FacsData(dsett['filename'], dsett['labels'], bindata[dStr], 
                         annotations=dsett['annotations'], analysis=dsett['analysis'],
                         parent=dsett['parent'])
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
        
        DataStore.add(fdata)
        
    DataStore.selectDataSet(store['current-data'])

    # Figures
    for fStr in store['figures']:
        fDict = store[fStr]
        splots = []
        for pStr in fDict['subplots']:
            splots.append(store[pStr])
        fDict['subplots'] = splots
        f = Figure()
        f.load(fDict)
        FigureStore.add(f)
        
    FigureStore.setSelectedFigure(store['current-figure'])


    return store['current-subplot'], store['selected-axes'], store['grid']
        


         

def packSubplots(store, figID, plots):
    splots = []
    for plot in plots:
        pStr = 'fig-%i-p%i' % (figID, plot.n)
        d = dict(plot.__dict__)
        d['axes'] = None    # the matplotlib axes object
        d['parent'] = None  # a ref to the matplotlib Figure object
        store[pStr] = d 
        splots.append(pStr)

    return splots























    