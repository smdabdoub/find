'''
Created on Feb 12, 2010

@author: shareef
'''

# PLOTTING METHOD
import numpy as np

def boxplot(subplot, figure, dims=None):
    # set default plot options if necessary
    opts = subplot.opts
    if len(opts) == 0:
        opts['labelAngle'] = -20
        
    
    ymax = np.max(np.maximum.reduce(subplot.Data))
    ylim = (1, ymax*10)
    # create the subplot and set its attributes
    subplot.axes = figure.add_subplot(subplot.mnp, 
                                   ylim=ylim, yscale='log', 
                                   autoscale_on=False,
                                   title=subplot.Title)
    subplot.axes.set_xticklabels(subplot.Labels, rotation=opts['labelAngle'])
    subplot.axes.boxplot(subplot.Data, sym='')
    
    

# OPTIONS DIALOG
from base import OptionsDialog, OptionsDialogPanel
import display.formatters as f
import wx

class BoxplotOptionsDialog(OptionsDialog):
    def __init__(self, parent, subplot, dims = None):
        """
        @type parent: Window
        @param parent: The parent window for the dialog
        @type subplot: Subplot
        @param subplot: The Subplot instance for which to specify settings
        """
        super(BoxplotOptionsDialog, self).__init__(parent, 
                                                         subplot, 
                                                         title="Boxplot Options", 
                                                         size=(400,180))

        self.NB.AddPage(BoxplotOptionsPanel(self.NB), "Boxplot Options")

        self.loadOptions(subplot.opts)
        
        # create button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.buttonSizer.AffirmativeButton.Bind(wx.EVT_BUTTON, self.cmdOK_Click)
        
        # Sizer
        self.Sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        

class BoxplotOptionsPanel(OptionsDialogPanel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Init controls
        self.txtLabelAngle = wx.TextCtrl(self, size=(80,20))

        # Layout
        mainSizer = wx.BoxSizer()
        mainSizer.Add(wx.StaticText(self, wx.ID_ANY, "X-axis Labels Rotation Angle:"))
        mainSizer.Add(self.txtLabelAngle, 1, wx.EXPAND, 10)
        
        # Sizer
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(mainSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)



    def loadOptions(self, opts):
        """
        This method loads the form input controls with saved/default data.
        
        :@type opts: dict  
        :@param opts: A dict of plot settings.
        """
        self.txtLabelAngle.Value = str(opts['labelAngle'])
            
    
    def validate(self):
        floatVal = f.FloatFormatter()
        msg = []
        
        if not floatVal.validate(self.txtLabelAngle.Value):
            msg.append("A valid number must be entered.")
        else:
            val = float(self.txtLabelAngle.Value)
            if val < -360 or val > 360:
                msg.append("A value between -360 and 360 must be entered.")
            
        return msg


    @property
    def Options(self):
        options = {}
        options['labelAngle'] = int(self.txtLabelAngle.Value)
        return options






