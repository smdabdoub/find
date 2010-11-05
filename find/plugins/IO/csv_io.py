"""
This module provides the functionality to 
read and write CSV files from FC data. 
"""
from data.io import FILE_INPUT, FILE_OUTPUT
from display.dialogs import ValidatedDialog
from plugins.pluginbase import IOPlugin 

from numpy import loadtxt
import wx

import csv

__all__ = ['register_csv']

class CSVPlugin(IOPlugin):
    """Read and write CSV files."""
    def __init__(self, filename=None, fcData=None, window=None):
        super(CSVPlugin, self).__init__(filename, fcData, window)
    
    def register(self):
        return {FILE_INPUT: self.load, FILE_OUTPUT: self.save}
    
    @property
    def FileType(self):
        return 'Comma Separated Values (*.csv)|*.csv' 
    
    def load(self):
        """
        Load the specified FACS data file. It is assumed that the first line
        of the file contains the column labels.
        
        @type filename: string
        @param filename: The name of the FACS data file to be loaded
        
        @rtype: tuple
        @return: A tuple containing a list of column labels and numpy array 
            containing the actual FACS data.
        """
        # display options dialog first
        delim = ','
        skiprows = 1
        commentChar = '#'
        dlg = CSVOptionsDialog(self.window)
        if dlg.ShowModal() == wx.ID_OK:
            delim = dlg.Delimiter
            skiprows = dlg.HeaderLineNumber
            commentChar = dlg.CommentCharacter
            dlg.Destroy()            
        
            # Retrieve first line of column labels
            with open(self.filename,'r') as fcFile:
                for i, line in enumerate(fcFile):
                    if i < skiprows:
                        labels = line
                    else:
                        break
                labels = labels.rstrip().replace('"','').replace("'",'').split(delim)
            
            # load actual data
            try:
                data = loadtxt(self.filename, comments=commentChar, delimiter=delim, skiprows=skiprows)
            except Exception:
                wx.MessageBox("Please ensure there are no missing values and that correct values for the CSV options were specified.",
                              "Data Loading Error", wx.OK | wx.ICON_ERROR)
                return
            
            # text annotations
            textAnn = {'file name': self.filename}
            textAnn['events'] = len(data)
            
            return (labels, data, {'text': textAnn})
        
        else:
            dlg.Destroy() 


    
    def save(self):
        """
        Save the supplied Flow Cytometry data to a comma separated value file.
        """
        writer = csv.writer(open(self.filename, 'w'), delimiter=',')
        writer.writerow(self.fcData.labels)
        writer.writerows(self.fcData.data)
        
        
        
import display.formatters as f

class CSVOptionsDialog(ValidatedDialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'CSV File Import Options', size=(250, 200))
        self.CenterOnParent()
        
        # form controls
        self.txtHeaderLine = wx.TextCtrl(self, wx.ID_ANY, '1', size=(50,20))
        self.txtCommentChar = wx.TextCtrl(self, wx.ID_ANY, '#', size=(50,20))
        self.txtDelimiter = wx.TextCtrl(self, wx.ID_ANY, ',', size=(50,20))
        
        # create a table of label-input controls
        self.formSizer = wx.GridSizer(3, 2, vgap=20)
        self.formSizer.Add(wx.StaticText(self, wx.ID_ANY, 'Header line number:'), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtHeaderLine, 1)
        self.formSizer.Add(wx.StaticText(self, wx.ID_ANY, 'Comment character:'), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtCommentChar, 1)
        self.formSizer.Add(wx.StaticText(self, wx.ID_ANY, 'Delimiter:'), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtDelimiter, 1)
        
        # create the button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL | wx.HELP)
        self.buttonSizer.AffirmativeButton.Bind(wx.EVT_BUTTON, super(CSVOptionsDialog, self).cmdOK_click)
        self.buttonSizer.HelpButton.Bind(wx.EVT_BUTTON, self.cmdHelp_Click)
        
        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.formSizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 20)
        self.SetSizer(self.sizer)
            
    
    @property
    def CommentCharacter(self):
        return self.txtCommentChar.Value
    
    @property
    def Delimiter(self):
        return self.txtDelimiter.Value
    
    @property
    def HeaderLineNumber(self):
        return int(self.txtHeaderLine.Value)

    def validate(self):
        intVal = f.IntFormatter()
        msg = []
        
        if not intVal.validate(self.txtHeaderLine.Value):
            msg.append("Header line number: A valid number must be entered.")
        elif int(self.txtHeaderLine.Value) <= 0:
            msg.append("Header line number: Please enter a number larger than 0.")
        
        return msg
    
    
    def cmdHelp_Click(self, event):
        from display.help import HelpDialog
        HelpDialog(self, "CSV Import Help", htmlfile="help/csv_import.html", size=(300,200)).Show()


def register_csv():
    return ('csv', CSVPlugin)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        