'''
Created on Sep 11, 2010

@author: shareef
'''
__all__ = ['heatmap2d_register']

from data.fast_kde import fast_kde
import transforms.methods as tm

import matplotlib.cm as CM
import numpy as np

def heatmap2d(subplot, figure, dims):
    """
    heatmap2d; 2D Heatmap; Plots a 2D heatmap of the data with event density as the main indicator.
    """
    opts = subplot.opts
    if len(opts) == 0:
        opts['type'] = 'Hexbins'
        opts['colorMap'] = 'gist_earth'
        opts['bins'] = (200, 200)
        opts['transform'] = 'log'
        opts['transformAuto'] = True
        
    subplot.axes = figure.add_subplot(subplot.mnp, title=subplot.Title)
    subplot.axes.set_xlabel(subplot.Labels[dims[0]])
    subplot.axes.set_ylabel(subplot.Labels[dims[1]])
    
    x = subplot.Data[:, dims[0]]
    y = subplot.Data[:, dims[1]]
    cbLabel = ''
    
    # apply transform
    if 'transform' not in opts:
        opts['transform'] = 'log'
    if opts['transform'] == 'log':
        x = tm.getMethod('log')(x)
        y = tm.getMethod('log')(y)
    
    
    extent = (0, x.max()*1.05, 0, y.max()*1.05)
    
    cmap = CM.get_cmap(opts['colorMap'])
    if opts['type'] == 'Hexbins':
        gAx = subplot.axes.hexbin(x, y, gridsize=opts['bins'][0], extent=extent, mincnt=1, cmap=cmap)
        cbLabel = 'Events'

    # The following two means of calculating the heat map do not 
    # work correctly yet and are not enabled for selection.
    if opts['type'] == 'Gaussian KDE':
        kdeGrid = fast_kde(x, y, gridsize=opts['bins'])
        gAx = subplot.axes.imshow(kdeGrid, extent=extent, cmap=cmap,
                            aspect='auto', interpolation='bicubic')
    
    if opts['type'] == 'Histogram':
        heatmap, xedges, yedges = np.histogram2d(x, y, bins=opts['bins'])
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        gAx = subplot.axes.imshow(heatmap, extent=extent, cmap=cmap,
                            aspect='auto')
        
    cb = subplot.parent.colorbar(gAx)
    if cbLabel == '':
        cbLabel = 'Events' if opts['transform'] != 'log' else 'log Events'
    cb.set_label(cbLabel)
    

    
    
    

from plot.base import OptionsDialog, OptionsDialogPanel, SingleTransformOptionsPanel
from display.formatters import IntFormatter
import wx
#TODO: add range panel
class Heatmap2DOptionsDialog(OptionsDialog):
    def __init__(self, parent, subplot, dims=None):
        """
        @type parent: Window
        @param parent: The parent window for the dialog
        @type subplot: Subplot
        @param subplot: The Subplot instance for which to specify settings
        """
        super(Heatmap2DOptionsDialog, self).__init__(parent, 
                                                     subplot, 
                                                     title="2D Heatmap Options",
                                                     size=(400,200))

        top = SingleTransformOptionsPanel(self.NB)
        self.NB.AddPage(Heatmap2DOptionsPanel(self.NB), "Heatmap Options")
        self.NB.AddPage(top, "Transformations")

        self.loadOptions(subplot.opts)
        
        # create button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.buttonSizer.AffirmativeButton.Bind(wx.EVT_BUTTON, self.cmdOK_Click)
        
        # Sizer
        self.Sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)


class Heatmap2DOptionsPanel(OptionsDialogPanel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.GAUSSIAN_KDE = 'Gaussian KDE'
        self.HISTOGRAM = 'Histogram'
        self.HEXBINS = 'Hexbins'
        types = [self.HEXBINS]#, self.GAUSSIAN_KDE, self.HISTOGRAM]
        
        # Init controls
        self.cbxType = wx.ComboBox(self, choices=types,
                                   style=wx.CB_READONLY)
#        self.cbxType.Bind(wx.EVT_COMBOBOX, self.cbxType_Select)
        self.cbxColormap = wx.ComboBox(self, choices=collectColormaps(),
                                   style=wx.CB_READONLY)
        self.txtXBins = wx.TextCtrl(self, size=(80,20))
        #self.txtYBins = wx.TextCtrl(self, size=(80,20))

        # Layout
        mainSizer = wx.FlexGridSizer(3, 2, 5, 5)
        mainSizer.Add(wx.StaticText(self, wx.ID_ANY, 'Heatmap Type:'))
        mainSizer.Add(self.cbxType, 1, wx.EXPAND)
        mainSizer.Add(wx.StaticText(self, wx.ID_ANY, 'Color Map:'))
        mainSizer.Add(self.cbxColormap, 1, wx.EXPAND)
        mainSizer.Add(wx.StaticText(self, wx.ID_ANY, "Bins:"))
        mainSizer.Add(self.txtXBins, 1, wx.EXPAND, 10)
#        mainSizer.Add(wx.StaticText(self, wx.ID_ANY, "Y Bins:"))
#        mainSizer.Add(self.txtYBins, 1, wx.EXPAND, 10)
        
        # Sizer
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(mainSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)


    def cbxType_Select(self, event):
        """
        Enable/disable the Bins text box depending on which histogram 
        type is selected.
        """
        if self.cbxType.StringSelection == self.HEXBINS:
            self.txtYBins.Enable(False)
            self.YBins = self.txtYBins.Value
            self.txtYBins.Value = ""
        else:
            if not self.txtYBins.IsEnabled():
                self.txtYBins.Enable(True)
                self.txtYBins.Value = self.YBins


    def loadOptions(self, opts):
        """
        This method loads the form input controls with saved/default data.
        
        :@type opts: dict  
        :@param opts: A dict of plot settings.
        """
        self.cbxType.StringSelection = opts['type']
        self.cbxColormap.StringSelection = opts['colorMap']
        self.txtXBins.Value = str(opts['bins'][0])
#        if opts['type'] is not self.HEXBINS:
#            self.txtYBins.Value = str(opts['bins'][1])
            
    
    def validate(self):
        intVal = IntFormatter()
        msg = []
        
        # validate X bins 
        if not intVal.validate(self.txtXBins.Value):
            msg.append("Bins: A valid integer must be entered.")
        else:
            val = int(self.txtXBins.Value)
            if val < 10:
                msg.append("Bins: A value of at least 10 must be entered.")
            
        # validate Y bins
#        if self.cbxType.StringSelection != self.HEXBINS:
#            if not intVal.validate(self.txtYBins.Value):
#                msg.append("Y Bins: A valid integer must be entered.")
#            else:
#                val = int(self.txtYBins.Value)
#                if val < 10:
#                    msg.append("A value of at least 10 must be entered.")
            
        return msg


    @property
    def Options(self):
        options = {}
        options['type'] = self.cbxType.StringSelection
        options['colorMap'] = self.cbxColormap.StringSelection
        
#        if self.txtYBins.Value == "":
#            self.txtYBins.Value = self.YBins
#        options['bins'] = (int(self.txtXBins.Value), int(self.txtYBins.Value))
        options['bins'] = (int(self.txtXBins.Value), None)
        return options





def collectColormaps():
    """
    Generate a list of all the colormaps defined by matplotlib.
    Taken from http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps
    """
    maps = [m for m in CM.datad] # if not m.endswith("_r")]
    maps.sort()
    return maps

def heatmap2d_register():
    return (heatmap2d, Heatmap2DOptionsDialog, [0])