__all__ = ['MainWindow']

# Local imports
import cluster.dialogs as cDlgs
import cluster.methods as cMthds
import cluster.util as cUtil
import data.handle as dh
import data.view as dv
import plot.dialogs as pDlgs
import plot.methods as pMthds

import display.dialogs as displayDialogs
import display.view as displayView
from data.store import DataStore, FacsData
from data import io
import error
import plugin
import transforms.methods as tm

# 3rd party imports
import wx
from wx.lib.wordwrap import wordwrap

# System imports
import math
import sys
import traceback

# CONSTANTS
# File Menu
ID_OPEN       = wx.NewId()
ID_LOAD_STATE = wx.NewId()
ID_SAVE_STATE = wx.NewId()

# Plots Menu
ID_PLOTS_ADD      = wx.NewId()
ID_PLOTS_SETUP    = wx.NewId()
ID_PLOTS_SAVE     = wx.NewId()

# Data Menu
ID_DATA_ISOLATE = wx.NewId()
ID_DATA_RECOLOR = wx.NewId()

# Controls
ID_CBX = wx.NewId()
ID_LINKED = wx.NewId()

class MainWindow(wx.Frame):
    """
    Main display window for the project.
    """
    
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(750,550))
        self.Center(direction=wx.HORIZONTAL)

        try:
            self.setup()
        except error.PluginError as pe:
            wx.MessageBox("The following error(s) occurred while loading the plugins directory:\n\n\t%s\n\nPlease fix the above problem(s) and restart FIND for plugins to work properly." % pe, 
                          "Plugin Error", wx.OK | wx.ICON_ERROR)
            loadPlugins = False
        else:
            loadPlugins = True    
            
        
        # Plugin menu
        if loadPlugins:
            self.pluginsMenu = self.generatePluginsMenu()
        
        self.dirname=''
        
        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D)
        self.splitter.SetBackgroundColour((150, 150, 150))
        #self.splitter.SetBackgroundColour('white')
        self.rightPanel = wx.Panel(self.splitter)
        self.facsPlotPanel = dv.FacsPlotPanel(self.rightPanel)
        self.treeCtrlPanel = displayView.FacsTreeCtrlPanel(self.splitter)
        
        # Partition the frame with sizers 
        self.dimensions = ['X axis', 'Y axis']
        self.selectorSizer = wx.FlexGridSizer(2, len(self.dimensions)+1, hgap=20)
        self.dataSelectors = []
        # add labels and combo boxes
        for dim in self.dimensions:
            self.selectorSizer.Add(wx.StaticText(self.rightPanel, -1, dim, (20, 5)), 1, wx.ALIGN_CENTER)
        
        self.chkLinked = wx.CheckBox(self.rightPanel, ID_LINKED, "Linked")
        self.selectorSizer.Add(self.chkLinked,0, wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.OnLinkedClick, id=ID_LINKED)

        for i in range(len(self.dimensions)):
            self.dataSelectors.append(wx.ComboBox(self.rightPanel, ID_CBX+i, "", (-1,-1), (160, -1), [], wx.CB_READONLY))
            self.selectorSizer.AddGrowableCol(i) # so dim selectors take up most space
            self.selectorSizer.Add(self.dataSelectors[i], 1, wx.ALIGN_CENTER | wx.RIGHT, 10)
            self.Bind(wx.EVT_COMBOBOX, self.OnCBXClick, id=ID_CBX+i)
            
        
        # Window layout
        self.dataSizer = wx.BoxSizer(wx.VERTICAL)
        self.dataSizer.Add(self.facsPlotPanel, True, wx.EXPAND)
        #self.dataSizer.Add(self.chkLinked, False, wx.EXPAND)
        self.dataSizer.Add(self.selectorSizer, False, wx.EXPAND | wx.TOP, 5)
        
        #self.rightPanel.SetBackgroundColour((100, 100, 100))
        self.rightPanel.SetBackgroundColour((255, 255, 255))
        #self.splitter.SetBackgroundColour('white')
        self.rightPanel.SetSizer(self.dataSizer)        
        self.splitter.SetMinimumPaneSize(20)
        self.splitter.SplitVertically(self.treeCtrlPanel, self.rightPanel, 150)
        
        # Set up status bar
        self.statusbar = self.CreateStatusBar(2)
        self.statusbar.SetStatusWidths([-1,200])
        self.statusbar.SetStatusStyles([wx.SB_NORMAL, wx.SB_RAISED])
        
        ## MENU SETUP ##
        
        # File menu
        fileMenu = wx.Menu()
        # Open file
        fileMenu.Append(ID_OPEN, "Open File(s)...\tCtrl+O"," Open a file to edit")
        self.Bind(wx.EVT_MENU, self.OnOpen, id=ID_OPEN)
        # Save/Load system state
        fileMenu.Append(ID_SAVE_STATE, "Save project...\tCtrl+S","Save the state of the current analysis project.")
        self.Bind(wx.EVT_MENU, self.OnSaveState, id=ID_SAVE_STATE)
        fileMenu.Append(ID_LOAD_STATE, "Load project...\tCtrl+L","Load a saved analysis project.")
        self.Bind(wx.EVT_MENU, self.OnLoadState, id=ID_LOAD_STATE)
        # Export submenu
        exportMenu = wx.Menu()
        # gather all the IO classes capable of output
        for entry in io.AvailableMethods().values():
            # instantiate the IO class
            c = entry[2]()
            if io.FILE_OUTPUT in c.register():
                doc = c.register()[io.FILE_OUTPUT].__doc__
                help = '' if doc is None else doc.strip().split('\n')[0]
                exportMenu.Append(entry[1], entry[0], help)
                self.Bind(wx.EVT_MENU, self.OnExport, id=entry[1])
        fileMenu.AppendSubMenu(exportMenu, 'Export...', 'Save data and/or clustering items')
        
        # Raise error
