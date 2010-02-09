from __future__ import with_statement
__all__ = ['MainWindow']

# Local imports
import cluster.dialogs as cDlgs
import cluster.methods as cMthds
import cluster.util as cUtil
from display.dialogs import ClusterInfoDialog
from display.dialogs import ClusterRecolorSelectionDialog
from display.dialogs import DimensionExclusionDialog
from display.dialogs import EditNameDialog
from display.dialogs import FigureSetupDialog
from display.dialogs import SampleDataDisplayDialog
import data.handle as dh
import data.view as dv
from data.store import DataStore
from data.store import FacsData
from data import io
import error
import plugin

# 3rd party imports
import wx
from wx.lib.wordwrap import wordwrap

# System imports
import math
import sys
import traceback

#TODO: remove these where possible as they are rarely necessary
# CONSTANTS

# File Menu
ID_OPEN       = wx.NewId()
ID_LOAD_STATE = wx.NewId()
ID_SAVE_STATE = wx.NewId()

# Plots Menu
ID_PLOTS_ADD      = wx.NewId()
ID_PLOTS_DELETE   = wx.NewId()
ID_PLOTS_RENAME   = wx.NewId()
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

        self.setup()
        self.dirname=''
        
        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D)
        self.rightPanel = wx.Panel(self.splitter)
        self.facsPlotPanel = dv.FacsPlotPanel(self.rightPanel)
        self.treeCtrlPanel = dv.FacsTreeCtrlPanel(self.splitter)
        
        # Partition the frame with sizers 
        self.dimensions = ['X axis', 'Y axis']
        self.selectorSizer = wx.FlexGridSizer(2, len(self.dimensions)+1, hgap=20)
        self.dataSelectors = []
        # add labels and combo boxes
        for dim in self.dimensions:
            self.selectorSizer.Add(wx.StaticText(self.rightPanel, -1, dim, (20, 5)), 1, wx.ALIGN_CENTER)
        
        self.chkLinked = wx.CheckBox(self.rightPanel, ID_LINKED, "Linked")
        self.selectorSizer.Add(self.chkLinked,0, wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.onLinkedClick, id=ID_LINKED)

        for i in range(len(self.dimensions)):
            self.dataSelectors.append(wx.ComboBox(self.rightPanel, ID_CBX+i, "", (-1,-1), (160, -1), [], wx.CB_READONLY))
            self.selectorSizer.AddGrowableCol(i) # so dim selectors take up most space
            self.selectorSizer.Add(self.dataSelectors[i], 1, wx.ALIGN_CENTER | wx.RIGHT, 10)
            self.Bind(wx.EVT_COMBOBOX, self.onCBXClick, id=ID_CBX+i)
            
        
        # Window layout
        self.dataSizer = wx.BoxSizer(wx.VERTICAL)
        self.dataSizer.Add(self.facsPlotPanel, True, wx.EXPAND)
        #self.dataSizer.Add(self.chkLinked, False, wx.EXPAND)
        self.dataSizer.Add(self.selectorSizer, False, wx.EXPAND | wx.TOP, 5)
        
        self.rightPanel.SetBackgroundColour("white")
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
        fileMenu.Append(ID_OPEN, "&Open File..."," Open a file to edit")
        self.Bind(wx.EVT_MENU, self.onOpen, id=ID_OPEN)
        # Save/Load system state
        fileMenu.Append(ID_SAVE_STATE, "Save project...","Save the state of the current analysis project.")
        self.Bind(wx.EVT_MENU, self.OnSaveState, id=ID_SAVE_STATE)
        fileMenu.Append(ID_LOAD_STATE, "Load project...","Load a saved analysis project.")
        self.Bind(wx.EVT_MENU, self.OnLoadState, id=ID_LOAD_STATE)
        # Raise error
        error = wx.MenuItem(fileMenu, wx.NewId(), 'Raise error')
        fileMenu.AppendItem(error)
        self.Bind(wx.EVT_MENU, self.OnRaiseError, id=error.GetId())
        # Exit
        item = fileMenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        self.Bind(wx.EVT_MENU, self.onMenuExit, item)
        self.Bind(wx.EVT_CLOSE, self.onExit)
        
        # Cluster menu
        # Populate from methods available from the imported cluster methods class
        clusterMenu = wx.Menu()
        clusterMethods = cMthds.getAvailableMethods()
        for id in clusterMethods:
            info = clusterMethods[id]
            # indicates this method is a plugin
            if (not info[4]):
                clusterMenu.Append(info[0], info[1], info[2])
                self.Bind(wx.EVT_MENU, self.onCluster, id=info[0])
        
        # Data menu
        self.dataMenu = wx.Menu()
        self.dataMenu.Append(ID_DATA_ISOLATE, 'Isolate Clusters', 
                               'Isolate one or more clusters as a separate data set under the parent')
        self.Bind(wx.EVT_MENU, self.onIsolateClusters, id=ID_DATA_ISOLATE)
        self.dataMenu.Append(ID_DATA_RECOLOR, 'Recolor Clusters', 
                               'Match the cluster IDs between two clusters in order to sync their colors')
        self.Bind(wx.EVT_MENU, self.onRecolorClusters, id=ID_DATA_RECOLOR)

        # Plots menu
        self.plotsMenu = wx.Menu()
        self.plotsMenu.Append(ID_PLOTS_SETUP, "Setup", 
                         " Indicate how the figure should be arranged in terms of subplots")
        self.Bind(wx.EVT_MENU, self.onSetupSubplots, id=ID_PLOTS_SETUP)
        self.plotsMenu.Append(ID_PLOTS_SAVE, "&Save Figure", 
                         " Export the figure as an image")
        self.Bind(wx.EVT_MENU, self.onSaveFigure, id=ID_PLOTS_SAVE)
