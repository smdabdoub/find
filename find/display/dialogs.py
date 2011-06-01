"""
This module contains all dialog classes necessary for non data-related menu items.

@author: Shareef Dabdoub
@organization: The Ohio State University
@organization: Nationwide Children's Hospital  
"""
import formatters as f

import math
import wx

class ValidatedDialog(wx.Dialog):
    """
    Base class for dialogs that need input to be validated.
    
    All subclasses should implement the validate method.
    
    Unless special action is needed on clicking OK, subclasses can simply bind
    super(subclass, self).cmdOK_click to run the validation routine and 
    continue.
    """
    def validate(self): 
        """
        Validates user input to the dialog.
        
        :@rtype: list
        :@return: A list of strings, one for each validation error. Empty if no errors. 
        """
        pass
    
    def cmdOK_click(self, event):
        """
        Call the form validation method and display any error messages.
        """
        msg = self.validate()
        if len(msg) > 0:
            dlg = wx.MessageDialog(None, '\n'.join(msg), 
                                   'Invalid input', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        event.Skip()
        

#TODO: validate for no input
class EditNameDialog(wx.Dialog):
    """
    This dialog allows the user to rename the labels of the incoming data set
    """
    
    def __init__(self, parent, label):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Edit Label', size=(200,103))
        self.CenterOnParent()
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.formSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.formSizer.AddSpacer(5)
        self.formSizer.Add(wx.StaticText(self, -1, 'Edit Label:'), 0, wx.ALIGN_LEFT)
        self.formSizer.AddSpacer(5)
        self.txtLabel = wx.TextCtrl(self, wx.ID_ANY, label)
        self.formSizer.Add(self.txtLabel, 2, wx.EXPAND)
        self.formSizer.AddSpacer(5)
        
        
        self.sizer.AddSpacer(10)
        self.sizer.Add(self.formSizer, 1, wx.EXPAND | wx.ALIGN_LEFT)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND)
        self.sizer.AddSpacer(5)
        
        self.SetSizer(self.sizer)
        
    @property
    def Text(self):
        """Retrieve the user-specified text"""
        return self.txtLabel.Value
    

from display.DataGrid import DataGrid

class SampleDataDisplayDialog(wx.Dialog):
    """
    This dialog uses the DataGrid class in the display package to give the user
    a sample view of the data they are importing, as well as allowing them to 
    rearrange and rename the columns
    """
    
    def __init__(self, parent, data, labels, title='Sample Data Display', applyAll=True, enableColMoving=True):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE, size=(450, 300))
        self.CenterOnParent()
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.dataGrid = DataGrid(self, data, labels, enableColMoving=enableColMoving)
        if applyAll:
            self.chkApplyToAll = wx.CheckBox(self, wx.ID_ANY, 'Apply to all files')
        
        self.sizer.Add(self.dataGrid, 1, wx.EXPAND)
        if applyAll:
            self.sizer.AddSpacer(10)
            self.sizer.Add(self.chkApplyToAll, 0, wx.EXPAND | wx.LEFT, 10)
        self.sizer.AddSpacer(5)
        self.sizer.Add(self.CreateButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND)
        self.sizer.AddSpacer(5)
        
        self.SetSizer(self.sizer)
        
    @property
    def ColumnsMoved(self):
        return self.dataGrid.colsMoved
    @property
    def ApplyToAll(self):
        return self.chkApplyToAll.Value
    @property
    def ColumnArrangement(self):
        """Retrieves the column labels as set by the user in the data grid"""
        return self.dataGrid.ColumnArrangement
    @property
    def ColumnLabels(self):
        return self.dataGrid.ColumnLabels
        


