'''
Created on Feb 12, 2010

@author: shareef
'''
# PLOTTING METHOD
from cluster.util import separate
import methods

import numpy.numarray as na
from data.store import DataStore


def barplot(subplot, figure, dims=None):
    """
    Create a bar chart with one bar for each cluster, and the bar height
    equal to the percent of events contained within the cluster.
    
    Some techniques borrowed from:
    http://www.scipy.org/Cookbook/Matplotlib/BarCharts
    """
    clusters = separate(subplot.Data, subplot.Clustering)
    
    # set default plot options
    opts = subplot.opts
    if len(opts) == 0:
        opts['labelAngle'] = 0 if len(clusters) < 5 else -20
        opts['toplevelPercent'] = False
    
    dataSize = len(subplot.Data)
    if opts['toplevelPercent']:
        dataSize = len(DataStore.getToplevelParent(subplot.dataIndex).data)
    
    percents = [float(len(cluster))/dataSize*100 for cluster in clusters]
    numBars = len(percents)
    width = 0.5
    
    xlocs = na.array(range(len(percents)))+0.5

    subplot.axes = figure.add_subplot(subplot.mnp, title=subplot.Title, autoscale_on=False)
    subplot.axes.set_xticks(xlocs + width/2)
    subplot.axes.set_xticklabels(map(lambda x: "%.2f%%" % x, percents), rotation=opts['labelAngle'])
    subplot.axes.xaxis.tick_bottom()
    subplot.axes.yaxis.tick_left()
    subplot.axes.set_xlim(0, xlocs[-1] + width*2)
    subplot.axes.set_ylim(0, 100)
    subplot.axes.bar(xlocs, percents, width=width, color=methods.plotColors[:numBars])
    
    
    
# OPTIONS DIALOG
from base import OptionsDialog, OptionsDialogPanel
import display.formatters as f
import wx

class BarplotOptionsDialog(OptionsDialog):
    def __init__(self, parent, subplot, dims = None):
        """
        @type parent: Window
        @param parent: The parent window for the dialog
        @type subplot: Subplot
        @param subplot: The Subplot instance for which to specify settings
        """
        super(BarplotOptionsDialog, self).__init__(parent, 
                                                         subplot, 
                                                         title="Barplot Options", 
                                                         size=(400,180))

        self.NB.AddPage(BarplotOptionsPanel(self.NB), "Barplot Options")

        self.loadOptions(subplot.opts)
        
        # create button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.buttonSizer.AffirmativeButton.Bind(wx.EVT_BUTTON, self.cmdOK_Click)
        
        # Sizer
        self.Sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        

class BarplotOptionsPanel(OptionsDialogPanel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Init controls
        self.txtLabelAngle = wx.TextCtrl(self, wx.ID_ANY, size=(80,20))
        self.chkTopLevelPct = wx.CheckBox(self, wx.ID_ANY, 'Display percentages relative to top-level data')

        # Layout
        mainSizer = wx.BoxSizer()
        mainSizer.Add(wx.StaticText(self, wx.ID_ANY, "X-axis Labels Rotation Angle:"))
        mainSizer.Add(self.txtLabelAngle, 1, wx.EXPAND, 10)
        
        # Sizer
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(mainSizer, 0, wx.ALIGN_CENTER)
        self.Sizer.Add(self.chkTopLevelPct, 0, wx.ALIGN_CENTER)



    def loadOptions(self, opts):
        """
        This method loads the form input controls with saved/default data.
        
        :@type opts: dict  
        :@param opts: A dict of plot settings.
        """
        self.txtLabelAngle.Value = str(opts['labelAngle'])
        self.chkTopLevelPct.Value = opts['toplevelPercent']

    
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
        options['toplevelPercent'] = self.chkTopLevelPct.Value
        return options






