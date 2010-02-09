'''
Created on Jan 28, 2010

@author: shareef
'''
import wx
from wx.lib.stattext import GenStaticText

class StyledStaticText(GenStaticText):
    def __init__(self, parent, id=wx.ID_ANY, label='', pos=(-1, -1),
        size=(-1, -1), style=0, name='StyledStaticText', color='#000000'):

        GenStaticText.__init__(self, parent, id, label, pos, size, style, name)
        
        label, style, weight = self.parse(label)
        
        self.SetLabel(label)
        self.default = wx.SystemSettings_GetFont(0)
        self.font = wx.Font(self.default.PointSize, self.default.Family, style, weight)

        self.SetFont(self.font)
        self.SetForegroundColour(color)
        
    def parse(self, string):
        # Bold, Italic
        if string.startswith('***') and string.endswith('***'):
            string = string.split('***')[1]
            return string, wx.ITALIC, wx.BOLD
        # Italics
        if string.startswith('**') and string.endswith('**'):
            string = string.split('**')[1]
            return string, wx.ITALIC, wx.NORMAL
        # Bold
        if string.startswith('*') and string.endswith('*'):
            string = string.split('*')[1]
            return string, wx.NORMAL, wx.BOLD
        
        return string, wx.NORMAL, wx.NORMAL