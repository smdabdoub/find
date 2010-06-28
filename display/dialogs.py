"""
This module contains all dialog classes necessary for non data-related menu items.

@author: Shareef Dabdoub
@organization: The Ohio State University
@organization: Nationwide Children's Hospital  
"""
from cluster.util import separate
from cluster.methods import getStringRepr
from data.store import DataStore
import plot.methods

import math
import wx

#TODO: validate input
class EditNameDialog(wx.Dialog):
    """
    This dialog allows the user to rename the labels of the incoming data set
    """
    
    def __init__(self, parent, label):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Edit Label', size=(200,103))
        self.CenterOnParent()
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.formSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.formSizer.AddSpacer(5)
        self.formSizer.Add(wx.StaticText(self, -1, 'Edit Label:'), 0, wx.ALIGN_LEFT)
        self.formSizer.AddSpacer(5)
        self.txtLabel = wx.TextCtrl(self, wx.ID_ANY, label)
        self.formSizer.Add(self.txtLabel, 2, wx.EXPAND)
        self.formSizer.AddSpacer(5)
        
        
        self.sizer.AddSpacer(10)
        self.sizer.Add(self.formSizer, 1, wx.EXPAND | wx.ALIGN_LEFT)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND)
        self.sizer.AddSpacer(5)
        
        self.SetSizer(self.sizer)
        
    @property
    def Text(self):
        """Retrieve the user-specified text"""
        return self.txtLabel.Value
    

from display.DataGrid import DataGrid

class SampleDataDisplayDialog(wx.Dialog):
    """
    This dialog uses the DataGrid class in the display package to give the user
    a sample view of the data they are importing, as well as allowing them to 
    rearrange and rename the columns
    """
    
    def __init__(self, parent, data, labels):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Sample Data Display', style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE, size=(450, 300))
        self.CenterOnParent()
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.dataGrid = DataGrid(self, data, labels)
        self.chkApplyToAll = wx.CheckBox(self, wx.ID_ANY, 'Apply to all files')
        
        self.sizer.Add(self.dataGrid, 1, wx.EXPAND)
        self.sizer.AddSpacer(10)
        self.sizer.Add(self.chkApplyToAll, 0, wx.EXPAND | wx.LEFT, 10)
        self.sizer.AddSpacer(5)
        self.sizer.Add(self.CreateButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND)
        self.sizer.AddSpacer(5)
        
        self.SetSizer(self.sizer)
    
    @property
    def ColumnsMoved(self):
        return self.dataGrid.colsMoved
    @property
    def ApplyToAll(self):
        return self.chkApplyToAll.Value
    @property
    def ColumnArrangement(self):
        """Retrieves the column labels as set by the user in the data grid"""
        return self.dataGrid.ColumnArrangement
    @property
    def ColumnLabels(self):
        return self.dataGrid.ColumnLabels
        


class DimensionExclusionDialog(wx.Dialog):
    """
    This dialog allows the user to choose which dimensions of the loaded
    FACS data will be used in analysis
    """
    
    def __init__(self, parent, dimensions):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Choose Dimensions for Analysis')
        self.CenterOnParent()
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.formSizer = wx.GridSizer(int(math.ceil(len(dimensions)/2.0)), 2, vgap=5, hgap=20) #rows,cols,vgap,hgap
        #self.formSizer = wx.GridSizer(len(dimensions), 1, vgap=5, hgap=20)
        self.chkApplyToAll = wx.CheckBox(self, wx.ID_ANY, 'Apply to all files')
        self.checkBoxes = []
        
        for dim in dimensions:
            self.checkBoxes.append(wx.CheckBox(self, wx.ID_ANY, dim))
            self.checkBoxes[-1].SetValue(True)
            self.formSizer.Add(self.checkBoxes[-1], 1, wx.EXPAND)
        
        self.sizer.AddSpacer(15)
        #self.sizer.Add(wx.StaticText(self, -1, 'Exclude dimensions'), 0, wx.ALIGN_CENTER_HORIZONTAL)
        #self.sizer.AddSpacer(20)
        self.sizer.Add(self.formSizer, 1, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.chkApplyToAll, 0, wx.EXPAND | wx.LEFT, 10)
        self.sizer.AddSpacer(5)
        self.sizer.Add(self.CreateButtonSizer(wx.OK), 0, wx.EXPAND)
        self.sizer.AddSpacer(5)
        
        self.SetSizer(self.sizer)
           
    
    @property
    def ApplyToAll(self):
        return self.chkApplyToAll.Value
    
    @property
    def SelectedDimensions(self):
        return [i for i in range(len(self.checkBoxes)) if self.checkBoxes[i].IsChecked()]
        
        


