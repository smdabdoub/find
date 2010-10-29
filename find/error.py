'''
This module contains all user-defined exceptions for FIND.
'''
import sys
import urllib
import urllib2
import wx

NO_NETWORK_CONNECTIVITY = 1

class PluginError(Exception):
    def __init__(self, errMsg):
        self.errMsg = errMsg
    
    def __str__(self):
        return self.errMsg

class ProjectLoadingError(Exception):
    def __init__(self, errType):
        self.errType = errType
    
    def __str__(self):
        return self.errType

class UnknownFileType(Exception):
    def __init__(self, filename):
        self.filename = filename
    def __str__(self):
        return "Tried to open %s.\nValid files must end in .csv or .fcs" % self.filename
    
class InvalidDataFile(Exception):
    def __init__(self, filename, msg):
        self.filename = filename
        self.msg = msg
        
    def __str__(self):
        return "Error opening %s: \n" % (self.filename, self.msg)
    
class InvalidPlotType(Exception):
    """
    Thrown when a plot command is issued for an unsupported data item.
    e.g. - A bar plot is issued for a clustering.
    """
    def __init__(self):
        pass
    def __str__(self):
        return "Plot type invalid for this item"
    
class UnimplementedFcsDataMode(Exception):
    """Exception raised on unimplemented data modes in fcs files
    
    mode: mode
    """
    
    def __init__(self, mode):
        self.mode = mode
        self.message = "Currently fcs data stored as type \'%s\' is unsupported" % mode


class ReportErrorDialog(wx.Dialog):
    def __init__(self, parent, err):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Report Error', size=(350, 265))
        self.CenterOnParent()
        
        self.err = str(err)
        self.success = True
        
        # Dialog widgets
        infoBox = wx.StaticText(self, wx.ID_ANY, "An error has occurred.\n\nPlease enter any related notes in the space below and click the Report button to send the log to us for analysis. Otherwise, click cancel.")
        infoBox.Wrap(325)
        self.txtReport = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.cmdReport = wx.Button(self, wx.ID_OK, "Report")
        self.cmdCancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cmdReport.Bind(wx.EVT_BUTTON, self.cmdReport_Click)

        stdButtonSizer = wx.StdDialogButtonSizer()
        stdButtonSizer.AddButton(self.cmdReport)
        stdButtonSizer.AddButton(self.cmdCancel)
        stdButtonSizer.Realize()
        
        # Dialog layout
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddSpacer(5)
        self.sizer.Add(infoBox, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.txtReport, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        self.sizer.AddSpacer(10)
        self.sizer.Add(stdButtonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        self.sizer.AddSpacer(5)
        
        self.Sizer = self.sizer

    @property
    def Success(self):
        return self.success
        
    # Event handlers
    def cmdReport_Click(self,event):
        try:
            sendErrorReport(self.err, str(self.txtReport.Value))
        except:
            self.success = False
        self.EndModal(wx.ID_OK)
        
        
        
# TODO: handle lack of internet connectivity by storing the error data and providing a menu option to upload the saved error data later 
def sendErrorReport(err, userMsg):
    errorData = urllib.urlencode({'userMsg' : userMsg, 'trace' : err})
    try:
        response = urllib2.urlopen('http://justicelab.org/find/report_error.php', errorData)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            sys.stderr.write('The server could not be reached.')
            sys.stderr.write('Reason: %s' % e.reason)
        elif hasattr(e, 'code'):
            sys.stderr.write('The server couldn\'t fulfill the request.')
            sys.stderr.write('Error code: %s' % e.code)
        raise


        
def warnUser(message, title='Warning'):
    wx.MessageBox(message, title, wx.OK | wx.ICON_WARNING)
        
        
        
        