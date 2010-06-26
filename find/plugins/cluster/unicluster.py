'''
Created on Jul 30, 2009

@author: shareef
'''
from plugins.pluginbase import ClusterOptionsDialog

import wx

__all__ = ['unicluster_register']

def unicluster(data, **kwargs):
    """
    Unicluster; Creates one large cluster that includes all the data;
    
    @var data: The input data to be clustered.
    """
    clustering = []
    for i in range(len(data)):
        clustering.append(0)
        
    return clustering,'One cluster found'
        

class UniclusterOptionsDialog(ClusterOptionsDialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Unicluster Options', size=(250, 150))
        self.CenterOnParent()
        
        txtUseless = wx.TextCtrl(self, -1, '1', (20,20))
        txtUseless.SetEditable(False)
        
        self.formSizer = wx.BoxSizer()
        self.formSizer.Add(wx.StaticText(self, -1, 'Number of clusters:', (20, 10)), 3, wx.ALIGN_RIGHT)
        self.formSizer.Add(txtUseless, 1, wx.ALIGN_LEFT)
        
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        
        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.formSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 20)
        self.sizer.Add(self.getApplySizer(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        self.sizer.AddSpacer(5)
        self.sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        self.sizer.AddSpacer(5)
        self.SetSizer(self.sizer)
    
    def getMethodArgs(self):
        options = {'clusters': 1}
        return options
        
        
    def getStrMethodArgs(self):
        options = {'clusters': 'Number of Clusters'}
        return (options, {})


def unicluster_register():
    return (unicluster, UniclusterOptionsDialog)


