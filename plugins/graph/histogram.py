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
        opts['bins'] = 200
        opts['transformAuto'] = True
        opts['xTransform'] = ''
        opts['yTransform'] = ''
    
    # Set axes transforms
    if (opts['transformAuto']):
        opts['xTransform'] = 'log'
        opts['yTransform'] = 'linear'
    
    subplot.axes = figure.add_subplot(subplot.mnp, title=subplot.Title)
    subplot.axes.set_xlabel(subplot.Labels[dims[0]])
    subplot.axes.set_xscale('linear')
#    subplot.axes.set_xscale(opts['xTransform'])
#    subplot.axes.set_yscale(opts['yTransform'])
    
    #subplot.axes.hist(subplot.Data[:, dims[0]], bins=250, normed=True, histtype='bar',log=True)
#    h, b = np.histogram(subplot.Data[:, dims[0]], bins=opts['bins'])
#    b = (b[:-1] + b[1:])/2.0
#    subplot.axes.plot(b, h)
    
    
    # Kernel density estimation version
    data = subplot.Data[:, dims[0]]
    if opts['xTransform'] == 'linear':
        func = np.linspace
    
    if opts['xTransform'] == 'log':
        data = tm.getMethod('log')(data) 
        func = np.logspace
    
    ind = func(np.min(data), np.max(data), data.shape[0]*.1)
    gkde = stats.gaussian_kde(data)
    kdepdf = gkde.evaluate(ind)
    subplot.axes.plot(ind, kdepdf, label='kde', color='red')


# OPTIONS DIALOG
from plot.base import OptionsDialog, OptionsDialogPanel, TransformOptionsPanel
from display.formatters import IntFormatter
import wx

class HistogramOptionsDialog(OptionsDialog):
    def __init__(self, parent, subplot, dims = None):
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

        self.NB.AddPage(TransformOptionsPanel(self.NB), "Transformations")
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
        self.txtBins = wx.TextCtrl(self, size=(80,20))

        # Layout
        mainSizer = wx.BoxSizer()
        mainSizer.Add(wx.StaticText(self, wx.ID_ANY, "Histogram Bins:"))
        mainSizer.Add(self.txtBins, 1, wx.EXPAND, 10)
        
        # Sizer
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(mainSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)



    def loadOptions(self, opts):
        """
        This method loads the form input controls with saved/default data.
        
        :@type opts: dict  
        :@param opts: A dict of plot settings.
        """
        self.txtBins.Value = str(opts['bins'])
            
    
    def validate(self):
        intVal = IntFormatter()
        msg = []
        
        if not intVal.validate(self.txtBins.Value):
            msg.append("A valid integer must be entered.")
        else:
            val = int(self.txtBins.Value)
            if val < -10 or val > 1000:
                msg.append("A value between 10 and 1000 must be entered.")
            
        return msg


    @property
    def Options(self):
        options = {}
        options['bins'] = int(self.txtBins.Value)
        return options
    
    

def histogram_register():
    return (histogram, HistogramOptionsDialog, [0])