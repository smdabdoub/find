'''
Created on Aug 23, 2010

@author: dabdoubs
'''

from cluster.util import clusteringInfo
from data.store import FacsData, DataStore
from display.dialogs import DataInfoDialog, EditNameDialog
from display.contextmenus import TreePopupMenu
import cluster.methods
import wx.lib.customtreectrl as CT

import wx


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
        """
        Rebuilds the tree from the current state of the DataStore.
        """
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
                toolTip = clusteringInfo(fData, cIndex)
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
        
    
    def displayDataInfo(self):
        dataID, _ = self.getSanitizedItemSelectionData()
        data = DataStore.get(dataID)
        dlg = DataInfoDialog(self.Parent, data)
        dlg.Show()
    
    def plotData(self, plotType):
        dataID, clusterID = self.getSanitizedItemSelectionData()
        self.Parent.TopLevelParent.facsPlotPanel.plotData(dataID, clusterID, plotType)
            
    def clearClusteringSelection(self):
        index = self.getItemSelectionData()
        DataStore.getData()[index].selectedClustering = None
        self.updateTree()
    
    def renameItem(self):
        """
        Give a new display name to the currently selected data item
        """
        dataID, clusterID = self.getSanitizedItemSelectionData()
        data = DataStore.get(dataID)
        dlg = EditNameDialog(self.Parent, data.displayname)
        if dlg.ShowModal() == wx.ID_OK:
            data.displayname = dlg.Text
            item = self.tree.GetSelection()
            item.SetText(dlg.Text)
            self.tree.RefreshSelected()
            item.SetHilight(False)
            item.SetHilight(True)
        
        dlg.Destroy()
            
    
    def deleteSelection(self):
        """
        Delete the data object referenced by the current tree selection.
        """
        self.Parent.TopLevelParent.facsPlotPanel.deleteAssociatedSubplots(self.getSanitizedItemSelectionData())
        self.applyToSelection(DataStore.remove, FacsData.removeClustering)
        # if all data deleted, clear axes selectors
        if len(DataStore.getData()) == 0:
            self.Parent.TopLevelParent.updateAxesList([])
        
        self.updateTree()
        
    def setDataExpanded(self, item, flag):
        data = self.tree.GetItemPyData(item)
        if (isinstance(data, int)):
            DataStore.getData()[data].nodeExpanded = flag
        if (isinstance(data, tuple)):
            DataStore.getData()[data[0]].infoExpanded[data[1]] = flag


    # Tree Event Handling
    def OnLeftDown(self, event):
        pt = event.GetPosition()
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