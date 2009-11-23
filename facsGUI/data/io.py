from __future__ import with_statement
"""
"""
from data.store import DataStore, FacsData
from ReadFCS.fcs import FCSReader
from IO.readFCS import FCSreader
from error import InvalidDataFile 

from matplotlib import mlab
import numpy as np

import os

# assume first line contains column labels
def loadCSV(filename):
    """
    Load the specified FACS data file.
    
    Note: currently only ASCII csv data files are accepted, 
    and not binary FCS files.
    
    @type filename: string
    @param filename: The name of the FACS data file to be loaded
    
    @rtype: tuple
    @return: A tuple containing a list of column labels and numpy array 
        containing the actual FACS data.
    """
    print 'loading:',filename
    # Retrieve first line of column labels
    facsFile = open(filename,'r')
    labels = facsFile.readline().rstrip().replace('"','').split(',')
    facsFile.close()
    print 'Column labels:',labels
    # load actual data
    data = mlab.load(filename, delimiter=',', skiprows=1)
    return (labels,data)


def loadFCS(filename):
    fcsReader = FCSReader(filename)
    data = np.column_stack(tuple(fcsReader.data[col] for col in fcsReader.names))
    return (fcsReader.names, data)

def loadFCS_New(filename):
    fcsReader = FCSreader(filename)
    info = fcsReader.get_FCMdata()
    #data = np.column_stack(tuple(fcsReader.data[col] for col in fcsReader.names))
    return (info[2], info[1])


# One-stop loader for all file types
fileTypes = {'csv': loadCSV, 'fcs': loadFCS_New}

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
    
    if (fileType in fileTypes):
        return fileTypes[fileType](filename)
    
    raise InvalidDataFile(filename)




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
         


























    