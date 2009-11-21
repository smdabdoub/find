
from data import plot
from data.store import DataStore
from display.dialogs import ClusterInfoDialog

import wx


class TreePopupMenu(wx.Menu):
    def __init__(self, parent, **kwargs):
        wx.Menu.__init__(self)

        self.parent = parent
        
        # Plot submenu
        self.plotSubmenu = wx.Menu()
        self.plotScatter = wx.MenuItem(self, plot.ID_PLOTS_SCATTER, 'Scatter Plot')
        self.plotSubmenu.AppendItem(self.plotScatter)
        self.Bind(wx.EVT_MENU, self.OnPlot, id=plot.ID_PLOTS_SCATTER)
        self.AppendSubMenu(self.plotSubmenu, 'Plot', 'Apply various data visualizations to the selected plot')

        # Menu items specific to a data item
        if ('dataItem' in kwargs and kwargs['dataItem']):
            # Histogram
            self.plotHistogram = wx.MenuItem(self, plot.ID_PLOTS_HISTOGRAM, 'Histogram', 'Plot a 1D histogram of the X-axis data')
            self.plotSubmenu.AppendItem(self.plotHistogram)
            self.Bind(wx.EVT_MENU, self.OnPlot, id=plot.ID_PLOTS_HISTOGRAM)
            
            # Boxplot
            self.plotBoxplot = wx.MenuItem(self, plot.ID_PLOTS_BOXPLOT, 'Boxplot', 'Plots a series of boxplots; one per dimension')
            self.plotSubmenu.AppendItem(self.plotBoxplot)
            self.Bind(wx.EVT_MENU, self.OnPlot, id=plot.ID_PLOTS_BOXPLOT)
            
        # Menu items specific to a clustering
        if ('dataItem' in kwargs and not kwargs['dataItem']):
            # Bar plot
            self.plotBarplot = wx.MenuItem(self, plot.ID_PLOTS_BARPLOT, 'Bar Plot', 'Plot the cluster percentages in bar plot form')
            self.plotSubmenu.AppendItem(self.plotBarplot)
            self.Bind(wx.EVT_MENU, self.OnPlot, id=plot.ID_PLOTS_BARPLOT)
            
            # Cluster info
            self.info = wx.MenuItem(self, wx.NewId(), 'Info')
            self.AppendItem(self.info)
            self.Bind(wx.EVT_MENU, self.OnInfo, id=self.info.GetId())
            
            # Isolate clusters
            self.isolate = wx.MenuItem(self, wx.NewId(), 'Isolate Clusters', 'Allows for separation of the clusters into new data sets')
            self.AppendItem(self.isolate)
            self.Bind(wx.EVT_MENU, self.parent.TopLevelParent.onIsolateClusters, id=self.isolate.GetId())
        
        # Generic menu items    
        # Delete item
        delete = wx.MenuItem(self, wx.NewId(), 'Delete', 'Delete the current item')
        self.AppendItem(delete)
        self.Bind(wx.EVT_MENU, self.OnDelete, id=delete.GetId())
        self.AppendSeparator()
        
        # View all data
#        view = wx.MenuItem(self, wx.NewId(), 'View All Data')
#        self.AppendItem(view)
#        self.Bind(wx.EVT_MENU, self.OnView, id=view.GetId())
        
        
    def OnClearClusteringSelection(self, event):
        self.parent.clearClusteringSelection()
    
    def OnDelete(self, event):
        self.parent.deleteSelection()
        
    def OnInfo(self, event):
        dlg = ClusterInfoDialog(self.parent.TopLevelParent)
        dlg.Show()
        
    def OnPlot(self, event):
        self.parent.plotData(event.GetId())
        
    def OnView(self, event):
        DataStore.view()
        
        
class FigurePopupMenu(wx.Menu):
    """
    This menu is created when a right-click event occurs on a FACS plot.
    It is meant to extend the Plots menu that exists on the main form menubar. 
    Specifically, it contains options directly related to the figure that 
    was clicked on by the user.
    
    @type dataPoint: tuple
    @var dataPoint: The inaxes location of the mouse click 
    """
    def __init__(self, parent, dataPoint, **kwargs):
        wx.Menu.__init__(self)

        self.parent = parent
        self.dataPoint = dataPoint
        
        # Begin menu
        isolate = wx.MenuItem(self, wx.NewId(), 'Isolate Cluster')
        self.AppendItem(isolate)
        self.Bind(wx.EVT_MENU, self.OnIsolate, id=isolate.GetId())
        
    
    
    def OnIsolate(self, event):
        print "Isolate menu clicked"
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        