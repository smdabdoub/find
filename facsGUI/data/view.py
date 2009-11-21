"""
This module contains classes and methods used to visualize FACS data.

@author: Shareef Dabdoub
@organization: The Ohio State University
@organization: Nationwide Children's Hospital
"""


# Local imports
from display.contextmenus import TreePopupMenu
from data import plot
import cluster.methods
from cluster.util import separate
from store import DataStore
from store import FacsData

# 3rd Party imports
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from matplotlib.pyplot import subplot
import wx
import wx.lib.customtreectrl as CT

# System imports




# http://www.december.com/html/spec/color.html
# red, irish-flag green, blue, ??, maroon6, yellow, teal....
_manycolors = ['#FF0000','#009900','#0000FF','#00EEEE','#8E236B','#FFFF00',
               '#008080',  'magenta', 'olive', 'orange', 'steelblue', 'darkviolet',
               'burlywood','darkgreen','sienna','crimson']


class PlotPanel(wx.Panel):
    """
    The panel class used for displaying the matplotlib figure for FACS data display.
    """
    def __init__( self, parent, color=None, dpi=None, **kwargs ):
        # initialize Panel
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE
        wx.Panel.__init__( self, parent, **kwargs )
        self.parent = parent.GrandParent
        self.windowParent = parent
        self.selectedSubplot = None
        self.singlePlotWindow = False
        
        # initialize matplotlib stuff
        self.figure = Figure(None, dpi)
        self.figure.subplots_adjust(wspace=0.5, hspace=0.5)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self._setColor(color)
        self.SetBackgroundColour("white")
        
        self._setSize()

        self.Bind(wx.EVT_IDLE, self._onIdle)
        self.Bind(wx.EVT_SIZE, self._onSize)
        
        self.figure.canvas.mpl_connect('button_press_event', self._onClick)
        
        
    def setSelectedSubplot(self, plotNum):
        if (not self.singlePlotWindow):
            if (plotNum > 0):
                self.parent.setSelectedPlotStatus("Subplot "+str(plotNum)+" selected")
            else:
                self.parent.setSelectedPlotStatus("")
            self.selectedSubplot = plotNum
        
        
    def saveFigure(self, fname, fmt, transparent=False):
        self.figure.savefig(fname, format=fmt, transparent=transparent)
        
        
    def _onClick(self, event):
        if (event.inaxes is not None):
            if (self.singlePlotWindow):
                print event.x,event.y
                print event.inaxes.get_position().get_points()
                self.windowParent.AddChosenCenter((event.xdata, event.ydata))
            elif (event.button == 3):  # Right click
                plotNum = event.inaxes.get_title().split(':')[0]
                self.setSelectedSubplot(int(plotNum))
                pt = event.guiEvent.GetPosition()
                # Append the figure menu to the plots menu
                #self.parent.plotsMenu.AppendSubMenu(FigurePopupMenu(self, (event.xdata, event.ydata)), "Figure", 
                #                                    "Options related to the clicked figure")
                self.PopupMenuXY(self.parent.plotsMenu, pt.x, pt.y)
            else:
                plotNum = event.inaxes.get_title().split(':')[0]
                self.setSelectedSubplot(int(plotNum))


    def _setColor( self, rgbtuple=None ):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor( clr )
        self.figure.set_edgecolor( clr )
        self.canvas.SetBackgroundColour( wx.Colour( *rgbtuple ) )

    def _onSize( self, event ):
        self._resizeflag = True

    def _onIdle( self, evt ):
        if self._resizeflag:
            self._resizeflag = False
            self._setSize()

    def _setSize( self ):
        pixels = tuple( self.windowParent.GetClientSize() )
        # ugly hack to accommodate for the button row in the center chooser dialog
        if (self.singlePlotWindow):
            pixels = (pixels[0], pixels[1] - 20)
        
        # Check for valid size
        if (pixels != (0,0)):
            self.canvas.SetSize(pixels)
            horizOffset = -50
            if (pixels[1] < abs(horizOffset)):
                horizOffset = 0
            figWidth = float(pixels[0])/self.figure.get_dpi()
            figHeight = float(pixels[1] + horizOffset)/self.figure.get_dpi()
            self.figure.set_size_inches(figWidth , figHeight)

    def draw(self): pass # abstract, to be overridden by child classes


