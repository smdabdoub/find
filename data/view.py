"""
This module contains classes and methods used to visualize FACS data.

@author: Shareef Dabdoub
@organization: The Ohio State University
@organization: Nationwide Children's Hospital
"""


# Local imports
from display.contextmenus import SubplotPopupMenu
from display.dialogs import EditNameDialog
from display.formatters import IntFormatter
import plot.methods as pmethods
import plot.dialogs as pdialogs
from store import DataStore, FigureStore

# 3rd Party imports
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.figure as mfig
from matplotlib.pyplot import subplot
import wx


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
        self.singlePlotWindow = False
        
        # initialize matplotlib stuff
        self.figure = mfig.Figure(None, dpi)
        self.figure.subplots_adjust(wspace=0.5, hspace=0.5)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self._setColor(color)
        self.SetBackgroundColour('white')
        
        self._resizeflag = True
        self._setSize()

        self.Bind(wx.EVT_IDLE, self._onIdle)
        self.Bind(wx.EVT_SIZE, self._onSize)
   
        
        
    def saveFigure(self, fname, fmt, transparent=False):
        self.figure.savefig(fname, format=fmt, transparent=transparent)


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



#TODO: decide whether to call it the selected subplot or current subplot, and rename everything to match
#TODO: have the parent class pass in event handler(s) in order for it to be notified when certain things happen that require changes in the parent (instead of this class referencing the parent and directly making changes)
class FacsPlotPanel(PlotPanel):
    """
    The main display figure for the FACS data.
    """
    
    def __init__(self, parent, selectedAxes = None, **kwargs):
        self.updateAxes(selectedAxes)
        self.subplots = []
        self.subplotRows = 1
        self.subplotCols = 1
        self._selectedSubplotIndex = None
        
        self.XAxisColumn = None
        self.YAxisColumn = None
        

        # initiate plotter
        PlotPanel.__init__( self, parent, **kwargs )
        #self._setColor((100,100,100))
        self._setColor((255,255,255))
        self.figure.canvas.mpl_connect('button_press_event', self.OnClick)
        
        
    def OnClick(self, event):
        try:
            if (event.inaxes is not None):
                intVal = IntFormatter()
                plotNum = event.inaxes.get_title().split(':')[0]
                if intVal.validate(plotNum):
                    self.SelectedSubplotIndex = int(plotNum)
                
                # Right click
                if (event.button == 3):
                    pt = event.guiEvent.GetPosition()
                    self.PopupMenuXY(SubplotPopupMenu(self), pt.x, pt.y)
        except wx.PyAssertionError as pae:
            print pae
    

        
    def addSubplot(self, dataStoreIndex, clusteringIndex = None, plotType = pmethods.ID_PLOTS_SCATTER_2D):
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
        self.subplots.append(Subplot(n, dataStoreIndex, clusteringIndex, plotType, self.figure))
        self.SelectedSubplotIndex = n
        self.draw()    
        
    
    def deleteSubplot(self):
        """
        Deletes the currently selected subplot from the figure.
        """
        if (self.SelectedSubplotIndex is not None):
            del self.subplots[self.SelectedSubplotIndex-1]
            self.renumberPlots()
            self.draw()
        
        # when the selected subplot is deleted, there is no longer a selection
        self.SelectedSubplotIndex = None
        

    def deleteAssociatedSubplots(self, ids):
        """
        Delete any subplots associated with the specified data or clustering ids
        
        @type ids: tuple
        @param ids: A tuple containing either a data ID and a clustering ID 
                    or a data ID and None.
        """
        all, figPlots = [ids[0]], {None: self.subplots}
        if ids[1] is None:
            DataStore.get(ids[0]).collectAllChildren(all)

        # add subplot lists from figures in the store
        for fID, fig in FigureStore.getFigures().items():
            if fID != FigureStore.getSelectedIndex():
                figPlots[fID] = fig.subplots
            
        # remove matching subplots from all figures
        for fID, plots in figPlots.items():
            toDelete = []
            for n, subplot in enumerate(plots):
                if (subplot.dataIndex in all):
                    if ids[1] is None:
                        toDelete.append(n)
                    else: 
                        if subplot.clustIndex == ids[1]:
                            toDelete.append(n)
            
            # delete flagged subplots by creating a new list w/o the deleted indices
            plots = [plots[i] for i in range(len(plots)) if not (i in toDelete)]
            if fID is None:
                self.subplots = plots
            else:
                FigureStore.get(fID).subplots = plots
            
            self.renumberPlots(fID)
        
        self.draw()
        
        
    def renameSubplot(self):
        """
        Allows the user to set the title of the selected subplot.
        """
        subplot = self.subplots[self.SelectedSubplotIndex-1]
        titleDlg = EditNameDialog(self, subplot.Title.split(':')[1].strip())
        if (titleDlg.ShowModal() == wx.ID_OK):
            subplot.Title = titleDlg.Text
            titleDlg.Destroy()
            self.draw()
        
        titleDlg.Destroy()
        

    def renumberPlots(self, figureID=None):
        """ 
        Renumber the subplots and their titles by their position in the list
        beginning with 1.
        """
        fig = None, None
        if figureID is None:
            fig = self
        else:
            fig = FigureStore.get(figureID)
            
        # renumber
        for n, subplot in enumerate(fig.subplots):
            subplot.n = n+1
            subplot.Title = subplot.Title.split(': ')[1]
        
        # set selected subplot
        ss = len(fig.subplots) if (len(fig.subplots) > 0) else None
        if figureID is None:
            self.SelectedSubplotIndex = ss
        else:
            fig.selectedSubplot = ss
            
    
    def plotData(self, dataID, clusterID=None, plotType=pmethods.ID_PLOTS_SCATTER_2D):
        """
        Plots the specified data set to the currently selected subplot.
        
        @type dataID: int
        @var dataID: The ID of the data set to be plotted
        @type clusterID: int
        @var clusterID: The ID of the specific clustering to be plotted, if any.
        @type plotType: int
        @var plotType: The type of plot to be draw. Defaults to scatter plot.     
        """
        if (self.SelectedSubplotIndex is not None):
            if isinstance(plotType, int):
                plotType = pmethods.strID(plotType)
            self.subplots[self.SelectedSubplotIndex-1] = Subplot(self.SelectedSubplotIndex, dataID, 
                                                            clusterID, plotType, self.figure)
            self.draw()
        else:
            self.addSubplot(dataID, clusterID, plotType)
            
    @property
    def SelectedSubplotIndex(self):
        """Get/Set the user-selected subplot"""
        if self._selectedSubplotIndex is not None:
            return self._selectedSubplotIndex

    @SelectedSubplotIndex.setter
    def SelectedSubplotIndex(self, plotNum):
        if (plotNum > 0):
            self._selectedSubplotIndex = plotNum
            self.parent.setSelectedPlotStatus("Subplot "+str(plotNum)+" selected")
            self.parent.chkLinked.Value = self.CurrentSubplotLinked
        else:
            self.parent.setSelectedPlotStatus("")
            self.parent.chkLinked.Value = False
            self._selectedSubplotIndex = None
                
    @property
    def CurrentSubplot(self):
        """
        Retrieves the subplot instance of the currently selected subplot.
        """
        if self.SelectedSubplotIndex is not None:
            if len(self.subplots) > 0:
                return self.subplots[self.SelectedSubplotIndex-1]
    
    @CurrentSubplot.setter
    def CurrentSubplot(self, subplot):
        """
        Sets the current subplot to a new Subplot instance
        
        @type subplot: Subplot
        @param subplot: A new Subplot instance
        """      
        if self.SelectedSubplotIndex is None:
            self.SelectedSubplotIndex = len(self.subplots)
        
        if len(self.subplots) > 0:
            self.subplots[self.SelectedSubplotIndex-1] =  subplot
        else:
            self.subplots.append(subplot)
            self.SelectedSubplotIndex = 1    

        
    def setCurrentSubplotLinked(self, linked):
        if len(self.subplots) > 0:
            if (not linked):
                self.subplots[self.SelectedSubplotIndex-1].linkedDimensions = (self.XAxisColumn, self.YAxisColumn)
            else:
                self.subplots[self.SelectedSubplotIndex-1].linkedDimensions = None
                self.draw()
    
    def getCurrentSubplotLinked(self):
        if self.SelectedSubplotIndex is not None:
            return self.subplots[self.SelectedSubplotIndex-1].linkedDimensions is None
        return False
    
    CurrentSubplotLinked = property(getCurrentSubplotLinked, setCurrentSubplotLinked)
    
    
    def showSubplotProperties(self):
        """
        Display the properties dialog for the current subplot.
        """
        subplot = self.CurrentSubplot
        dlg = pdialogs.getPlotOptionsDialog(self, subplot)
        if dlg is not None:
            if (dlg.ShowModal() == wx.ID_OK):
                subplot.Options = dlg.Options
                self.draw()
            dlg.Destroy()
        else:
            dlg = wx.MessageBox(None, 'There are no user-definable properties for this plot.',
                                   'No Properties Dialog', wx.OK|wx.ICON_INFORMATION)
    
    
    @property
    def SelectedAxes(self):
        return (self.XAxisColumn, self.YAxisColumn)
    
    
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
        if (selectedAxes is not None and len(selectedAxes) >= 2):
            self.XAxisColumn = selectedAxes[0]
            self.YAxisColumn = selectedAxes[1]
            
        if (redraw):
