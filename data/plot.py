'''
Created on Aug 30, 2009

@author: shareef
'''
from cluster.util import separate
from data import store

import numpy as np
import numpy.numarray as na
import wx
from data.store import DataStore

ID_PLOTS_SCATTER_2D    = wx.NewId()
ID_PLOTS_BOXPLOT    = wx.NewId()
ID_PLOTS_HISTOGRAM  = wx.NewId()
ID_PLOTS_BARPLOT    = wx.NewId()

methods = {}

def addPluginMethod(descriptor):
    """
    Adds a plotting method to the list of available methods.
    
    @var descriptor: A tuple containing the method ID, short name, 
                     description, function reference, list of applicable data-type IDs, 
                     and plugin flag (True if a plugin)
    """
    global methods
    methods[descriptor[0]] = descriptor
    

def getStringRepr(methodID):
    """
    Get the name of a clustering method by its ID.
    
    @type methodID: int
    @param methodID: One of the module-defined ID_* constants for the available methods.
    @rtype: string
    @return: The name of the specified clustering algorithm
    """
    if (methodID is not None):
        return methods[methodID][1]
    
    

# http://www.december.com/html/spec/color.html
# red, irish-flag green, blue, ??, maroon6, yellow, teal....
plotColors = ['#FF0000','#009900','#0000FF','#00EEEE','#8E236B','#FFFF00',
               '#008080',  'magenta', 'olive', 'orange', 'steelblue', 'darkviolet',
               'burlywood','darkgreen','sienna','crimson']

# For use with contour plotting
def colorcycle(ind=None, colors=plotColors):
    """
    Returns the color cycle, or a color cycle, for manually advancing
    line colors.
    """
    return colors[ind % len(colors)] if ind!=None else colors

# Plotting methods
def scatterplot2D(subplot, figure, dims):
    # set default plot options if necessary
    opts = subplot.opts
    if len(opts) == 0:
        opts['xRange'] = ()
        opts['xRangeAuto'] = True
        opts['yRange'] = ()
        opts['yRangeAuto'] = True 
        opts['xTransform'] = '' 
        opts['yTransform'] = ''
        opts['transformAuto'] = True
        
    
    # Set axes transforms
    if (opts['transformAuto']):
        tf = ('xTransform', 'yTransform')
        for i in range(2):
            lc = DataStore.get(subplot.dataIndex).labels[dims[i]].lower()
            if ('fsc' in lc or 'ssc' in lc):
                opts[tf[i]] = 'linear'
            else:
                opts[tf[i]] = 'log'
    
    if opts['xRangeAuto']:
        opts['xRange'] = (1, np.max(subplot.Data[:,dims[0]])*1.5)
    if opts['yRangeAuto']:
        opts['yRange'] = (1, np.max(subplot.Data[:,dims[1]])*1.5)
    
    # create the subplot and set its attributes
    subplot.axes = figure.add_subplot(subplot.mnp, xlim=opts['xRange'], 
                                      ylim=opts['yRange'], autoscale_on=False)
    #TODO: retrieve scaling info from subplot
    subplot.axes.set_xscale(opts['xTransform'], nonposx='clip')
    subplot.axes.set_yscale(opts['yTransform'], nonposy='clip')
    subplot.axes.set_xlabel(subplot.Labels[dims[0]])
    subplot.axes.set_ylabel(subplot.Labels[dims[1]])
    subplot.axes.set_title(subplot.Title)
    
    # draw the supplied FACS data
    if (not subplot.isDataClustered()):
        subplot.axes.plot(subplot.Data[:,dims[0]], 
                          subplot.Data[:,dims[1]], 
                          '.', ms=1, color='black')
    else:
        data = separate(subplot.Data, subplot.Clustering)
        for i in range(len(data)):
            xs = data[i][:,dims[0]]
            ys = data[i][:,dims[1]]
            subplot.axes.plot(xs, ys, '.', ms=1, color=plotColors[i])



def histogram(subplot, figure, dims):
    subplot.axes = figure.add_subplot(subplot.mnp, title=subplot.Title)
    subplot.axes.set_xlabel(subplot.Labels[dims[0]])
    subplot.axes.set_yscale('log')
    subplot.axes.set_xscale('log')
    #subplot.axes.hist(subplot.Data[:, dims[0]], bins=250, normed=True, histtype='bar',log=True)
    h, b = np.histogram(subplot.Data[:, dims[0]], bins=200, new=True)
    b = (b[:-1] + b[1:])/2.0
    subplot.axes.plot(b, h)





def boxplot(subplot, figure, labelRotation = -20):
    ymax = np.max(np.maximum.reduce(subplot.Data))
    ylim = (1, ymax*10)
    # create the subplot and set its attributes
    subplot.axes = figure.add_subplot(subplot.mnp, 
                                   ylim=ylim, yscale='log', 
                                   autoscale_on=False,
                                   title=subplot.Title)
    subplot.axes.set_xticklabels(subplot.Labels, rotation=labelRotation)
    subplot.axes.boxplot(subplot.Data, sym='')




def barplot(subplot, figure):
    """
    Create a bar chart with one bar for each cluster, and the bar height
    equal to the percent of events contained within the cluster.
    
    Some techniques borrowed from:
    http://www.scipy.org/Cookbook/Matplotlib/BarCharts
    """
    dataSize = len(subplot.Data)
    clustering = separate(subplot.Data, subplot.Clustering)
    percents = [float(len(cluster))/dataSize*100 for cluster in clustering]
    numBars = len(percents)
    width = 0.5
    rotation = 0 if numBars < 5 else -20
    xlocs = na.array(range(len(percents)))+0.5

    subplot.axes = figure.add_subplot(subplot.mnp, title=subplot.Title, autoscale_on=False)
    subplot.axes.set_xticks(xlocs + width/2)
    subplot.axes.set_xticklabels(map(lambda x: "%.2f%%" % x, percents), rotation=rotation)
    subplot.axes.xaxis.tick_bottom()
    subplot.axes.yaxis.tick_left()
    subplot.axes.set_xlim(0, xlocs[-1] + width*2)
    subplot.axes.set_ylim(0, 100)
    subplot.axes.bar(xlocs, percents, width=width, color=plotColors[:numBars])
    
    
    
    
    
    
methods[ID_PLOTS_BARPLOT] = (ID_PLOTS_BARPLOT, "Bar plot", 
                             """Create a bar chart with one bar for each 
                             cluster, and the bar height equal to the percent 
                             of events contained within the cluster.""", 
                             barplot, [store.ID_CLUSTERING_ITEM], False)

methods[ID_PLOTS_BOXPLOT] = (ID_PLOTS_BOXPLOT, "Box plot",
                             """Create a standard boxplot for each dimension 
                             in parallel in the same plot""",
                             boxplot, [store.ID_DATA_ITEM], False)


methods[ID_PLOTS_HISTOGRAM] = (ID_PLOTS_HISTOGRAM, "Histogram" 
                               """Display a 1D histogram using the dimension 
                               currently selected for the x-axis""",
                               histogram, [store.ID_DATA_ITEM], False)


methods[ID_PLOTS_SCATTER_2D] = (ID_PLOTS_SCATTER_2D, "2D Scatter Plot",
                             """Display a 2D Scatterplot of the currently 
                             selected x and y axes.""",
                             scatterplot2D, [store.ID_DATA_ITEM, store.ID_CLUSTERING_ITEM], False)
                             
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    