class FacsPlotPanel(PlotPanel):
    """
    The main display figure for the FACS data.
    """
    
    def __init__(self, parent, selectedAxes = [], colors = [], **kwargs):
        self.updateAxes(selectedAxes)
        self.color_list = colors
        self.subplots = []
        self.subplotRows = 1
        self.subplotCols = 1
        self.selectedSubplot = None

        # initiate plotter
        PlotPanel.__init__( self, parent, **kwargs )
        self._setColor((255,255,255))
        
    def addSubplot(self, dataStoreIndex, clusteringIndex = None, plotType = plot.ID_PLOTS_SCATTER):
        """
        Add a subplot to the figure.
        
        @type dataStoreIndex: int
        @param dataStoreIndex: The index into the data store for the FacsData 
            object backing the new subplot.
        @type clusteringIndex: int
        @param clusteringIndex: The index into the list of clusterings for the 
            data set this subplot represents.
        @type plotType: int
        @param plotType: One of the module-defined ID_PLOTS_* constants.
        """
        n = len(self.subplots)+1
        self.subplots.append(Subplot(n, dataStoreIndex, clusteringIndex, plotType))
        self.setSelectedSubplot(n)
        self.draw()    
        
    
    def deleteSubplot(self):
        """
        Deletes the currently selected subplot from the figure.
        """
        if (self.selectedSubplot > 0):
            del self.subplots[self.selectedSubplot-1]
            self.renumberPlots()
            self.draw()
        
        # when the selected subplot is deleted, there is no longer a selection
        self.setSelectedSubplot(None)
        
        
    def deleteAssociatedSubplots(self, ids):
        """
        Delete any subplots associated with the specified data or clustering ids
        
        @type ids: tuple
        @param ids: A tuple containing either a data ID and a clustering ID 
                    or just a data ID.
        """
        toDelete = []
        for n, subplot in enumerate(self.subplots):
            if (subplot.dataIndex == ids[0]): 
                if ids[1] is None:
                    toDelete.append(n)
                elif (ids[1] is not None) and (subplot.clustIndex == ids[1]):
                    toDelete.append(n)
        
        # delete flagged subplots by creating a new list w/o the deleted indices
        self.subplots = [self.subplots[i] for i in range(len(self.subplots)) if not (i in toDelete)]
        self.renumberPlots()
        
        self.draw()


    def renumberPlots(self):
        """ 
        renumber the subplots and their titles
        """
        for n, subplot in enumerate(self.subplots):
            subplot.n = n+1
            subplot.Title = subplot.Title.split(': ')[1]
        
        if (len(self.subplots) > 0):
            self.setSelectedSubplot(len(self.subplots))
        else:
            self.setSelectedSubplot(0)
            
    
    def plotData(self, dataID, clusterID=None, plotType=plot.ID_PLOTS_SCATTER):
        """
        Plots the specified data set to the currently selected subplot.
        
        @type dataID: int
        @var dataID: The ID of the data set to be plotted
        @type clusterID: int
        @var clusterID: The ID of the specific clustering to be plotted, if any.
        @type plotType: int
        @var plotType: The type of plot to be draw. Defaults to scatter plot.     
        """
        if (self.selectedSubplot > 0):
            self.subplots[self.selectedSubplot-1] = Subplot(self.selectedSubplot, dataID, 
                                                            clusterID, plotType)
            self.draw()
        else:
            wx.MessageDialog(self, 'Please select a subplot before plotting', 
                             'Select Subplot', wx.OK|wx.ICON_ERROR)
            
    
    def setCurrentSubplotDataSet(self, dataIndex, redraw=True):
        """
        Assigns a particular data set to the currently selected subplot.
        
        @type dataIndex: int
        @param dataIndex: The index of the data set from the store this subplot represents
        """
        self.subplots[self.selectedSubplot-1].setData(dataIndex)
        self.subplots[self.selectedSubplot-1].drawFlag = redraw
        self.draw()
    
    def setCurrentSubplotClustering(self, clusteringIndex, redraw=True):
        """
        Assigns a particular clustering to the currently selected subplot.
        
        @type clusteringIndex: int
        @param clusteringIndex: The index into the list of clusterings for the 
            data set this subplot represents
        """
        self.subplots[self.selectedSubplot-1].setClustering(clusteringIndex)
        self.subplots[self.selectedSubplot-1].drawFlag = redraw
        self.draw()
    
    
    def updateAxes(self, selectedAxes, redraw=False):
        """
        Specify the dimensions of the data to display on each of the axes in 
        the subplots in the figure.
        
        @type selectedAxes: list
        @param selectedAxes: A list of integers indicating which of the data 
            dimensions to display on the X and Y axes.
        @type redraw: bool 
        @param redraw: A boolean indicating whether or not to redraw the figure.
        """
        if (len(selectedAxes) >= 2):
            self.XAxisColumn = selectedAxes[0]
            self.YAxisColumn = selectedAxes[1]
            
        if (redraw):
            for subplot in self.subplots:
                subplot.drawFlag = True
            self.draw()
            
    def updateSubplotGrid(self, rows, cols, redraw=True):
        """
        Specify the dimensions of the subplot grid for the main figure.
        
        @type row: int
        @param row: The number of rows in the subplot grid for the figure.
        @type col: int
        @param col: The number of columns in the subplot grid for the figure.
        @type redraw: bool 
        @param redraw: A boolean indicating whether or not to redraw the figure.
        """
        self.subplotRows = rows
        self.subplotCols = cols
        
        if (redraw):
            for subplot in self.subplots:
                subplot.drawFlag = True
            self.draw()
    
    #TODO: finish the selective redrawing
    def draw(self):
        """Draw all visible subplots"""            
        # Clear the figure canvas
        self.canvas.figure.clf() 
        # Draw each subplot
        if (len(self.subplots) > 0):             
            subCount = 0
            for _ in range(self.subplotRows):
                for _ in range(self.subplotCols):
                    if (subCount < len(self.subplots)): # and self.subplots[subCount].drawFlag):
                        self.drawSubplot(self.subplotRows, self.subplotCols, self.subplots[subCount])
                        self.subplots[subCount].drawFlag = False
                        subCount += 1
                
            self.canvas.draw()

            


    # TODO: include plots in plugin system
    def drawSubplot(self, row, col, subplot):
        """
        Issue the commands necessary for drawing a subplot on the current 
        figure in the panel.
        
        @type row: int
        @param row: The number of rows in the subplot grid for the figure.
        @type col: int
        @param col: The number of columns in the subplot grid for the figure.
        @type subplot: Subplot
        @param subplot: The Subplot instance to draw on the figure.
        """            
        dims = (self.XAxisColumn, self.YAxisColumn)
        subplot.mnp = self.mnp(row, col, subplot.n)
        if (subplot.Title == ''):
            subplot.Title = subplot.DisplayName
        
        #TODO: streamline this with a single generic plot method (see cluster)  
        # Plot data using available methods in data.plot
        if (subplot.plotType == plot.ID_PLOTS_SCATTER):
            plot.scatterplot2D(subplot, self.figure, dims)

        if (subplot.plotType == plot.ID_PLOTS_HISTOGRAM):
            plot.histogram(subplot, self.figure, dims)
            
        if (subplot.plotType == plot.ID_PLOTS_BOXPLOT):
            plot.boxplot(subplot, self.figure)
            
        if (subplot.plotType == plot.ID_PLOTS_BARPLOT):
            plot.barplot(subplot, self.figure)
        
        subplot.drawFlag = False


    def mnp(self, row, col, num):
        """
        Create a 3 digit integer representing rowsXcolsXplot# to pass as input
        to the subplot creation routine provided by matplotlib.
        
        @type row: int
        @param row: The number of rows in the subplot grid for the figure.
        @type col: int
        @param col: The number of columns in the subplot grid for the figure.
        @type num: int
        @param num: The number of the subplot in the overall grid.
        """
        return 100*row+10*col+num            


