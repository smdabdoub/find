'''
Created on Aug 23, 2010

@author: dabdoubs
'''

from cluster.util import clusteringInfo
from data.store import FacsData, DataStore, FigureStore, Figure
from data.view import switchFigures
from display.dialogs import DataInfoDialog, EditNameDialog
from display.contextmenus import DataTreePopupMenu, FigureTreePopupMenu
import cluster.methods
import wx.lib.customtreectrl as CT
import wx



DATA_SET_ITEM = 0
FIGURE_SET_ITEM = 1


class FacsTreeCtrlPanel(wx.Panel):
    def __init__(self, parent):
        # Use the WANTS_CHARS style so the panel doesn't eat the Return key.
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS, size=(200,550))
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.tree = CT.CustomTreeCtrl(self, wx.NewId(), wx.DefaultPosition, (200,550), CT.TR_DEFAULT_STYLE)
        self.dataTreeExpanded = True
        self.figureTreeExpanded = True

        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        self.fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        self.figureicn   = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE,  wx.ART_OTHER, isz))

        self.tree.SetImageList(il)
        self.il = il

        self.updateTree()

        self.Bind(CT.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, self.tree)
        self.Bind(CT.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, self.tree)
        self.tree.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.tree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        


    def updateTree(self):
        """
        Rebuilds the tree from the current state of the DataStore.
        """
        self.tree.DeleteAllItems()
        
        self.root = self.tree.AddRoot("Project")
        self.tree.SetPyData(self.root, None)
        self.tree.SetItemImage(self.root, self.fldridx, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, self.fldropenidx, wx.TreeItemIcon_Expanded)
        
        
        dataTree = self.tree.AppendItem(self.root, "Data Sets")
        self.tree.SetPyData(dataTree, DATA_SET_ITEM)
        self.tree.SetItemImage(dataTree, self.fldridx, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(dataTree, self.fldropenidx, wx.TreeItemIcon_Expanded)
        
        figsTree = self.tree.AppendItem(self.root, "Figure Sets")
        self.tree.SetPyData(figsTree, FIGURE_SET_ITEM)
        self.tree.SetItemImage(figsTree, self.fldridx, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(figsTree, self.fldropenidx, wx.TreeItemIcon_Expanded)

        # create tree
        self.buildDataTree(dataTree, DataStore.getData(), [])
        self.buildFigureTree(figsTree, FigureStore.getFigures())
        self.tree.Expand(self.root)
        if self.dataTreeExpanded:
            self.tree.Expand(dataTree)
        if self.figureTreeExpanded:
            self.tree.Expand(figsTree)    


    def buildDataTree(self, parent, dataDict, visited):
        for dIndex, fData in dataDict.iteritems():
            # add tree node for the FACS data set
            if fData.ID in visited:
                return
            child = self.tree.AppendItem(parent, fData.displayname)
            if (DataStore.getCurrentIndex() == dIndex):
                self.tree.SetItemBold(child, True)
            self.tree.SetPyData(child, (DATA_SET_ITEM, dIndex))
            self.tree.SetItemImage(child, self.fldridx, wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(child, self.fldropenidx, wx.TreeItemIcon_Expanded)
            
            # add nodes for all the clusterings of the current data set
            for cIndex in fData.clustering:
                clust = self.tree.AppendItem(child, 
                                            cluster.methods.getStringRepr(fData.methodIDs[cIndex]) + 
                                            " " + str(cIndex+1))
                if ((fData.selectedClustering == cIndex) and (fData.ID == DataStore.getCurrentIndex())):
                    self.tree.SetItemBold(clust, True)
                toolTip = clusteringInfo(fData, cIndex)
                self.tree.SetPyData(clust, (DATA_SET_ITEM, dIndex, cIndex, toolTip)) #(data index, cluster index, tooltip)
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
            self.buildDataTree(child, dict([(i,DataStore.getData()[i]) for i in fData.children]), visited)
            
            if (fData.nodeExpanded and self.tree.GetChildrenCount(child) > 0):
                self.tree.Expand(child)


    def buildFigureTree(self, root, figures):
        for id, fig in figures.iteritems():
            child = self.tree.AppendItem(root, fig.name)
            if (FigureStore.getSelectedIndex() == id):
                self.tree.SetItemBold(child, True)
            self.tree.SetPyData(child, (FIGURE_SET_ITEM, id))
            self.tree.SetItemImage(child, self.figureicn, wx.TreeItemIcon_Normal)
        



    def getItemSelectionData(self):
        """
        Get the data item behind the currently selected tree item.
        
        @rtype treeItemData: int or tuple
        @return treeItemData: An int if the selected item is
            a sub-root node, i.e. the Data Sets or Figure Sets nodes. Otherwise a n-tuple with the 
            set type followed by the object ID, any subset IDs (clustering), and any other included info.
        """
        sel = self.tree.GetSelection()
        return self.tree.GetItemPyData(sel)
    
    
    def getSanitizedItemSelectionData(self):
        """
        Retrieves the selected item data. If data is a tuple 
        (i.e. data, clustering, or figure) it returns a 2- or 3-tuple
        as appropriate.
        
        Data: 2-tuple - (DATA_SET_ITEM, data ID)
        Clustering: 3-tuple - (DATA_SET_ITEM, data ID, cluster ID)
        Figure: 2-tuple - (FIGURE_SET_ITEM, figure ID)
        
        @rtype: tuple
        @return: A 2 or 3-tuple depending on the selected item data.
        """
        data = self.getItemSelectionData()
        
        # data, clustering, or figure
        if (isinstance(data,tuple)):
            # clustering
            if len(data) > 2:
                return (data[0], data[1], data[2])
            else:
                return data
    
   
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
        data = self.getSanitizedItemSelectionData()
        
        if data is not None and data[0] is DATA_SET_ITEM:
            # determine if item is a data set or a clustering and select it
            if len(data) == 2:
                dataFunc(data[1])
            if len(data) == 3:
                clustFunc(DataStore.selectDataSet(data[1]), data[2])
            
            
    def selectItemTreeSelection(self):
        """
        Using the selected tree item, set the corresponding object 
        in the data store as the current selection.
        """
        item = self.getSanitizedItemSelectionData()
        
        if item is not None:
            if item[0] is DATA_SET_ITEM:
                self.applyToSelection(DataStore.selectDataSet, FacsData.selectClustering)
            
            if item[0] is FIGURE_SET_ITEM:
                if item[1] != FigureStore.getSelectedIndex():
                    currFig = FigureStore.getSelectedFigure()
                    newFig = FigureStore.get(item[1])
                    switchFigures(self.Parent.TopLevelParent.facsPlotPanel, currFig, newFig, True)
                    FigureStore.setSelectedFigure(item[1])
        
    
    def displayDataInfo(self):
        item = self.getSanitizedItemSelectionData()
        if item is not None and item[0] is DATA_SET_ITEM:
            data = DataStore.get(id)
            dlg = DataInfoDialog(self.Parent, data)
            dlg.Show()
    
    def plotData(self, plotType):
        item = self.getSanitizedItemSelectionData()
        
        if item is None:
            return
        
        dataID = item[1]
        clusterID = None if len(item) < 3 else item[2]
        self.Parent.TopLevelParent.facsPlotPanel.plotData(dataID, clusterID, plotType)
            
    def clearClusteringSelection(self):
        item = self.getSanitizedItemSelectionData()
        
        if item is not None and item[0] is DATA_SET_ITEM:
            DataStore.get(id).selectedClustering = None
            self.updateTree()
    
    def renameItem(self):
        """
        Give a new display name to the currently selected data item
        """
        item = self.getSanitizedItemSelectionData()
        if item is None:
            return
        
        if (item[0] is DATA_SET_ITEM):
            data = DataStore.get(item[1])
            dlg = EditNameDialog(self.Parent, data.displayname)
            if dlg.ShowModal() == wx.ID_OK:
                data.displayname = dlg.Text
            dlg.Destroy()
                
        if (item[0] is FIGURE_SET_ITEM):
            figure = FigureStore.get(item[1])
            dlg = EditNameDialog(self.Parent, figure.name)
            if dlg.ShowModal() == wx.ID_OK:
                figure.name = dlg.Text
            dlg.Destroy()
            
        item = self.tree.GetSelection()
        item.SetText(dlg.Text)
        self.tree.RefreshSelected()
        item.SetHilight(False)
        item.SetHilight(True)
            
    
    def deleteSelection(self):
        """
        Delete the data object referenced by the current tree selection.
        """
        item = self.getSanitizedItemSelectionData()
        
        if item is None:
            return
        
        if item[0] is DATA_SET_ITEM:
            self.Parent.TopLevelParent.facsPlotPanel.deleteAssociatedSubplots()
            self.applyToSelection(DataStore.remove, FacsData.removeClustering)
            # if all data deleted, clear axes selectors
            if len(DataStore.getData()) == 0:
                self.Parent.TopLevelParent.updateAxesList([])
                
        if item[0] is FIGURE_SET_ITEM:
            id = item[1]
            
            #TODO: figure out if this is a good shortcut for clearing the figure of subplots
            if id == FigureStore.getSelectedIndex():
                wx.MessageBox('The currently selected Figure cannot be deleted.', 'Invalid Action', wx.OK | wx.ICON_WARNING)
            else:
                FigureStore.remove(id)
        
        self.updateTree()
        
    def setExpanded(self, item, flag):
        #item = self.getItemSelectionData()
        data = self.tree.GetItemPyData(item)
        
        if isinstance(data, int):
            if data is DATA_SET_ITEM:
                self.dataTreeExpanded = flag
            if data is FIGURE_SET_ITEM:
                self.figureTreeExpanded = flag
        
        if isinstance(data, tuple):
            if data[0] is DATA_SET_ITEM:
                if len(data) == 2:
                    DataStore.getData()[data[1]].nodeExpanded = flag
                
                if len(data) > 3:
                    DataStore.getData()[data[1]].infoExpanded[data[2]] = flag


    # Tree Event Handling
    def OnLeftDown(self, event):
        pt = event.GetPosition()
        item, flags = self.tree.HitTest(pt)
        if item:
            self.tree.SelectItem(item)
            self.selectItemTreeSelection()
            
            self.updateTree()
        event.Skip()


    # Handle context menus
    def OnRightUp(self, event):
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        if item:
            self.tree.SelectItem(item)
            item = self.getSanitizedItemSelectionData()
            if item is None:
                return
            
            if item[0] is DATA_SET_ITEM:
                if len(item) == 2:
                    self.Parent.PopupMenu(DataTreePopupMenu(self, dataItem=True), pt)
                elif len(item) == 3:
                    self.Parent.PopupMenu(DataTreePopupMenu(self, dataItem=False), pt)
            
            if item[1] is FIGURE_SET_ITEM:
                self.Parent.PopupMenu(FigureTreePopupMenu(self), pt) 


    def OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)


    def OnItemExpanded(self, event):
        item = event.GetItem()
        if item:
            self.setExpanded(item, True)

    def OnItemCollapsed(self, event):
        item = event.GetItem()
        if item:
            self.setExpanded(item, False)















