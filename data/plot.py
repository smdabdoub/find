'''
Created on Aug 30, 2009

@author: shareef
'''
from cluster.util import separate

import numpy as np
import numpy.numarray as na
import wx

ID_PLOTS_SCATTER    = wx.NewId()
ID_PLOTS_BOXPLOT    = wx.NewId()
ID_PLOTS_HISTOGRAM  = wx.NewId()
ID_PLOTS_BARPLOT    = wx.NewId()

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
    xlim = (1, np.max(subplot.getData()[:,dims[0]])*1.5)
    ylim = (1, np.max(subplot.getData()[:,dims[1]])*1.5)
    # create the subplot and set its attributes
    subplot.axes = figure.add_subplot(subplot.mnp, xlim=xlim, ylim=ylim, autoscale_on=False)
    #TODO: retrieve scaling info from subplot
    subplot.axes.set_xscale('log', nonposx='clip')
    subplot.axes.set_yscale('log', nonposy='clip')
    subplot.axes.set_xlabel(subplot.getLabels()[dims[0]])
    subplot.axes.set_ylabel(subplot.getLabels()[dims[1]])
    subplot.axes.set_title(subplot.Title)
    
    # draw the supplied FACS data
    if (not subplot.isDataClustered()):
        subplot.axes.plot(subplot.getData()[:,dims[0]], 
                          subplot.getData()[:,dims[1]], 
                          '.', ms=1, color='black')
    else:
        data = separate(subplot.getData(), subplot.getClustering())
        for i in range(len(data)):
            xs = data[i][:,dims[0]]
            ys = data[i][:,dims[1]]
            subplot.axes.plot(xs, ys, '.', ms=1, color=plotColors[i])



def histogram(subplot, figure, dims):
    subplot.axes = figure.add_subplot(subplot.mnp, title=subplot.Title)
    subplot.axes.set_xlabel(subplot.getLabels()[dims[0]])
    subplot.axes.hist(subplot.getData()[:, dims[0]], bins=250, normed=True, histtype='bar',log=True)




def boxplot(subplot, figure, labelRotation = -20):
    ymax = np.max(np.maximum.reduce(subplot.getData()))
    ylim = (1, ymax*10)
    # create the subplot and set its attributes
    subplot.axes = figure.add_subplot(subplot.mnp, 
                                   ylim=ylim, yscale='log', 
                                   autoscale_on=False,
                                   title=subplot.Title)
    subplot.axes.set_xticklabels(subplot.getLabels(), rotation=labelRotation)
    subplot.axes.boxplot(subplot.getData(), sym='')




def barplot(subplot, figure):
    """
    Create a bar chart with one bar for each cluster, and the bar height
    equal to the percent of events contained within the cluster.
    
    Some techniques borrowed from:
    http://www.scipy.org/Cookbook/Matplotlib/BarCharts
    """
    dataSize = len(subplot.getData())
    clustering = separate(subplot.getData(), subplot.getClustering())
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    