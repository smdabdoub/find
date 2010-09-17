
import data.store as ds
import plot.methods

import wx

from itertools import ifilter

class DataTreePopupMenu(wx.Menu):
    def __init__(self, parent, **kwargs):
        wx.Menu.__init__(self)

        self.parent = parent
        self.dataItem = True
        
        # Retrieve the appropriate plotting methods from the plot.methods module
        dataPlots = ifilter(lambda item: ds.ID_DATA_ITEM in item[-2], 
                            plot.methods.AvailableMethods().itervalues())
        clusterPlots = ifilter(lambda item: ds.ID_CLUSTERING_ITEM in item[-2], 
                               plot.methods.AvailableMethods().itervalues())
        
        # Plot submenu
        self.plotSubmenu = wx.Menu()
        self.AppendSubMenu(self.plotSubmenu, 'Plot', 'Apply various data visualizations to the selected plot')

        # Menu items specific to a data item
        if ('dataItem' in kwargs and kwargs['dataItem']):
            # Data info
            self.info = wx.MenuItem(self, wx.NewId(), 'Info')
            self.AppendItem(self.info)
            self.Bind(wx.EVT_MENU, self.OnInfo, id=self.info.GetId())
            
            # Rename data item
            self.rename = wx.MenuItem(self, wx.NewId(), 'Rename', 'Give a new display name to this data item')
            self.AppendItem(self.rename)
            self.Bind(wx.EVT_MENU, self.OnRename, id=self.rename.GetId())
            
            self.assignPlotMethods(dataPlots, self.plotSubmenu)
            
            
        # Menu items specific to a clustering
        if ('dataItem' in kwargs and not kwargs['dataItem']):
            self.dataItem = False
            self.assignPlotMethods(clusterPlots, self.plotSubmenu)
            
            # Cluster info
            self.info = wx.MenuItem(self, wx.NewId(), 'Info')
            self.AppendItem(self.info)
            self.Bind(wx.EVT_MENU, self.OnInfo, id=self.info.GetId())
            
            # Isolate clusters
            self.isolate = wx.MenuItem(self, wx.NewId(), 'Isolate Clusters', 'Allows for separation of the clusters into new data sets')
            self.AppendItem(self.isolate)
            self.Bind(wx.EVT_MENU, self.parent.TopLevelParent.OnIsolateClusters, id=self.isolate.GetId())
        
        # Generic menu items    
        # Delete item
        delete = wx.MenuItem(self, wx.NewId(), 'Delete', 'Delete the current item')
        self.AppendItem(delete)
        self.Bind(wx.EVT_MENU, self.OnDelete, id=delete.GetId())
        
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
        if self.dataItem:
            self.parent.displayDataInfo()
        else:
            import cluster.dialogs as cd
            dlg = cd.ClusterInfoDialog(self.parent.TopLevelParent)
            dlg.Show()
        
    def OnPlot(self, event):
        self.parent.plotData(event.GetId())
        
    def OnView(self, event):
        ds.DataStore.view()
        
    def assignPlotMethods(self, methods, menu):
        """
        Populate a menu with the supplied plotting methods.
        
        :@type methods: tuple
        :@param methods: (strID, intID, title, description, ...)
        :@type menu: wx.Menu
        :@param menu: The menu to which the methods should be added. 
        """
        methods = list(methods)
        builtins = [item for item in methods if not item[-1]] 
        plugins = [item for item in methods if item[-1]]

        for method in builtins:
            menu.AppendItem(wx.MenuItem(self, method[1], method[2], method[3]))
            self.Bind(wx.EVT_MENU, self.OnPlot, id=method[1])
    
        if len(plugins) > 0:
            # Add a disabled menu item as a separator
            item = wx.MenuItem(self, wx.ID_ANY, "---Plugins---")
            item.Enable(False)
            menu.AppendItem(item)
            
            for method in plugins:
                menu.AppendItem(wx.MenuItem(self, method[1], method[2], method[3]))
                self.Bind(wx.EVT_MENU, self.OnPlot, id=method[1])
        
    

class FigureTreePopupMenu(wx.Menu):
    def __init__(self, parent, **kwargs):
        wx.Menu.__init__(self)

        self.parent = parent


        # Rename
        self.rename = wx.MenuItem(self, wx.NewId(), 'Rename', 'Give a new display name to this data item')
        self.AppendItem(self.rename)
        self.Bind(wx.EVT_MENU, self.OnRename, id=self.rename.GetId())

        # Delete
        self.delete = wx.MenuItem(self, wx.NewId(), 'Delete', 'Delete the current item')
        self.AppendItem(self.delete)
        self.Bind(wx.EVT_MENU, self.OnDelete, id=self.delete.GetId())



    def OnRename(self, event):
        self.parent.renameItem()

    def OnDelete(self, event):
        self.parent.deleteSelection()





ID_PLOTS_DELETE     = wx.NewId()
ID_PLOTS_PROPERTIES = wx.NewId()
ID_PLOTS_RENAME     = wx.NewId()
        
class SubplotPopupMenu(wx.Menu):
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
    
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        