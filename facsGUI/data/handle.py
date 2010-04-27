"""
This module contains various methods for handling FACS data.
"""
from matplotlib import mlab
import math
import numpy

def filterData(data, selDims):
    """
    Filter out the columns that are not selected for analysis
    
    @type data: array
    @param data: The input data to be filtered by column
    @type selDims: list
    @param selDims: The dimensions to keep in the filtered set
    
    @rtype: array
    @return: A reduced dimension version of the original data set
    """
    if data.shape[1] > len(selDims):
        return data[:, selDims]
    return data
    
    
def closestPoints(data, pts):
    """
    Given a list of n-dimensional points and an n-dimensional 
    data matrix, this method will find the points within the matrix
    that are the closest to each of the points in the list.
    
    @type data: array
    @var data: An n-dimensional array of points in Euclidean space
    @type pts: list
    @var pts: A list of n-dimensional points in Euclidean space
    @rtype: list
    @return: A list of the points in data closest to the respective points 
             in pts
    """
    closestPts = {}
    
    for pt in pts:
        closestPts[pt] = None
        for row in data:
            dist = distance(pt, row)
            if (closestPts[pt] is not None and dist < closestPts[pt]):
                closestPts[pt] = (dist, row)
    
    return [closestPts[pt][1] for pt in closestPts]
    
    
        

def distance(pt1, pt2):
    """
    Finds the Euclidean distance between multidimensional points
    """
    return math.sqrt(sum([(pt1[i]-pt2[i])**2 for i in range(len(pt1))]))
    

def reorderColumns(data, columnOrder):
    """
    Given an m x n data set, rearrange the n columns to the specified order.
    
    @type data: numpy.ndarray
    @var data: An m x n data set
    @type columnOrder: list
    @var columnOrder: A list of integers specifying columns. 
                      The order of the integers will set the new column order
                      for the given data set.
                      
    @rtype: numpy.ndarray
    @return: The column-reordered data set 
    """
    rows = len(data)
    cols = len(data[0])
    
    if (len(columnOrder) != cols):
        raise Exception, "Dimension Mismatch - columnOrder len must match col len of data"
    
    return numpy.column_stack(tuple([data[:,i] for i in columnOrder]))

#TODO: check this for dicts
def mergeData(clusters, data):
    """
    Combine the specified clusters into one data array.
    
    :@type clusters: collection
    :@param clusters: The IDs of the clusters to merge.
    :@type data: list/array or dict
    :@param data: The data pre-separated into clusters.
    
    :@rtype: array
    :@return: A new data array containing the merged clusters.
    """
    if type(data) is dict:
        rows = sum([data[i].shape[0] for i in clusters])
        cols = data[i].shape[1]
    else:
        rows = sum([len(data[i]) for i in clusters])
        cols = len(data[i][0])
    
    cat = tuple([data[i] for i in clusters])
    return numpy.concatenate(cat).reshape(rows, cols)


    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    