class FigureSetupDialog(wx.Dialog):
    """
    This dialog allows the user to specify the grid for subplots on the main figure.
    """
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Specify figure subplot grid', size=(320, 150))
        self.CenterOnParent()
        
        # create form controls
        self.txtRows = wx.TextCtrl(self, wx.ID_ANY, '1')
        self.txtColumns = wx.TextCtrl(self, wx.ID_ANY, '2')
        
        # create a table of label-input controls
        self.formSizer = wx.GridSizer(3, 2, hgap=10) #rows,cols,vgap,hgap
        self.formSizer.Add(wx.StaticText(self, -1, 'Number of rows:', (20, 10)), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtRows, 1)
        self.formSizer.Add(wx.StaticText(self, -1, 'Number of columns:', (20, 10)), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtColumns, 1)
        
        # create the button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        
        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.formSizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 20)
        self.SetSizer(self.sizer)
        
        
    def getRows(self):
        return int(self.txtRows.GetValue())
    
    def getColumns(self):
        return int(self.txtColumns.GetValue())
        


class DataInfoDialog(wx.Dialog):
    """
    This class displays (for now) the header information embedded in 
    FCS 3.0 files.
    """
    def __init__(self, parent, data):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Data Information', style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE, size=(280, 500))
        self.CenterOnParent()
        
        textAnn = sorted(data.annotations['text'].iteritems())
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.dataGrid = DataGrid(self, textAnn, ['Parameter', 'Value'], False, False)
        
        self.sizer.Add(self.dataGrid, 1, wx.EXPAND)
        self.sizer.AddSpacer(5)
        self.sizer.Add(self.CreateButtonSizer(wx.OK), 0, wx.EXPAND)
        self.sizer.AddSpacer(5)
        
        self.SetSizer(self.sizer)

        
        
        
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
            self.formSizer = wx.FlexGridSizer(numClusters+1, numColumns+1, hgap=hGap, vgap=vGap) #rows,cols,vgap,hgap
        else:
            self.formSizer = wx.FlexGridSizer(numClusters, numColumns, hgap=hGap, vgap=vGap) #rows,cols,vgap,hgap
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
        
        

class ClusterRecolorSelectionDialog(wx.Dialog):
    def __init__(self, parent, ):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Select clusterings to match colors")
        self.CenterOnParent()
    
        data = DataStore.getData()
        self.listLabels = [wx.StaticText(self, -1, data[i].displayname) for i in data]
        self.clusterLists = [wx.ListBox(self, wx.NewId(), style=wx.LB_SINGLE, 
                                        choices=[getStringRepr(data[i].methodIDs[cidx]) + " " + 
                                                 str(cidx+1) for cidx in data[i].clustering]) for i in data]
        
        self.Sizer = wx.FlexGridSizer(2, len(self.clusterLists), vgap=10, hgap=20)
        self.Sizer.AddMany([(label, 1, wx.EXPAND) for label in self.listLabels])
        self.Sizer.AddMany([(list, 1, wx.EXPAND) for list in self.clusterLists])
        self.Sizer.AddSpacer(10)
        self.Sizer.Add(self.CreateButtonSizer(wx.OK|wx.CANCEL), 1, wx.EXPAND)
        
    
    
    def _selectedClusters(self):
        selections = []
        for i,list in enumerate(self.clusterLists):
            selections.append((i,list.Selection))

        return selections
    
    @property
    def Source(self):
        return self._selectedClusters()[0]
        
    @property
    def Destination(self):
        return self._selectedClusters()[1]
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
      
        
        