class Subplot(object):
    """
    Represents a single subplot and the options necessary for specifying what is displayed.
    """
    
    def __init__(self, n, dataStoreIndex, clusteringIndex = None, plotType = plot.ID_PLOTS_SCATTER):
        self.n = n
        self.dataIndex = dataStoreIndex
        self.clustIndex = clusteringIndex
        self.plotType = plotType
        self.axes = None
        self.mnp = None
        self._title = ''
        self.drawFlag = True


    # TODO: replace get/set with properties
    def getData(self):
        """
        Retrieve the data backing this subplot.
        
        @rtype: numpy array
        @return: An array containing the original data backing this subplot.
        """
        data = DataStore.getData()
        facs = data[self.dataIndex]
        return facs.data
        
    def setData(self, dataStoreIndex):
        self.dataIndex = dataStoreIndex
        self.clustIndex = None
    

    
    def getClustering(self):
        """
        Retrieve the clustering specified for this subplot.
        
        @rtype: list
        @return: A list where each element indicates the cluster membership of the 
            corresponding index in the original data
        """
        return DataStore.getData()[self.dataIndex].clustering[self.clustIndex]
    
    def setClustering(self, clusteringIndex):
        """
        Set the clustering index to use from the list of clusterings from the 
        data set backing this suplot.
        
        @type clusteringIndex: int
        @param clusteringIndex: The index into the list of clusterings for the 
            data set this subplot represents 
        """
        self.clustIndex = clusteringIndex
    
    
    def getLabels(self):
        """
        Retrieve the column labels for the data backing this subplot.
        
        @rtype: list
        @return: A list of strings representing the column names for the 
            data backing this subplot.
        """
        return DataStore.getData()[self.dataIndex].labels
    
    @property
    def DisplayName(self):
        """
        Retrieve the display name for the data backing this subplot.
        
        @rtype: string
        @return: A string representing the name of the file for the 
            data backing this subplot.
        """
        return DataStore.getData()[self.dataIndex].displayname
    
    def isDataClustered(self):
        """
        Determine whether a clustering has been specified for this subplot.
        
        @rtype: bool
        @return: A boolean indicating whether a clustering has been specified for this subplot.
        """
        return self.clustIndex is not None
    
    # Title Property
    def getTitle(self):
        return self._title
    def setTitle(self, title):
        self._title = '%i: %s' % (self.n, title)
    
    Title = property(getTitle, setTitle, doc='The visible title at the top of the subplot.')
    
    
