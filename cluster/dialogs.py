"""
This module contains subclasses of wx.Dialog specifically designed 
to allow users to customize the options used to run various clustering 
methods.

@author: Shareef Dabdoub
@organization: The Ohio State University
@organization: Nationwide Children's Hospital
"""
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

from util import separate
import plot

class ClusterInfoDialog(wx.Dialog):
    """
    This dialog displays detailed information on the currently selected clustering.
    """
    
    def __init__(self, parent, isolate = False):
        hGap = 20
        vGap = 10
        clusterIDs = DataStore.getCurrentDataSet().getCurrentClustering()
        clustering = separate(DataStore.getCurrentDataSet().data, clusterIDs)
        numClusters = len(clustering)
        numColumns = 3
        self.radioList = []
        self.isolate = isolate
        
        #TODO: still not perfect, larger cluster sizes gives an increasing space
        #      at the bottom
        # The magic # includes the header width, the vgap for it, and the widths and
        # border pads for the two sizers
        dlgWidth = 275
        dlgHeight = ((numClusters+1) * (vGap+20)) + 100
        if isolate:
            dlgWidth += 50
            #dlgHeight += 20
            
        title = 'Clustering Info'
        if (isolate):
            title = 'Isolate clusters'
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(dlgWidth, dlgHeight))
        self.CenterOnParent()
        
        
        # create main data display sizer
        # one row for each cluster plus header row
        # cols: cluster color, % of total
        
        self.formSizer = None
        if isolate:
            self.formSizer = wx.FlexGridSizer(numClusters+1, numColumns+1, hgap=hGap, vgap=vGap)
        else:
            self.formSizer = wx.FlexGridSizer(numClusters, numColumns, hgap=hGap, vgap=vGap)
        # header row
        if isolate:
            self.formSizer.Add(wx.StaticText(self, -1, 'Select', (5,10)), 1, wx.EXPAND)
        self.formSizer.Add(wx.StaticText(self, -1, 'Cluster', (5, 10)), 1, wx.EXPAND)
        self.formSizer.Add(wx.StaticText(self, -1, '% of Total', (20, 10)), 1, wx.EXPAND)
        self.formSizer.Add(wx.StaticText(self, -1, '# of Events', (20, 10)), 1, wx.EXPAND)
        # data rows
        for i in range(len(clustering)):
            cluster = clustering[i]
            if isolate:
                self.radioList.append(wx.CheckBox(self, wx.ID_ANY))
                self.formSizer.Add(self.radioList[i], 0, wx.EXPAND)
            # cluster color box
            label = wx.StaticText(self, -1, '', (20, 10))
            label.SetBackgroundColour(plot.methods.plotColors[i])
            self.formSizer.Add(label, 1, wx.EXPAND)
            # % of total
            percent = float(len(cluster))/len(DataStore.getCurrentDataSet().data)*100
            label = wx.StaticText(self, -1, '%6.2f' % percent + ' %', (30, 10))
            self.formSizer.Add(label, 1, wx.EXPAND | wx.ALIGN_CENTER)
            # number of events
            label = wx.StaticText(self, -1, str(len(cluster)), (30, 10))
            self.formSizer.Add(label, 1, wx.EXPAND | wx.ALIGN_CENTER)        
        
        # create the button row
        self.buttonSizer = None
        if isolate:
            self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        else:
            self.buttonSizer = self.CreateButtonSizer(wx.OK)
        
        
        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.formSizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 20)
        self.SetSizer(self.sizer)
        
        

    def SelectedClusters(self):
        return [i for i in range(len(self.radioList)) if self.radioList[i].IsChecked()]



from data.store import DataStore
from methods import getStringRepr
     
class ClusterRecolorSelectionDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Select clusterings to match colors", 
                           style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE, size=(400, 150))
        self.CenterOnParent()
    
        allData = DataStore.getData()
        self.choices = []
        self.choiceIDs = []
        
        # Populate the choices list with string, and populate the 
        # choiceIDs list with (dataID, clusteringID) tuples so the 
        # combo box selection can be tied to the data
        for didx in allData:
            fcData = allData[didx]
            for cidx in fcData.clustering: 
                self.choices.append(fcData.displayname + ": " + 
                            getStringRepr(fcData.methodIDs[cidx]) + " " + 
                            str(cidx+1))
                self.choiceIDs.append((fcData.ID, cidx))
        
        
        self.cbxSourceClustering = wx.ComboBox(self, choices=self.choices, style=wx.CB_READONLY)
        self.cbxDestClustering = wx.ComboBox(self, choices=self.choices, style=wx.CB_READONLY)

        
        self.formSizer = wx.FlexGridSizer(2, 2, vgap=5, hgap=5)
        self.formSizer.FlexibleDirection = wx.HORIZONTAL
        self.formSizer.AddF(wx.StaticText(self, -1, 'First Clustering:'), wx.SizerFlags(1).Expand())
        self.formSizer.AddF(self.cbxSourceClustering, wx.SizerFlags(2).Expand())
        self.formSizer.AddF(wx.StaticText(self, -1, 'Second Clustering:'), wx.SizerFlags(1).Expand())
        self.formSizer.AddF(self.cbxDestClustering, wx.SizerFlags(2).Expand())
        
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.AddF(self.formSizer, wx.SizerFlags(1).Expand().Border(wx.ALL, 10))
        self.Sizer.AddF(self.CreateButtonSizer(wx.OK|wx.CANCEL), wx.SizerFlags().Expand().Border(wx.BOTTOM, 10))

    
    @property
    def Source(self):
        if self.cbxSourceClustering.Selection >= 0:
            return self.choiceIDs[self.cbxSourceClustering.Selection]
        
    @property
    def Destination(self):
        if self.cbxDestClustering.Selection >= 0:
            return self.choiceIDs[self.cbxDestClustering.Selection]
        
        
        
        
        
        
        
        


