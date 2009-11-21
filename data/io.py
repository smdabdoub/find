"""
"""
from ReadFCS.fcs import FCSReader
from IO.readFCS import FCSreader
from error import InvalidDataFile 

from matplotlib import mlab
import numpy as np


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

















    