#            for subplot in self.subplots:
#                subplot.drawFlag = True
            self.draw()


    @property
    def Grid(self):
        return (self.subplotRows, self.subplotCols)
    
    #TODO: The redraw param should probably default to False
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
        self.canvas.figure.clear()
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
        else:
            #TODO: test this case thoroughly
            self.canvas.draw()

            


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
        if (subplot.linkedDimensions is not None):
            dims = subplot.linkedDimensions
        subplot.mnp = self.mnp(row, col, subplot.n)
        if (subplot.Title == ''):
            subplot.Title = subplot.DisplayName
        
        # Plot data using available methods in data.plot
        pmethods.getMethod(subplot.plotType)(subplot, self.figure, dims)
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
    
    def __init__(self, n=None, dataStoreIndex=None, clusteringIndex=None, plotType=pmethods.ID_PLOTS_SCATTER_2D, parent=None):
        self.n = n
        self.dataIndex = dataStoreIndex
        self.clustIndex = clusteringIndex
        self.plotType = plotType
        self.opts = {}
        self.axes = None
        self.parent = parent
        self.mnp = None  #TODO: switch to allow 1,1,1 format for alt method in maplotlib
        self._title = ''
        self.linkedDimensions = None
        self.drawFlag = True
        
    def load(self, attrs):
        """
        Assign values to each of the Subplot private members using the 
        attributes for a Subplot instance from a saved project file.
        
        @type attrs: dict
        @param attrs: The __dict__ copied from a Subplot instances                              
        """
        for key in attrs:
            self.__dict__[key] = attrs[key]


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
        
    Data = property(getData, setData, 
                    doc="""Get the FacsData instance or Set the DataStore ID 
                           of the dataset visualized by this subplot.""")
    

    
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
        
    Clustering = property(getClustering, setClustering, 
                          doc="""Get/Set the index of the clustering of the 
                                 data set visualized by this subplot""")
    
    @property
    def Labels(self):
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
    
    Title = property(getTitle, setTitle, 
                     doc='The visible title at the top of the subplot.')
    
    # Plot Options
    def getOptions(self):
        return self.opts
    def setOptions(self, options):
        self.opts.update(options)
    
    Options = property(getOptions, setOptions, 
                       doc='Get/Set the display options for this subplot')




# Module methods
def switchFigures(panel, currentFigure, newFigure, redraw=False):
    saveToFigure(panel, currentFigure)
    loadFigure(panel, newFigure, redraw)


def loadFigure(panel, figure, redraw=False):
    panel.subplots = figure.subplots
    panel.SelectedSubplotIndex = figure.selectedSubplot
    panel.updateSubplotGrid(figure.grid[0], figure.grid[1], False)
    panel.updateAxes(figure.axes, redraw)
    
    
def saveToFigure(panel, figure):    
    """
    Save existing plots to a given Figure
    """
    figure.subplots = panel.subplots
    figure.selectedSubplot = panel.SelectedSubplotIndex
    figure.grid = panel.Grid
    figure.axes = panel.SelectedAxes
    
    
    
    
    
    
            