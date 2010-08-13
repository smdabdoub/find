"""
This module contains subclasses of wx.Dialog specifically designed 
to allow users to customize the options used to run various clustering 
methods.

@author: Shareef Dabdoub
@organization: The Ohio State University
@organization: Nationwide Children's Hospital
"""
import display.customsizers as customsizers
import methods
import wx

dialogs = {}


def addPluginDialog(ID, dialog):
    global dialogs
    dialogs[ID] = dialog
    

def getClusterDialog(clusterID, parent):
    return dialogs[clusterID](parent)
    
    
            
 

dialogs[methods.ID_KMEANS] = methods.kmeans.KMeansDialog
dialogs[methods.ID_BAKKER_SCHUT] = methods.bakker_schut.BakkerSchutKMeansDialog
#dialogs[methods.ID_AUTOCLASS] = None


from data.view import PlotPanel, Subplot
from data.store import DataStore

class CenterChooserDialog(wx.Dialog):
    """
    Provide scatterplot view of the data for choosing centers 
    """
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Cluster Center Chooser', size=(550, 550))
        self.CenterOnParent()
        
        self.centers = []
        
        # set up the plotting panel
        self.dataPanel = CenterChooserPanel(self, self.OnClick)
        (self.dataSelectors, self.selectorSizer) = customsizers.ChannelSelectorSizer(self)
        
        if DataStore.getCurrentIndex() is not None:
            self.dataPanel.addData(DataStore.getCurrentIndex())
            
            # filter the list of labels to include only user-selected ones
            selDims = DataStore.getCurrentDataSet().selDims
            labels = [DataStore.getCurrentDataSet().labels[i] for i in selDims]
            customsizers.populateSelectors(self.dataSelectors, labels, selDims)        
            self.dataPanel.updateAxes((selDims[0],selDims[1]))
        
        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.dataPanel, True, wx.EXPAND | wx.BOTTOM | wx.TOP, -20)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.selectorSizer, False, wx.EXPAND | wx.TOP, 20)
        self.sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), False, wx.EXPAND)
        
        self.SetSizer(self.sizer)
        self.SetBackgroundColour("white")
        
    
    
    def OnClick(self, event):
        if (event.inaxes is not None):
            self.AddChosenCenter((event.xdata, event.ydata))


    def OnCBXClick(self, e):
        """ 
        Instructs the FacsPlotPanel instance to update the displayed axis 
        based on the selection made in the axis selection region of the main frame.
        """
        cbxSelected = self._GetSelectedAxes()
        self.dataPanel.updateAxes(cbxSelected, True)
        
    
    def _GetSelectedAxes(self):
        return [cbx.GetClientData(cbx.GetSelection()) for cbx in self.dataSelectors]
    
    
    def AddChosenCenter(self, point):
        cbxSelected = self._GetSelectedAxes()
        dims = DataStore.getCurrentDataSet().labels
        if (DataStore.getCurrentDataSet().selDims):
            dims = DataStore.getCurrentDataSet().selDims
        retPoint = [0 for i in dims] 
        for i in range(len(cbxSelected)):
            retPoint[cbxSelected[i]] = point[i]
        
        self.centers.append(retPoint)
        self.dataPanel.addCenter(retPoint)
    
    def GetCenters(self):
        return self.centers



import plot.methods as pmethods
import numpy as np

class CenterChooserPanel(PlotPanel):
    def __init__(self, parent, clickHandler, **kwargs):
        # initiate plotter
        PlotPanel.__init__( self, parent, **kwargs )
        self._setColor((255,255,255))
        self.figure.canvas.mpl_connect('button_press_event', clickHandler)
        
        # private members
        self.plot = None
        self.centers = []
        self.axes = (0, 1)
        
    def addData(self, dataIndex):
        self.plot = Subplot(1, dataIndex)
        self.plot.mnp = '111'
    
    def addCenter(self, center):
        self.centers.append(center)
        self.draw()
    
    def updateAxes(self, axes):
        self.axes = axes
        self.draw()
        
        
    def draw(self):
        # scatterplot data
        pmethods.getMethod(self.plot.plotType)(self.plot, self.figure, self.axes)
        
        self.plot.axes.plot([500, 200], [500, 200],'+', ms=30, color='red')
        # draw centers
        try:
            c = np.asarray(self.centers)
            self.plot.axes.plot(c[:, self.axes[0]], c[:, self.axes[0]],'o', ms=30, color='red')
        except IndexError:
            pass
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