#---------------------------------------------------------------------------
class FacsTreeCtrlPanel(wx.Panel):
    def __init__(self, parent):
        # Use the WANTS_CHARS style so the panel doesn't eat the Return key.
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS, size=(200,550))
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.tree = CT.CustomTreeCtrl(self, wx.NewId(), wx.DefaultPosition, (200,550), CT.TR_DEFAULT_STYLE)

        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        self.fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))

        self.tree.SetImageList(il)
        self.il = il

        self.updateTree()

        self.Bind(CT.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, self.tree)
        self.Bind(CT.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, self.tree)
        self.tree.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.tree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        


    def updateTree(self):
        self.tree.DeleteAllItems()
        
        self.root = self.tree.AddRoot("Data Sets")
        self.tree.SetPyData(self.root, None)
        self.tree.SetItemImage(self.root, self.fldridx, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, self.fldropenidx, wx.TreeItemIcon_Expanded)

        self.buildTree(self.root, DataStore.getData(), [])
        self.tree.Expand(self.root)
            


    def buildTree(self, parent, dataDict, visited):
        for dIndex, fData in dataDict.iteritems():
            # add tree node for the FACS data set
            if fData.ID in visited:
                return
            child = self.tree.AppendItem(parent, fData.displayname)
            if (DataStore.getCurrentIndex() == dIndex):
                self.tree.SetItemBold(child, True)
            self.tree.SetPyData(child, dIndex)
            self.tree.SetItemImage(child, self.fldridx, wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(child, self.fldropenidx, wx.TreeItemIcon_Expanded)
            
            # add nodes for all the clusterings of the current data set
            for cIndex in fData.clustering:
                clust = self.tree.AppendItem(child, 
                                            cluster.methods.getStringRepr(fData.methodIDs[cIndex]) + 
                                            " " + str(cIndex+1))
                if ((fData.selectedClustering == cIndex) and (fData.ID == DataStore.getCurrentIndex())):
                    self.tree.SetItemBold(clust, True)
                toolTip = fData.clusteringInfo(cIndex)
                self.tree.SetPyData(clust, (dIndex,cIndex,toolTip)) #(data index, cluster index, tooltip)
                self.tree.SetItemImage(clust, self.fldridx, wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(clust, self.fldropenidx, wx.TreeItemIcon_Expanded)
                # set clustering options
                for line in toolTip.split('\n'):
                    if (line != ''):
                        info = self.tree.AppendItem(clust, line)
                        self.tree.SetPyData(info, None)
                
                if (fData.infoExpanded[cIndex]):
                    self.tree.Expand(clust)
            
            # recursive call to build the tree for any children
            visited.append(fData.ID)
            self.buildTree(child, dict([(i,DataStore.getData()[i]) for i in fData.children]), visited)
            
            if (fData.nodeExpanded and self.tree.GetChildrenCount(child) > 0):
                self.tree.Expand(child)





    def getItemSelectionData(self):
        """
        Get the data item behind the currently selected tree item.
        
        @rtype treeItemData: int or tuple
        @return treeItemData: A single index if the item to be selected is
            a FacsData object. Otherwise a 2-tuple indicating the index of 
            the FacsData object and the index of the clustering within it
            to select.
        """
        sel = self.tree.GetSelection()
        return self.tree.GetItemPyData(sel)
    
    
    def getSanitizedItemSelectionData(self):
        data = self.getItemSelectionData()
        if (isinstance(data,int)):
            return (data, None)
        if (isinstance(data,tuple)):
            return (data[0], data[1])
    
   
    def applyToSelection(self, dataFunc, clustFunc):
        """
        Apply a function to the data selection depending on whether it refers
        to a FacsData object or a clustering of a FacsData object.
        
        @type dataFunc: function
        @param dataFunc: A function to apply to the FacsData object selected.
        @type clustFunc: function
        @param clustFunc: A function to apply to the clustering of the FacsData
            object selected.
        """
        data = self.getItemSelectionData()
        # determine if item is a data set or a clustering and select it
        if (isinstance(data,int)):
            dataFunc(data)
        if (isinstance(data,tuple)):
            clustFunc(DataStore.selectDataSet(data[0]), data[1])
            
            
    def selectDataByTreeSelection(self):
        """
        Using the selected tree item, set the corresponding object 
        in the data store as the current selection.
        """
        self.applyToSelection(DataStore.selectDataSet, FacsData.selectClustering)
        
    def plotData(self, plotType):
        dataID, clusterID = self.getSanitizedItemSelectionData()
        self.Parent.TopLevelParent.facsPlotPanel.plotData(dataID, clusterID, plotType)
            
    def clearClusteringSelection(self):
        index = self.getItemSelectionData()
        DataStore.getData()[index].selectedClustering = None
        self.updateTree()
    
    def deleteSelection(self):
        """
        Delete the data object referenced by the current tree selection.
        """
        self.Parent.TopLevelParent.facsPlotPanel.deleteAssociatedSubplots(self.getSanitizedItemSelectionData())
        self.applyToSelection(DataStore.remove, FacsData.removeClustering)
        self.updateTree()
        
    def setDataExpanded(self, item, flag):
        data = self.tree.GetItemPyData(item)
        if (isinstance(data, int)):
            DataStore.getData()[data].nodeExpanded = flag
        if (isinstance(data, tuple)):
            DataStore.getData()[data[0]].infoExpanded[data[1]] = flag


    # Tree Event Handling
    def OnLeftDown(self, event):
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        if item:
            self.tree.SelectItem(item)
            self.selectDataByTreeSelection()
            self.updateTree()
        event.Skip()


    def OnRightUp(self, event):
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        if item:
            self.tree.SelectItem(item)
            data = self.getItemSelectionData()
            if (isinstance(data, tuple)):
                self.Parent.PopupMenu(TreePopupMenu(self, dataItem=False), pt)
            elif (isinstance(data, int)):
                self.Parent.PopupMenu(TreePopupMenu(self, dataItem=True), pt)
            else:
                pass


    def OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)


    def OnItemExpanded(self, event):
        item = event.GetItem()
        if item:
            self.setDataExpanded(item, True)

    def OnItemCollapsed(self, event):
        item = event.GetItem()
        if item:
            self.setDataExpanded(item, False)

#---------------------------------------------------------------------------

    
    
    
    
    
    
    
    
    
    
    
            