#        error = wx.MenuItem(fileMenu, wx.NewId(), 'Raise error')
#        fileMenu.AppendItem(error)
#        self.Bind(wx.EVT_MENU, self.OnRaiseError, id=error.GetId())
        # Exit
        item = fileMenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        self.Bind(wx.EVT_MENU, self.OnMenuExit, item)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        
        # Cluster menu
        # Populate from methods available from the imported cluster methods class
        clusterMenu = wx.Menu()
        clusterMethods = cMthds.getAvailableMethods()
        for id in clusterMethods:
            info = clusterMethods[id]
            # indicates this method is a plugin
            if (not info[4]):
                clusterMenu.Append(info[0], info[1], info[2])
                self.Bind(wx.EVT_MENU, self.OnCluster, id=info[0])
        
        # Data menu
        self.dataMenu = wx.Menu()
        self.dataMenu.Append(ID_DATA_RECOLOR, 'Recolor Clusters', 
                               'Match the cluster IDs between two clusters in order to sync their colors')
        self.Bind(wx.EVT_MENU, self.OnRecolorClusters, id=ID_DATA_RECOLOR)

        # Plots menu
        self.plotsMenu = wx.Menu()
        self.plotsMenu.Append(ID_PLOTS_SETUP, "Setup", 
                         " Indicate how the figure should be arranged in terms of subplots")
        self.Bind(wx.EVT_MENU, self.OnSetupSubplots, id=ID_PLOTS_SETUP)
        self.plotsMenu.Append(ID_PLOTS_SAVE, "Save Figure", 
                         " Export the figure as an image")
        self.Bind(wx.EVT_MENU, self.OnSaveFigure, id=ID_PLOTS_SAVE)
        self.plotsMenu.Append(ID_PLOTS_ADD, "Add Subplot", " Add a subplot to the current figure")
        self.Bind(wx.EVT_MENU, self.OnAddSubplot, id=ID_PLOTS_ADD)
        
        
        
        # Help menu
        self.helpMenu = wx.Menu()
        self.helpMenu.Append(wx.ID_ABOUT, "&About FIND"," Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "File")
        menuBar.Append(clusterMenu, "Cluster")
        menuBar.Append(self.dataMenu, "Data")
        menuBar.Append(self.plotsMenu, "Plots")
        if loadPlugins:
            menuBar.Append(self.pluginsMenu, "Plugins")
        menuBar.Append(self.helpMenu, "&Help")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        
        self.Show(1)

        sys.excepthook = self.excepthook



    ## GENERAL METHODS ##
    def setup(self):
        # Icons
        if sys.platform == "win32":
            ib = wx.IconBundle()
            ib.AddIconFromFile("find_white.ico", wx.BITMAP_TYPE_ANY)
            self.SetIcons(ib)
        
        # Plugins
        plugin.importPlugins(plugin.discoverPlugins())
            
            


    def updateAxesList(self, labels, selectedAxes=(0,1)):
        """
        Update the axis selection boxes
        """ 
        for i in range(len(self.dataSelectors)):
            self.dataSelectors[i].SetItems(labels)
            if len(labels) >= len(self.dataSelectors):
                self.dataSelectors[i].SetSelection(selectedAxes[i])
        
    
    def setSelectedPlotStatus(self, status):
        self.statusbar.SetStatusText(status, 1)
    
    #TODO: move at least part of this to the plugin module
    def generatePluginsMenu(self):
        pluginsMenu = wx.Menu()
        submenus = {}
        for type_ in plugin.pluginTypes:
            submenus[type_] = wx.Menu()
        
        # Add loaded plugins to the submenus
        for type_ in plugin.loaded:
            for module in plugin.loaded[type_]:
                try:
                    pluginMethods = module.__all__
                # skip this module if it does not define __all__
                except AttributeError:
                    continue
                # Handle special cases for various types
                
                #TODO: Implement Analysis plugins
                # Analysis plugins
                if type_ == plugin.pluginTypes[0]:
                    continue
                # Clustering plugins
                elif type_ == plugin.pluginTypes[1]:
                    for method in pluginMethods:
                        cID = wx.NewId()
                        cmethod, cdialog = eval('module.'+method)()
                        doc = cmethod.__doc__.split(';')
                        name = doc[0].strip()
                        descr = doc[1].strip()
                        cMthds.addPluginMethod((cID, name, descr, cmethod, True))
                        cDlgs.addPluginDialog(cID, cdialog)
                        # Create the menu item
                        submenus[type_].Append(cID, name, descr)
                        self.Bind(wx.EVT_MENU, self.OnCluster, id=cID)
                # Plotting plugins
                elif type_ == plugin.pluginTypes[2]:
                    for method in pluginMethods:
                        pID = wx.NewId()
                        pmethod, pdialog, dtypes = eval('module.'+method)()
                        doc = pmethod.__doc__.split(';')
                        strID = doc[0].strip()
                        name  = doc[1].strip()
                        descr = doc[2].strip()
                        pMthds.addPluginMethod((strID, pID, name, descr, pmethod, dtypes, True))
                        pDlgs.addPluginDialog(strID, pdialog)
                        # Create a disabled menu item to indicate plugin was loaded
                        item = wx.MenuItem(submenus[type_], pID, name, descr)
                        item.Enable(False)
                        submenus[type_].AppendItem(item)
                # I/O plugins
                elif type_ == plugin.pluginTypes[3]:
                    for method in pluginMethods:
                        name, cls = eval('module.'+method)()
                        ci = cls('')
                        descr = ' '.join(name, 'plugin') if ci.__doc__ is None \
                                else ci.__doc__.strip().split('\n')[0]
                        io.addPluginMethod((name, wx.NewId(), cls, True))
                        # Create a disabled menu item to indicate plugin was loaded
                        item = wx.MenuItem(submenus[type_], wx.ID_ANY, name, descr)
                        item.Enable(False)
                        submenus[type_].AppendItem(item)
                # Transforms plugins
                elif type_ == plugin.pluginTypes[4]:
                    pID = wx.NewId()
                    tmethod, tscaleClass = eval('module.'+method)()
                    doc = tmethod.__doc__.split(';')
                    strID = doc[0].strip()
                    name  = doc[1].strip()
                    descr = doc[2].strip()
                    tm.addPluginMethod((strID, pID, name, descr, tmethod, tscaleClass))
                
     
        # Add submenus to main menu
        for type_ in plugin.pluginTypes:
            if type_ == 'IO':
                pluginsMenu.AppendSubMenu(submenus[type_], type_)
            else:
                pluginsMenu.AppendSubMenu(submenus[type_], type_.capitalize())
        
        return pluginsMenu
        
    
    ## EVENT HANDLING ##     
    def OnRaiseError(self, event):
        raise Exception("Test exception raised") 
    
    # FRAME CONTROLS    
    def OnCBXClick(self, event):
        """ 
        Instructs the FacsPlotPanel instance to update the displayed axis 
        based on the selection made in the axis selection region of the main frame.
        """
        cbxSelected = [self.dataSelectors[i].GetSelection() for i in range(len(self.dataSelectors))]
        self.facsPlotPanel.updateAxes(cbxSelected, True)

    def OnLinkedClick(self, event):
        """
        Sets whether the currently selected subplot will respond to the dimension selector
        """
        self.facsPlotPanel.setCurrentSubplotLinked(self.chkLinked.Value)
        
    def OnExit(self, event):
        self.treeCtrlPanel.Destroy()
        self.Destroy()

    # MENU ITEMS
    
    # File Menu
    def OnMenuExit(self, event):
        """
        Handles window exit event
        """
        self.Close(True)
        
    
    def OnOpen(self, event):
        """
        Opens a FACS data file, parses it, and updates the FacsPlotPanel instance.
        """
        # retrieve the I/O methods for inputting files
        inputMethods = [m[2]() for m in io.AvailableMethods().values()]
        formats = '|'.join([m.FileType for m in inputMethods if io.FILE_INPUT in m.register()])
        allLabels = []
        allColArr = []
        allDims   = []
        fColsMoved = False
        numLoaded = 0
        
        # keep track of the common number of dimensions for datasets
        numDims = DataStore.getCurrentDataSet()
        if numDims is not None:
            numDims = len(numDims.labels)
        
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", formats, 
                            wx.FD_OPEN|wx.FD_MULTIPLE|wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            #TODO: move to data.io module?
            # process each file selected
            for n, path in enumerate(dlg.Paths):
                self.statusbar.SetStatusText('loading: ' + path, 0)
                try:
                    (labels, data, annotations) = io.loadDataFile(path, window=self)
                except TypeError:
                    # if there was an error loading the file, 
                    # loadDataFile should return None, so skip this file
                    continue
                
                # make sure the new file matches dimensions of loaded files
                if numDims is None:
                    numDims = len(labels)
                elif len(labels) != numDims:
                    wx.MessageBox("Error loading file: %s\n\nThe number of channels does not match those in currently loaded datasets. \n\nThis file will not be loaded." % dlg.Filenames[n],
                                  "File Error", wx.OK | wx.ICON_ERROR)
                    continue
                    
                
                # Give the user a brief preview of the data (10 rows) and allow
                # column rearrangement and renaming
                if (not allLabels):
                    dgridDlg = displayDialogs.SampleDataDisplayDialog(self, data[0:10,:], labels)
                    if (dgridDlg.ShowModal() == wx.ID_OK):
                        ca = dgridDlg.ColumnArrangement
                        lbls = dgridDlg.ColumnLabels
                        # Reassign the column labels
                        labels = [lbls[i] for i in ca]
                        
                        if dgridDlg.ApplyToAll:
                            allLabels = list(labels)
                            allColArr = list(ca)
                        
                        # Rearrange the data columns
                        if (dgridDlg.ColumnsMoved):
                            fColsMoved = True
                            data = dh.reorderColumns(data, ca)
                    else:
                        dgridDlg.Destroy()
                        continue
                    dgridDlg.Destroy()
                else:
                    labels = list(allLabels)
                    if fColsMoved:
                        data = dh.reorderColumns(data, allColArr)
                    
                # update the DataStore
                DataStore.add(FacsData(dlg.Filenames[n], labels, data, annotations=annotations))
                numLoaded += 1
                if n == 0:
                    self.updateAxesList(labels)
                    
                if (not allDims):
                    # Allow the user to choose columns for use in analysis
                    dimDlg = displayDialogs.DimensionExclusionDialog(self, labels)
                    dimDlg.Size=(dimDlg.Size[0]*.75, dimDlg.Size[1]*.8)
                    if (dimDlg.ShowModal() == wx.ID_OK):
                        DataStore.getCurrentDataSet().selDims = dimDlg.SelectedDimensions
                        if (dimDlg.ApplyToAll):
                            allDims = list(dimDlg.SelectedDimensions)
                    dimDlg.Destroy()
                else:
                    DataStore.getCurrentDataSet().selDims = list(allDims)

                # update the panel
                self.facsPlotPanel.updateAxes([0,1])
                if (len(self.facsPlotPanel.subplots) == 0 or len(dlg.Paths) > 1):
                    self.facsPlotPanel.addSubplot(DataStore.getCurrentIndex())
        
            # Create an n/2 x 2 grid for the n selected data files
            if (numLoaded > 1):
                self.facsPlotPanel.updateSubplotGrid(int(math.ceil(numLoaded/2.0)), 2)
            self.statusbar.SetStatusText('All data files loaded.')
            self.treeCtrlPanel.updateTree()
            
        dlg.Destroy()
        
    def OnExport(self, event):
        if DataStore.getCurrentIndex() is None:
            wx.MessageBox("Please load a dataset before attempting to export",
                          "Data Missing", wx.OK | wx.ICON_ERROR)
            return
        
        format = io.getMethod(event.GetId())().FileType
        dlg = wx.FileDialog(self, "Save File", "", "", 
                            format, 
                            wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            io.exportDataFile(event.GetId(), dlg.Path, DataStore.getCurrentDataSet(), window=self)
        
        dlg.Destroy()
    
    def OnSaveState(self, event):
        from data.io import saveState
        
        dlg = wx.FileDialog(self, "Save project to file", "", "", "*.find", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK and dlg.Filename:
            if not '.find' in dlg.Filename:
                dlg.Filename = dlg.Filename + '.find'
                dlg.Path = dlg.Path + '.find'
            
            try:
                selectedAxes = (self.facsPlotPanel.XAxisColumn, self.facsPlotPanel.YAxisColumn)
            except AttributeError:
                selectedAxes = (None, None)
            grid = (self.facsPlotPanel.subplotRows, self.facsPlotPanel.subplotCols)
            saveState(dlg.Directory, dlg.Filename, self.facsPlotPanel.subplots, 
                      self.facsPlotPanel.SelectedSubplotIndex, selectedAxes, grid)
            self.statusbar.SetStatusText("Project saved to %s" % dlg.Path, 0)
            
        dlg.Destroy()
            
    
    def OnLoadState(self, event):
        from data.io import loadState
        
        if len(DataStore.getData()) > 0:
            dlgWarn = wx.MessageDialog(self, 'This action may overwrite currently loaded datasets and/or plots.\n\nContinue anyway?', 'Warning', 
                                   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            if dlgWarn.ShowModal() == wx.ID_NO:
                dlgWarn.Destroy()
                return
            dlgWarn.Destroy()

        formats = "FIND Project File (*.find)|*.find"
        dlg = wx.FileDialog(self, "Select saved project", self.dirname, "", formats, wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            subplotDicts, currSubplot, selectedAxes, grid = loadState(dlg.Directory, dlg.Filename)
            self.facsPlotPanel.loadSavedPlots(subplotDicts, currSubplot)
            self.facsPlotPanel.updateAxes(selectedAxes, False)
            self.facsPlotPanel.updateSubplotGrid(grid[0], grid[1], True)
            self.chkLinked.Value = self.facsPlotPanel.CurrentSubplotLinked
            labels = DataStore.getCurrentDataSet().labels if DataStore.getCurrentDataSet() is not None else []
            self.updateAxesList(labels, selectedAxes)
            self.treeCtrlPanel.updateTree()
            self.statusbar.SetStatusText("Project loaded from %s" % dlg.Path, 0)
        
        dlg.Destroy()
            
        
    #TODO: Remove this
    def OnExportClustering(self, event):
        dlg = wx.FileDialog(self, "Export selected clustering to file", "", "", "*.clst", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            if not '.clst' in dlg.Path:
                dlg.Path = dlg.Path + '.clst'
            
            fdata = DataStore.getCurrentDataSet()
            io.exportClustering(dlg.Path, fdata, fdata.selectedClustering)
        
        dlg.Destroy()
    
    # Cluster Menu
    def OnCluster(self, event):
        """
        Handles all clustering requests.
        
        Clustering requests are handled in the following method:
            1. Passes the requested clustering method to 
               L{cluster.dialogs.ClusterOptionsDialog.showDialog} method 
            2. Passes the data and the returned method options to L{cluster.methods.cluster}
            3. Passes the returned cluster membership list to the FacsPlotPanel for display
        """
        dlg = cDlgs.getClusterDialog(event.GetId(), self)
        if dlg.ShowModal() == wx.ID_OK:
            if (DataStore.getCurrentDataSet() is not None):
                self.statusbar.SetStatusText('Running %s clustering...' % cMthds.methods[event.GetId()][1], 0)
                fcs = DataStore.getCurrentDataSet()
                data = fcs.data
                # Remove columns from analysis as specified by the user
                if len(fcs.selDims) > 0:
                    data = dh.filterData(data, fcs.selDims)
                clusterIDs, msg = cMthds.cluster(event.GetId(), data, **dlg.getMethodArgs())
                DataStore.addClustering(event.GetId(), clusterIDs, dlg.getMethodArgs())
                clusteringIndex = DataStore.getCurrentDataSet().clustering.keys()[-1]
                self.statusbar.SetStatusText(msg, 0)
                if (dlg.isApplyChecked()):
                    if self.facsPlotPanel.SelectedSubplotIndex is not None:
                        self.facsPlotPanel.CurrentSubplot = dv.Subplot(self.facsPlotPanel.SelectedSubplotIndex, 
                                                                       DataStore.getCurrentIndex(), clusteringIndex)
                        self.facsPlotPanel.draw()
                    else:
                        self.facsPlotPanel.addSubplot(DataStore.getCurrentIndex(), clusteringIndex)
                self.treeCtrlPanel.updateTree()
        dlg.Destroy()
        
    # Plots Menu
    def OnAddSubplot(self, event):
        """
        Instructs the FacsPlotPanel instance to add a subplot to the figure.
        """
        cds = DataStore.getCurrentDataSet()
        if cds is None:
            return
        
        try:
            clusteringIndex = cds.clustering.keys()[-1]
        except IndexError:
            self.facsPlotPanel.addSubplot(DataStore.getCurrentIndex())
        else:
            self.facsPlotPanel.addSubplot(DataStore.getCurrentIndex(), clusteringIndex)
        
        
    def OnSetupSubplots(self, event):
        dlg = displayDialogs.FigureSetupDialog(self, self.facsPlotPanel.subplotRows, self.facsPlotPanel.subplotCols)
        if dlg.ShowModal() == wx.ID_OK:
            self.facsPlotPanel.updateSubplotGrid(dlg.getRows(), dlg.getColumns())
        
        dlg.Destroy()
            
    def OnSaveFigure(self, event):
        formats = "PNG (*.png)|*.png|PDF (*.pdf)|*.pdf|PostScript (*.ps)|*.ps|EPS (*.eps)|*.eps|SVG (*.svg)|*.svg"
        fmts = ['png', 'pdf', 'ps', 'eps', 'svg']
        dlg = wx.FileDialog(self, "Save Figure", self.dirname, "", formats, wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            fileSplit = dlg.GetFilename().split('.')
            if (fileSplit[len(fileSplit)-1].lower() not in fmts):
                path += '.'+fmts[dlg.GetFilterIndex()]
            self.facsPlotPanel.saveFigure(path, fmts[dlg.GetFilterIndex()])
            self.statusbar.SetStatusText("Figure saved to "+path, 0)
        
        dlg.Destroy()
    
    # Data Menu
    
    #TODO: consider moving this to a more accessible location
    def OnIsolateClusters(self, event):
        """
        Handles menu requests to create a new dataset from a selection of 
        one or more clusters from an existing, clustered dataset.
        Note: If either dialog box spawned by this method are canceled, 
              the entire process is canceled. 
        """
        dlg = cDlgs.ClusterInfoDialog(self, True)
        if dlg.ShowModal() == wx.ID_OK:
            selection = dlg.SelectedClusters()
            nameDlg = displayDialogs.EditNameDialog(self, '')
            if (nameDlg.ShowModal() == wx.ID_OK):
                cUtil.isolateClusters(selection, nameDlg.Text)
            nameDlg.Destroy()
            
            self.treeCtrlPanel.updateTree()
        
        dlg.Destroy()
    
    
    
    def OnRecolorClusters(self, event):
        """
        Display a dialog that allows the user to select two clusterings, and
        rearrange their order to reflect cluster similarity.
        """
        dlg = cDlgs.ClusterRecolorSelectionDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            src = dlg.Source
            dst = dlg.Destination
            if (src is not None and dst is not None):
                cUtil.reassignClusterIDs(src, dst)
                self.SetStatusText("Cluster recoloring performed")
        
        dlg.Destroy()
            
        
    # Help Menu
    def OnAbout(self, event):
        """
        Displays a simple About dialog.
        """
        info = wx.AboutDialogInfo()
        info.Name = "FIND: Flow Investigation using N-Dimensions"
        info.Version = "0.2"
        info.Copyright = "(C) Shareef M. Dabdoub"
        info.Description = wordwrap(
            "This application allows for the display, clustering, and general analysis of "
            "n-dimensional FACS data",
            500, wx.ClientDC(self.facsPlotPanel))
        info.WebSite = ("http://justicelab.org/find", "FIND Main Site")
        info.Developers = ["Shareef M. Dabdoub"]
        #info.License = wordwrap("Pay me one MILLLLLLLION dollars!!!", 500, wx.ClientDC(self.facsPlotPanel))
        # Show the wx.AboutBox
        wx.AboutBox(info)
        

    def excepthook(self, type, value, tb):
        message = 'Uncaught exception:\n'
        message += ''.join(traceback.format_exception(type, value, tb))
        
        sys.stderr.write('ERROR: %s\n' % str(message))
        dlg = error.ReportErrorDialog(self, str(message))
        if (dlg.ShowModal() == wx.ID_OK):
            if dlg.Success:
                self.statusbar.SetStatusText("Error report submitted successfully", 0)
            else:
                self.statusbar.SetStatusText("Problem submitting report. Please check your system error logs", 0)
        dlg.Destroy()

        
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MainWindow(None, -1, "FIND: Flow Investigation using N-Dimensions")
    app.MainLoop()
    sys.exit(0)
        