"""
This module contains various methods for handling FACS data.
"""
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
    if isinstance(data, dict):
        rows = sum([data[i].shape[0] for i in clusters])
        cols = data[i].shape[1]
    else:
        rows = sum([len(data[i]) for i in clusters])
        cols = len(data[i][0])
    
    cat = tuple([data[i] for i in clusters])
    return numpy.concatenate(cat).reshape(rows, cols)


    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    