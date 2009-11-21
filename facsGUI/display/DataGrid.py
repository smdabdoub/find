
from dialogs import EditNameDialog

import  wx
import  wx.grid             as  gridlib
import  wx.lib.gridmovers   as  gridmovers

#---------------------------------------------------------------------------

class CustomDataTable(gridlib.PyGridTableBase):
    def __init__(self, data, labels):
        gridlib.PyGridTableBase.__init__(self)
        self.data = data
        self.labels = labels

        self.ids = range(len(labels))

        self.rowLabels = range(len(data))

        # Associate the column identifiers to the data dimension names
        self.colLabels = dict([(i, labels[i]) for i in self.ids])

        # This is a list of dictionaries for each row of data. Each dictionary is of 
        # length len(labels) and contains a mapping for each column with its associated
        # dimension from the data set
        self.data = [dict([(i, row[i]) for i in self.ids]) for row in data]

    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.ids)

    def IsEmptyCell(self, row, col):
        id = self.ids[col]
        return not self.data[row][id]

    def GetValue(self, row, col):
        id = self.ids[col]
        return self.data[row][id]

    def SetValue(self, row, col, value):
        id = self.ids[col]
        self.data[row][id] = value

    #--------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display column labels
    def GetColLabelValue(self, col):
        id = self.ids[col]
        return self.colLabels[id]

    # Called when the grid needs to display row labels
    def GetRowLabelValue(self,row):
        return self.rowLabels[row]
    
    def SetColLabelValue(self, col, label):
        id = self.ids[col]
        self.colLabels[id] = label
    
    def ReorderColLabels(self):
        self.colLabels = [self.colLabels[id] for id in self.ids]

    #--------------------------------------------------
    # Methods added for demo purposes.

    # The physical moving of the cols/rows is left to the implementer.
    # Because of the dynamic nature of a wxGrid the physical moving of
    # columns differs from implementation to implementation

    # Move the column
    def MoveColumn(self,frm,to):
        grid = self.GetView()

        if grid:
            # Move the identifiers
            old = self.ids[frm]
            del self.ids[frm]

            if to > frm:
                self.ids.insert(to-1,old)
            else:
                self.ids.insert(to,old)

            # Notify the grid
            grid.BeginBatch()
           
            msg = gridlib.GridTableMessage(
                    self, gridlib.GRIDTABLE_NOTIFY_COLS_INSERTED, to, 1
                    )
            grid.ProcessTableMessage(msg)

            msg = gridlib.GridTableMessage(
                    self, gridlib.GRIDTABLE_NOTIFY_COLS_DELETED, frm, 1
                    )
            grid.ProcessTableMessage(msg)
            
            grid.EndBatch()

    # Move the row
    def MoveRow(self,frm,to):
        grid = self.GetView()

        if grid:
            # Move the rowLabels and data rows
            oldLabel = self.rowLabels[frm]
            oldData = self.data[frm]
            del self.rowLabels[frm]
            del self.data[frm]

            if to > frm:
                self.rowLabels.insert(to-1,oldLabel)
                self.data.insert(to-1,oldData)
            else:
                self.rowLabels.insert(to,oldLabel)
                self.data.insert(to,oldData)

            # Notify the grid
            grid.BeginBatch()

            msg = gridlib.GridTableMessage(
                    self, gridlib.GRIDTABLE_NOTIFY_ROWS_INSERTED, to, 1
                    )
            grid.ProcessTableMessage(msg)

            msg = gridlib.GridTableMessage(
                    self, gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED, frm, 1
                    )
            grid.ProcessTableMessage(msg)
    
            grid.EndBatch()

    def Refresh(self):
        grid = self.GetView()
        if grid:
            grid.BeginBatch()
            msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
            grid.ProcessTableMessage(msg)
            grid.EndBatch()

#---------------------------------------------------------------------------
class DataGrid(gridlib.Grid):
    def __init__(self, parent, data, labels):
        gridlib.Grid.__init__(self, parent, -1)

        table = CustomDataTable(data, labels)

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)

        # Enable Column moving
        gridmovers.GridColMover(self)
        self.Bind(gridmovers.EVT_GRID_COL_MOVE, self.OnColMove, self)
        self.colsMoved = False

        # Enable Row moving
        #gridmovers.GridRowMover(self)
        #self.Bind(gridmovers.EVT_GRID_ROW_MOVE, self.OnRowMove, self)
        
        # Enable column label editing
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLDClick, self)
        
    @property
    def ColumnArrangement(self):
        return self.GetTable().ids
    @property
    def ColumnLabels(self):
        """
        @rtype dict
        @return: A dictionary mapping the data column with its label
        """
        return self.GetTable().colLabels
    

    def OnLabelLDClick(self, evt):
        colID = self.GetTable().ids[evt.Col]
        colLabel = self.GetTable().colLabels[colID]
        print "Label Double Click Event: clicked on", colLabel
        dlg = EditNameDialog(self, colLabel)
        if (dlg.ShowModal() == wx.ID_OK):
            self.GetTable().SetColLabelValue(colID, dlg.Text)
            self.GetTable().Refresh()
            print "Label changed to:", dlg.Text

    # Event method called when a column move needs to take place
    def OnColMove(self, evt):
        frm = evt.GetMoveColumn()       # Column being moved
        to = evt.GetBeforeColumn()      # Before which column to insert
        self.GetTable().MoveColumn(frm,to)
        self.GetTable().ReorderColLabels()
        self.colsMoved = True

    # Event method called when a row move needs to take place
    def OnRowMove(self, evt):
        frm = evt.GetMoveRow()          # Row being moved
        to = evt.GetBeforeRow()         # Before which row to insert
        self.GetTable().MoveRow(frm,to)






        
        
        
        
        
        
        
        