#        self.plotsMenu.AppendSeparator()
        self.plotsMenu.Append(ID_PLOTS_ADD, "&Add Subplot", " Add a subplot to the current figure")
        self.Bind(wx.EVT_MENU, self.onAddSubplot, id=ID_PLOTS_ADD)
#        self.plotsMenu.Append(ID_PLOTS_DELETE, "&Delete Subplot", " Delete the selected subplot")
#        self.Bind(wx.EVT_MENU, self.onDeleteSubplot, id=ID_PLOTS_DELETE)
#        self.plotsMenu.Append(ID_PLOTS_RENAME, "Rename Subplot", " Rename the selected subplot")
#        self.Bind(wx.EVT_MENU, self.onRenameSubplot, id=ID_PLOTS_RENAME)
        
        # Plugin menu
        self.pluginsMenu = self.generatePluginsMenu()
        
        # Help menu
        self.helpMenu = wx.Menu()
        self.helpMenu.Append(wx.ID_ABOUT, "&About FIND"," Information about this program")
        self.Bind(wx.EVT_MENU, self.onAbout, id=wx.ID_ABOUT)
        
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "File")
        menuBar.Append(clusterMenu, "Cluster")
        menuBar.Append(self.dataMenu, "Data")
        menuBar.Append(self.plotsMenu, "Plots")
        menuBar.Append(self.pluginsMenu, "Plugins")
        menuBar.Append(self.helpMenu, "&Help")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        
        self.Show(1)

        sys.excepthook = self.excepthook



    ## GENERAL METHODS ##
    def setup(self):
        pass
        # Icon
