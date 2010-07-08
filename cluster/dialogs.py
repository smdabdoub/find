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
    
    
            
 

dialogs[methods.strID(methods.ID_KMEANS)] = methods.kmeans.KMeansDialog
dialogs[methods.strID(methods.ID_BAKKER_SCHUT)] = methods.bakker_schut.BakkerSchutKMeansDialog
#dialogs[methods.ID_AUTOCLASS] = None


from data.view import FacsPlotPanel
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
        self.facsPlotPanel = FacsPlotPanel(self,[0,1])
        self.facsPlotPanel.singlePlotWindow = True 
        self.facsPlotPanel.addSubplot(DataStore.getCurrentIndex())
        (self.dataSelectors, self.selectorSizer) = customsizers.ChannelSelectorSizer(self)
        # filter the list of labels to include only user-selected ones
        selDims = DataStore.getCurrentDataSet().selDims
        labels = [DataStore.getCurrentDataSet().labels[i] for i in selDims]
        customsizers.populateSelectors(self.dataSelectors, labels, selDims)        
        self.facsPlotPanel.updateAxes([selDims[0],selDims[1]], True)
        
        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.facsPlotPanel, True, wx.EXPAND | wx.BOTTOM | wx.TOP, -20)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.selectorSizer, False, wx.EXPAND | wx.TOP, 20)
        self.sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), False, wx.EXPAND)
        
        self.SetSizer(self.sizer)
        self.SetBackgroundColour("white")
        
        self.figure.canvas.mpl_connect('button_press_event', self.OnClick)
    
    
    def OnClick(self, event):
        if (event.inaxes is not None):
            print event.x,event.y
            print event.inaxes.get_position().get_points()
            self.windowParent.AddChosenCenter((event.xdata, event.ydata))


    def OnCBXClick(self, e):
        """ 
        Instructs the FacsPlotPanel instance to update the displayed axis 
        based on the selection made in the axis selection region of the main frame.
        """
        cbxSelected = self._GetSelectedAxes()
        self.facsPlotPanel.updateAxes(cbxSelected, True)
        
    
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
        
        print "Added point:", retPoint
        self.centers.append(retPoint)
    
    def GetCenters(self):
        return self.centers