class DimensionExclusionDialog(wx.Dialog):
    """
    This dialog allows the user to choose which dimensions of the loaded
    FACS data will be used in analysis
    """
    
    def __init__(self, parent, dimensions):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Choose Dimensions for Analysis')
        self.CenterOnParent()
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.formSizer = wx.GridSizer(int(math.ceil(len(dimensions)/2.0)), 2, vgap=5, hgap=20) #rows,cols,vgap,hgap
        #self.formSizer = wx.GridSizer(len(dimensions), 1, vgap=5, hgap=20)
        self.chkApplyToAll = wx.CheckBox(self, wx.ID_ANY, 'Apply to all files')
        self.checkBoxes = []
        
        for dim in dimensions:
            self.checkBoxes.append(wx.CheckBox(self, wx.ID_ANY, dim))
            self.checkBoxes[-1].SetValue(True)
            self.formSizer.Add(self.checkBoxes[-1], 1, wx.EXPAND)
        
        self.sizer.AddSpacer(15)
        #self.sizer.Add(wx.StaticText(self, -1, 'Exclude dimensions'), 0, wx.ALIGN_CENTER_HORIZONTAL)
        #self.sizer.AddSpacer(20)
        self.sizer.Add(self.formSizer, 1, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.chkApplyToAll, 0, wx.EXPAND | wx.LEFT, 10)
        self.sizer.AddSpacer(5)
        self.sizer.Add(self.CreateButtonSizer(wx.OK), 0, wx.EXPAND)
        self.sizer.AddSpacer(5)
        
        self.SetSizer(self.sizer)
           
    
    @property
    def ApplyToAll(self):
        return self.chkApplyToAll.Value
    
    @property
    def SelectedDimensions(self):
        return [i for i in range(len(self.checkBoxes)) if self.checkBoxes[i].IsChecked()]
        
        

class FigureSetupDialog(ValidatedDialog):
    """
    This dialog allows the user to specify the grid for subplots on the main figure.
    """
    
    def __init__(self, parent, rows=1, cols=1):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Plot Grid Setup', size=(200, 150))
        self.CenterOnParent()
        
        # create form controls
        self.txtRows = wx.TextCtrl(self, wx.ID_ANY, str(rows), size=(40,20))
        self.txtColumns = wx.TextCtrl(self, wx.ID_ANY, str(cols), size=(40,20))
        
        # create a table of label-input controls
        self.formSizer = wx.FlexGridSizer(3, 2, hgap=10)
        self.formSizer.SetFlexibleDirection(wx.HORIZONTAL)
        self.formSizer.Add(wx.StaticText(self, -1, 'Rows:'), 0, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtRows, 1)
        self.formSizer.Add(wx.StaticText(self, -1, 'Columns:'), 0, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtColumns, 1)
        
        # create the button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.buttonSizer.AffirmativeButton.Bind(wx.EVT_BUTTON, super(FigureSetupDialog, self).cmdOK_click)
        
        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.formSizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        self.SetSizer(self.sizer)
        
        
    def getRows(self):
        return int(self.txtRows.GetValue())
    
    def getColumns(self):
        return int(self.txtColumns.GetValue())
    
    def validate(self):
        intVal = f.IntFormatter()
        msg = []
        
        if not intVal.validate(self.txtRows.Value):
            msg.append("Rows: A valid number must be entered.")
        elif int(self.txtRows.Value) < 1 or int(self.txtRows.Value) > 9:
            msg.append("Rows: Enter a value between 1 and 9.")
        
        if not intVal.validate(self.txtColumns.Value):
            msg.append("Columns: A valid number must be entered.")
        elif int(self.txtColumns.Value) < 1 or int(self.txtColumns.Value) > 9:
            msg.append("Columns: Enter a value between 1 and 9.")
        
        return msg
        


class DataInfoDialog(wx.Dialog):
    """
    This class displays basic information for data sets, and embedded header 
    information for FCS 3.0 files.
    """
    def __init__(self, parent, data):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Data Information', 
                           style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE, size=(280, 500))
        self.CenterOnParent() 
        
        textAnn = []
        textAnn.append(('display name', data.displayname))
        textAnn.append(('selected dimensions', ', '.join([data.labels[i] for i in data.selDims])))
        
        if 'text' in data.annotations:
            textAnn.extend(sorted(data.annotations['text'].iteritems()))
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.dataGrid = DataGrid(self, textAnn, ['Parameter', 'Value'], False, False)
        
        self.sizer.Add(self.dataGrid, 1, wx.EXPAND)
        self.sizer.AddSpacer(5)
        self.sizer.Add(self.CreateButtonSizer(wx.OK), 0, wx.EXPAND)
        self.sizer.AddSpacer(5)
        
        self.SetSizer(self.sizer)

        
        
        

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
      
        
        