#        image = wx.Image('find16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
#        icon = wx.EmptyIcon()
#        icon.CopyFromBitmap(image)
#        self.SetIcon(icon) 
        
        # Plugins
        plugin.importPlugins(plugin.discoverPlugins())
        self.generatePluginsMenu()
        
    def updateAxesList(self, labels, selectedAxes=(0,1)):
        """
        Update the axis selection boxes
        """
        for i in range(len(self.dataSelectors)):
            self.dataSelectors[i].SetItems(labels)
            self.dataSelectors[i].SetSelection(selectedAxes[i])
            
        
        
    
    def setSelectedPlotStatus(self, status):
        self.statusbar.SetStatusText(status, 1)
    
    #TODO: move at least part of this to the plugin module
    def generatePluginsMenu(self):
        pluginsMenu = wx.Menu()
        submenus = []
        for type_ in plugin.pluginTypes:
            submenus.append(wx.Menu())
        
        # Add loaded plugins to the submenus
        for i, type_ in enumerate(plugin.loaded):
            for module in plugin.loaded[type_]:
                try:
                    pluginMethods = module.__all__
                # skip this module if it does not define __all__
                except AttributeError:
                    continue
                # Handle special cases for various types
                # Clustering plugins
                if type_ == plugin.pluginTypes[0]:
                    for method in pluginMethods:
                        ID = wx.NewId()
                        cmethod, cdialog = eval('module.'+method)()
                        doc = cmethod.__doc__.split(';')
                        name = doc[0].strip()
                        descr = doc[1].strip()
                        cMthds.addPluginMethod((ID, name, descr, cmethod, True))
                        cDlgs.addPluginDialogs(ID, cdialog)
                        # Create the menu item
                        submenus[i].Append(ID, name, descr)
                        self.Bind(wx.EVT_MENU, self.onCluster, id=ID)
                
        
        # Add submenus to main menu
        for i, menu in enumerate(submenus):
            pluginsMenu.AppendSubMenu(menu, plugin.pluginTypes[i].capitalize())
        
        return pluginsMenu
        
    
    ## EVENT HANDLING ##
    def OnPluginAction(self, event):
        """
        This method acts as a passthrough for handling user requests for plugins.
        Each plugin-type will be handled by the appropriate module.
        """
        pass        
    
    def OnRaiseError(self, event):
        raise Exception("Test exception raised") 
    
    # FRAME CONTROLS    
    def onCBXClick(self, event):
        """ 
        Instructs the FacsPlotPanel instance to update the displayed axis 
        based on the selection made in the axis selection region of the main frame.
        """
        cbxSelected = [self.dataSelectors[i].GetSelection() for i in range(len(self.dataSelectors))]
        self.facsPlotPanel.updateAxes(cbxSelected, True)

    def onLinkedClick(self, event):
        """
        Sets whether the currently selected subplot will respond to the dimension selector
        """
        self.facsPlotPanel.setCurrentSubplotLinked(self.chkLinked.Value)
        
    def onExit(self, event):
        self.treeCtrlPanel.Destroy()
        self.Destroy()

    # MENU ITEMS
    
    # File Menu
    def onMenuExit(self, event):
        """
        Handles window exit event
        """
        self.Close(True)
        
    
    def onOpen(self, event):
        """
        Opens a FACS data file, parses it, and updates the FacsPlotPanel instance.
        
        @see: L{data.handle.loadFacsCSV} for details on what types of files can be loaded
        """
        #TODO: Move the formats list to the data.io module
        formats = "Binary FCS (*.fcs)|*.fcs|Comma Separated Values (*.csv)|*.csv"
        allLabels = []
        allColArr = []
        allDims   = []
        fColsMoved = False
        
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", formats, wx.FD_OPEN|wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            if (len(dlg.Paths) > 1):
                # Create an n/2 x 2 grid for the n selected data files
                self.facsPlotPanel.updateSubplotGrid(int(math.ceil(len(dlg.Paths)/2.0)), 2)
            
            #TODO: move to data.io module
            #TODO: bypass the dialogs if all checked
            # process each file selected
            for n, path in enumerate(dlg.Paths):
                self.statusbar.SetStatusText('loading: ' + path, 0)
                #TODO: include data annotations
                (labels, data) = io.loadDataFile(path)
                
                # Give the user a brief preview of the data (10 rows) and allow
                # column rearrangement and renaming
                if (not allLabels):
                    dgridDlg = SampleDataDisplayDialog(self, data[0:10,:], labels)
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
                DataStore.add(FacsData(dlg.Filenames[n], labels, data))
                self.updateAxesList(labels)
                    
                if (not allDims):
                    # Allow the user to choose columns for use in analysis
                    dimDlg = DimensionExclusionDialog(self, labels)
                    dimDlg.Size=(dimDlg.Size[0]*.75, dimDlg.Size[1]*.8)
                    if (dimDlg.ShowModal() == wx.ID_OK):
                        DataStore.getCurrentDataSet().selDims = dimDlg.SelectedDimensions
                        if (dimDlg.ApplyToAll):
                            allDims = list(dimDlg.SelectedDimensions)
                    dimDlg.Destroy()
                else:
                    DataStore.getCurrentDataSet().selDims = list(allDims)
                print 'Selected dimensions:', DataStore.getCurrentDataSet().selDims

                # update the panel
                self.facsPlotPanel.updateAxes([0,1])
                if (len(self.facsPlotPanel.subplots) == 0 or len(dlg.Paths) > 1):
                    self.facsPlotPanel.addSubplot(DataStore.getCurrentIndex())
        
            self.statusbar.SetStatusText('All data files loaded.')
            self.treeCtrlPanel.updateTree()
            
        dlg.Destroy()
        
    
    def OnSaveState(self, event):
        from data.io import saveState
        
        dlg = wx.FileDialog(self, "Save project to file", "", "", "*.find", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK and dlg.Filename:
            if not '.find' in dlg.Filename:
                dlg.Filename = dlg.Filename + '.find'
                dlg.Path = dlg.Path + '.find'
            
            selectedAxes = (self.facsPlotPanel.XAxisColumn, self.facsPlotPanel.YAxisColumn)
            grid = (self.facsPlotPanel.subplotRows, self.facsPlotPanel.subplotCols)
            saveState(dlg.Directory, dlg.Filename, self.facsPlotPanel.subplots, 
                      self.facsPlotPanel.selectedSubplot, selectedAxes, grid)
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
            self.updateAxesList(DataStore.getCurrentDataSet().labels, selectedAxes)
            self.treeCtrlPanel.updateTree()
            self.statusbar.SetStatusText("Project loaded from %s" % dlg.Path, 0)
        
        dlg.Destroy()
            
        
    
    def OnExportClustering(self, event):
        dlg = wx.FileDialog(self, "Export selected clustering to file", "", "", "*.clst", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            if not '.clst' in dlg.Path:
                dlg.Path = dlg.Path + '.clst'
            
            fdata = DataStore.getCurrentDataSet()
            io.exportClustering(dlg.Path, fdata, fdata.selectedClustering)
        
        dlg.Destroy()
    
    # Cluster Menu
    def onCluster(self, event):
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
                fcs = DataStore.getCurrentDataSet()
                data = fcs.data
                # Remove columns from analysis as specified by the user
                if fcs.selDims:
                    data = dh.filterData(data, fcs.selDims)
                clusterIDs, msg = cMthds.cluster(event.GetId(), data, **dlg.getMethodArgs())
                DataStore.addClustering(event.GetId(), clusterIDs, dlg.getMethodArgs())
                clusteringIndex = DataStore.getCurrentDataSet().clustering.keys()[-1]
                self.statusbar.SetStatusText(msg, 0)
                if (dlg.isApplyChecked()):
                    self.facsPlotPanel.setCurrentSubplotDataSet(DataStore.getCurrentIndex(), False)
                    self.facsPlotPanel.setCurrentSubplotClustering(clusteringIndex)
                self.treeCtrlPanel.updateTree()
        dlg.Destroy()
        
    # Plots Menu
    def onAddSubplot(self, event):
        """
        Instructs the FacsPlotPanel instance to add a subplot to the figure.
        """
        try:
            clusteringIndex = DataStore.getCurrentDataSet().clustering.keys()[-1]
        except IndexError:
            self.facsPlotPanel.addSubplot(DataStore.getCurrentIndex())
        else:
            self.facsPlotPanel.addSubplot(DataStore.getCurrentIndex(), clusteringIndex)
    
    #TODO: remove
    def onDeleteSubplot(self, event):
        """
        Instructs the FacsPlotPanel instance to remove the currently selected subplot.
        """
        self.facsPlotPanel.deleteSubplot()
    
    #TODO: remove
    def onRenameSubplot(self, event):
        """
        Allows the user to set the title of the selected subplot.
        """
        subplot = self.facsPlotPanel.subplots[self.facsPlotPanel.selectedSubplot-1]
        titleDlg = EditNameDialog(self, subplot.Title.split(':')[1].strip())
        if (titleDlg.ShowModal() == wx.ID_OK):
            subplot.Title = titleDlg.Text
            self.facsPlotPanel.draw()
        
        titleDlg.Destroy()
        
        
    def onSetupSubplots(self, event):
        dlg = FigureSetupDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.facsPlotPanel.updateSubplotGrid(dlg.getRows(), dlg.getColumns())
        
        dlg.Destroy()
            
    def onSaveFigure(self, event):
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
    def onIsolateClusters(self, event):
        """
        Handles menu requests to create a new dataset from a selection of 
        one or more clusters from an existing, clustered dataset.
        Note: If either dialog box spawned by this method are canceled, 
              the entire process is canceled. 
        """
        dlg = ClusterInfoDialog(self, True)
        if dlg.ShowModal() == wx.ID_OK:
            selection = dlg.SelectedClusters()
            nameDlg = EditNameDialog(self, '')
            if (nameDlg.ShowModal() == wx.ID_OK):
                cUtil.isolateClusters(selection, nameDlg.Text)
            
            self.treeCtrlPanel.updateTree()
        
        dlg.Destroy()
    
    def onRecolorClusters(self, event):
        dlg = ClusterRecolorSelectionDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            src = dlg.Source
            dst = dlg.Destination
            cUtil.reassignClusterIDs(src, dst)
        
        dlg.Destroy()
            
        
    # Help Menu
    def onAbout(self, event):
        """
        Displays a simple About dialog.
        """
        info = wx.AboutDialogInfo()
        info.Name = "FIND: Flow Investigation using N-Dimensions"
        info.Version = "0.1"
        info.Copyright = "(C) Shareef Dabdoub"
        info.Description = wordwrap(
            "This application allows for the display, clustering, and general analysis of "
            "n-dimensional FACS data",
            500, wx.ClientDC(self.facsPlotPanel))
        info.WebSite = ("http://justicelab.org/fwac", "FWAC Main Site")
        info.Developers = ["Shareef Dabdoub"]
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
    frame = MainWindow(None, -1, "FIND Display")
    app.MainLoop()
    sys.exit(0)
        
