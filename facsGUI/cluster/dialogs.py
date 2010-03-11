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

class ClusterOptionsDialog(wx.Dialog):
    """
    Provides a base options dialog to specify a consistent interface for
    retrieving data from clustering-related dialogs
    """
    
    def getMethodArgs(self): pass
    def getStrMethodArgs(self): pass
    
    def getApplySizer(self, parent):
        self.chkApplyToCurrentSuplot = wx.CheckBox(parent, wx.ID_ANY, 'Apply to current subplot')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.chkApplyToCurrentSuplot)
        return sizer
    
    def isApplyChecked(self):
        return self.chkApplyToCurrentSuplot.GetValue()
    
    
            
class KMeansDialog(ClusterOptionsDialog):
    """
    Provide an options dialog for the k-means clustering algorithm 
    """
    
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'K-Means Options', size=(350, 300))
        self.CenterOnParent()
        
        # create form controls
        self.txtNumClusters   = wx.TextCtrl(self, wx.ID_ANY, '3', size=(50,20))
        self.cbxMethod        = wx.ComboBox(self, wx.ID_ANY, 'Mean', (-1,-1), (160, -1), ['Mean','Median'], wx.CB_READONLY)
        self.txtNumPasses     = wx.TextCtrl(self, wx.ID_ANY, '5', size=(50,20))
        self.chkInitialCenters = wx.CheckBox(self, wx.ID_ANY, 'Manually select centers?')
        self.initialCenters = []
        
        self.chkInitialCenters.Bind(wx.EVT_CHECKBOX, self.chkInitialCenters_Click)
        
        # create a table of label-input controls
        self.formSizer = wx.GridSizer(4, 2, vgap=20) #rows,cols,vgap,hgap
        self.formSizer.Add(wx.StaticText(self, -1, 'Number of clusters:', (20, 10)), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtNumClusters, 1)
        self.formSizer.Add(wx.StaticText(self, -1, 'K-Means method:', (20, 5)), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.cbxMethod, 1, wx.EXPAND)
        self.formSizer.Add(wx.StaticText(self, -1, 'Number of Passes:', (20, 10)), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtNumPasses, 1)
        
        # create the button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.buttonSizer.AffirmativeButton.Bind(wx.EVT_BUTTON, self.cmdOK_Click)
        #self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        #self.cmdOK = wx.Button(self, wx.ID_OK)
        #self.cmdCancel = wx.Button(self, wx.ID_CANCEL)
        #self.cmdOK.Bind(wx.EVT_BUTTON, self.cmdOK_Click)
        #self.buttonSizer.Add(self.cmdOK, 0, wx.EXPAND)
        #self.buttonSizer.Add(self.cmdCancel, 0, wx.EXPAND)
        
        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.formSizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.Add(self.chkInitialCenters, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.Add(self.getApplySizer(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 20)
        self.SetSizer(self.sizer)
        
        
    def cmdOK_Click(self,event):
        if self.chkInitialCenters.IsChecked():
            dlg = CenterChooserDialog(self)
            if dlg.ShowModal() == wx.ID_OK:
                self.initialCenters = dlg.GetCenters()
            dlg.Destroy()
        event.Skip()
            
    def chkInitialCenters_Click(self, event):
        if (event.Selection):
            self.txtNumPasses.Enable(False)
            self.txtNumPasses.Value = '0'
        else:
            self.txtNumPasses.Enable(True)
    
    
    def getMethodArgs(self):
        """
        Gather all options specified in the dialog.
        
        @rtype: dict
        @return: A dictionary of algorithm options.
        """
        options = {}
        options['numClusters'] = self._getNumClusters()
        options['method'] = self._getMethod()
        options['numPasses'] = self._getNumPasses()
        options['initialCenters'] = self._getInitialCenters()
        return options
    
    def getStrMethodArgs(self):
        """
        Define an equivalency between the variable form of algorithm options 
        and the full string representation of the options.
        
        @rtype: tuple
        @return: A tuple containing:
            - A dictionary equating the short form of method option names
            with the full string descriptions.
            - A dictionary containing translations for any argument values
            that are not easily understandable
        """
        options = {}
        options['numClusters'] = 'Number of Clusters'
        options['method'] = 'Method'
        options['numPasses'] = 'Number of Passes'
        options['initialCenters'] = 'Manually chosen centers'
        values = {}
        values['method'] = {'a':'Mean', 'm':'Median'}
        return (options, values)
        
        
    def _getNumClusters(self):
        """
        Retrieve the specified cluster target for the algorithm.
        
        @rtype: int
        @return: The number of clusters to find.
        """
        return int(self.txtNumClusters.GetValue())
    
    def _getMethod(self):
        """
        Retrieve the specified method for determining the cluster center.
        
        @rtype: char
        @return: The method by which the cluster center is determined.
        """
        if (self.cbxMethod.GetValue() == 'Mean'):
            return 'a'
        if (self.cbxMethod.GetValue() == 'Median'):
            return 'm'
    
    def _getNumPasses(self):
        """
        Retrieve the specified number of times the k-means algorithm should
        be run.
        
        @rtype: int
        @return: The number of passes the algorithm should perform.
        """
        return int(self.txtNumPasses.GetValue())
    
    def _getInitialCenters(self):
        """
        Retrieve the user-specified points to be used as initial centers for the 
        k-means algorithm
        
        @rtype: list
        @return: A list of 2D points
        """
        return self.initialCenters
    

dialogs[methods.ID_KMEANS] = KMeansDialog
dialogs[methods.ID_AUTOCLASS] = None


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




