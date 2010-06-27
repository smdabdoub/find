'''
Created on Feb 11, 2010

@author: shareef
'''

# PLOTTING METHOD
from cluster.util import separate
from data.store import DataStore
import methods
import numpy as np

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
        fcData = DataStore.get(subplot.dataIndex)
        tf = ('xTransform', 'yTransform')
        for i, dim in enumerate(dims):
            t = fcData.getDefaultTransform(dim)
            if (t is not None) and ('log' in t.lower()):
                opts[tf[i]] = 'log'
            else:
                opts[tf[i]] = 'linear'
            
    
    if opts['xRangeAuto']:
        opts['xRange'] = (1, np.max(subplot.Data[:,dims[0]])*1.5)
    if opts['yRangeAuto']:
        opts['yRange'] = (1, np.max(subplot.Data[:,dims[1]])*1.5)
    
    # create the subplot and set its attributes
    subplot.axes = figure.add_subplot(subplot.mnp, xlim=opts['xRange'], 
                                      ylim=opts['yRange'], autoscale_on=False)

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
            subplot.axes.plot(xs, ys, '.', ms=1, color=methods.plotColors[i])




# OPTIONS DIALOG
from base import OptionsDialog, RangeOptionsPanel, TransformOptionsPanel
import wx

class ScatterPlot2dOptionsDialog(OptionsDialog):
    def __init__(self, parent, subplot, dims = None):
        """
        @type parent: Window
        @param parent: The parent window for the dialog
        @type subplot: Subplot
        @param subplot: The Subplot instance for which to specify settings
        """
        super(ScatterPlot2dOptionsDialog, self).__init__(parent, 
                                                         subplot, 
                                                         title="2D Scatterplot Options", 
                                                         size=(400,180))
        
        self.NB.AddPage(RangeOptionsPanel(self.NB), "Plot Range")
        self.NB.AddPage(TransformOptionsPanel(self.NB), "Transformations")

        self.loadOptions(subplot.opts)
        
        # create button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.buttonSizer.AffirmativeButton.Bind(wx.EVT_BUTTON, self.cmdOK_Click)
        
        # Sizer
        self.Sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        
        
    

