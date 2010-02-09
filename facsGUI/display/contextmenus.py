
from data import plot
from data.store import DataStore
from display.dialogs import ClusterInfoDialog

import wx


class TreePopupMenu(wx.Menu):
    def __init__(self, parent, **kwargs):
        wx.Menu.__init__(self)

        self.parent = parent
        
        #TODO: retrieve the appropriate plotting methods from the data.plot module
        # Plot submenu
        self.plotSubmenu = wx.Menu()
        self.plotScatter = wx.MenuItem(self, plot.ID_PLOTS_SCATTER_2D, '2D Scatter Plot')
        self.plotSubmenu.AppendItem(self.plotScatter)
        self.Bind(wx.EVT_MENU, self.OnPlot, id=plot.ID_PLOTS_SCATTER_2D)
        self.AppendSubMenu(self.plotSubmenu, 'Plot', 'Apply various data visualizations to the selected plot')

        # Menu items specific to a data item
        if ('dataItem' in kwargs and kwargs['dataItem']):
            # Rename data item
            self.rename = wx.MenuItem(self, wx.NewId(), 'Rename', 'Give a new display name to this data item')
            self.AppendItem(self.rename)
            self.Bind(wx.EVT_MENU, self.OnRename, id=self.rename.GetId())
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
    
    def OnRename(self, event):
        self.parent.renameItem()
    
    def OnDelete(self, event):
        self.parent.deleteSelection()
        
    def OnInfo(self, event):
        dlg = ClusterInfoDialog(self.parent.TopLevelParent)
        dlg.Show()
        dlg.Destroy()
        
    def OnPlot(self, event):
        self.parent.plotData(event.GetId())
        
    def OnView(self, event):
        DataStore.view()
        


ID_PLOTS_DELETE     = wx.NewId()
ID_PLOTS_PROPERTIES = wx.NewId()
ID_PLOTS_RENAME     = wx.NewId()
        
class FigurePopupMenu(wx.Menu):
    """
    This menu is created when a right-click event occurs on a FACS plot.
    It is meant to extend the Plots menu that exists on the main form menubar. 
    Specifically, it contains options directly related to the figure that 
    was clicked on by the user.
    
    @type dataPoint: tuple
    @var dataPoint: The inaxes location of the mouse click 
    """
    def __init__(self, parent, **kwargs):
        wx.Menu.__init__(self)

        self.parent = parent
        
        # Begin menu
        self.Append(ID_PLOTS_PROPERTIES, "Properties...", "Edit/View the settings of this plot")
        self.Bind(wx.EVT_MENU, self.OnShowProperties, id=ID_PLOTS_PROPERTIES)
        self.Append(ID_PLOTS_DELETE, "Delete Subplot", " Delete the selected subplot")
        self.Bind(wx.EVT_MENU, self.OnDeleteSubplot, id=ID_PLOTS_DELETE)
        self.Append(ID_PLOTS_RENAME, "Rename Subplot", " Rename the selected subplot")
        self.Bind(wx.EVT_MENU, self.OnRenameSubplot, id=ID_PLOTS_RENAME)
        
    
    
    def OnDeleteSubplot(self, event):
        """
        Instructs the FacsPlotPanel instance to remove the currently selected subplot.
        """
        self.parent.deleteSubplot()
        
        
    def OnRenameSubplot(self, event):
        """
        """
        self.parent.renameSubplot()
        
        
    def OnShowProperties(self, event):
        """
        """
        self.parent.showSubplotProperties()
    
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        