'''
Created on Feb 11, 2010

@author: shareef
'''
__all__ = ['histogram_register']

import transforms.methods as tm

import numpy as np
from scipy import stats

def histogram(subplot, figure, dims):
    """
    histogram; Histogram; Plots a 1D Histogram
    """
    # set default plot options if necessary
    opts = subplot.opts
    if len(opts) == 0:
        opts['type'] = 'Gaussian KDE'
        opts['bins'] = 200
        opts['transformAuto'] = True
        opts['xTransform'] = ''
        opts['yTransform'] = ''
        opts['kdeDisplay'] = True 
    
    # Set axes transforms
    if (opts['transformAuto']):
        opts['xTransform'] = 'log'
        opts['yTransform'] = 'linear'
    
    subplot.axes = figure.add_subplot(subplot.mnp, title=subplot.Title)
    subplot.axes.set_xlabel(subplot.Labels[dims[0]])
    
    data = subplot.Data[:, dims[0]]
    
    if opts['xTransform'] == 'log':
        data = tm.getMethod('log')(data)

    # Kernel density estimation
    if opts['type'] == 'Gaussian KDE' or opts['type'] == 'Both':
        ind = np.linspace(np.min(data), np.max(data), data.shape[0]*.1)
        gkde = stats.gaussian_kde(data)
        kdepdf = gkde.evaluate(ind)
        subplot.axes.plot(ind, kdepdf, label='kde', color='blue')
    
    # Binned Histogram
    if opts['type'] != 'Gaussian KDE':
        #subplot.axes.hist(subplot.Data[:, dims[0]], bins=250, normed=True, histtype='bar',log=True)
        h, b = np.histogram(data, bins=opts['bins'])
        if opts['type'] == 'Both':
            h = tm.getMethod('log')(h)
        b = (b[:-1] + b[1:])/2.0
        subplot.axes.plot(b, h)
        
    if opts['type'] == 'Both':
        dataMax = max(np.max(kdepdf), np.max(h))
        subplot.axes.set_ylim(0, dataMax + 0.1)
        
        


# OPTIONS DIALOG
from plot.base import OptionsDialog, OptionsDialogPanel, TransformOptionsPanel
from display.formatters import IntFormatter
import wx

class HistogramOptionsDialog(OptionsDialog):
    def __init__(self, parent, subplot):
        """
        @type parent: Window
        @param parent: The parent window for the dialog
        @type subplot: Subplot
        @param subplot: The Subplot instance for which to specify settings
        """
        super(HistogramOptionsDialog, self).__init__(parent, 
                                                         subplot, 
                                                         title="Histogram Options", 
                                                         size=(400,180))

        top = TransformOptionsPanel(self.NB)
        top.enableYTransform(False)
        self.NB.AddPage(top, "Transformations")
        self.NB.AddPage(HistogramOptionsPanel(self.NB), "Histogram Options")

        self.loadOptions(subplot.opts)
        
        # create button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.buttonSizer.AffirmativeButton.Bind(wx.EVT_BUTTON, self.cmdOK_Click)
        
        # Sizer
        self.Sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        
        
class HistogramOptionsPanel(OptionsDialogPanel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Init controls
        self.cbxType = wx.ComboBox(self, choices=['Gaussian KDE', 'Binned', 'Both'],
                                   style=wx.CB_READONLY)
        self.cbxType.Bind(wx.EVT_COMBOBOX, self.cbxType_Select)
        self.txtBins = wx.TextCtrl(self, size=(80,20))
        self.txtBins.Enable(False)

        # Layout
        mainSizer = wx.FlexGridSizer(2, 2, 5, 5)
        mainSizer.Add(wx.StaticText(self, wx.ID_ANY, 'Histogram Type:'))
        mainSizer.Add(self.cbxType, 1, wx.EXPAND)
        mainSizer.Add(wx.StaticText(self, wx.ID_ANY, "Histogram Bins:"))
        mainSizer.Add(self.txtBins, 1, wx.EXPAND, 10)
        
        # Sizer
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(mainSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)


    def cbxType_Select(self, event):
        """
        Enable/disable the Bins text box depending on which histogram 
        type is selected.
        """
        if self.cbxType.StringSelection in ('Binned', 'Both'):
            self.txtBins.Enable(True)
        else:
            self.txtBins.Enable(False)


    def loadOptions(self, opts):
        """
        This method loads the form input controls with saved/default data.
        
        :@type opts: dict  
        :@param opts: A dict of plot settings.
        """
        self.cbxType.StringSelection = opts['type']
        self.txtBins.Value = str(opts['bins'])
            
    
    def validate(self):
        intVal = IntFormatter()
        msg = []
        
        if not intVal.validate(self.txtBins.Value):
            msg.append("A valid integer must be entered.")
        else:
            val = int(self.txtBins.Value)
            if val < 10 or val > 1000:
                msg.append("A value between 10 and 1000 must be entered.")
            
        return msg


    @property
    def Options(self):
        options = {}
        options['type'] = self.cbxType.StringSelection
        options['bins'] = int(self.txtBins.Value)
        return options
    
    

def histogram_register():
    return (histogram, HistogramOptionsDialog, [0])