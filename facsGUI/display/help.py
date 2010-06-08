'''
Created on Jun 2, 2010

@author: dabdoubs
'''
import wx
import wx.html

class HelpDialog(wx.Dialog):
    """
    Creates a window for displaying help information from HTML source.
    The source can be either actual HTML in a string (with the html 
    parameter), or a path to a file containing the desired HTML 
    (htmlfile parameter). 
    
    Note that if both parameters are supplied, only the html parameter will be 
    used.
    
    :@type parent: wx.Window
    :@param parent: The parent window for this dialog
    :@type title: str
    :@param title: A title for the dialog
    :@type size: tuple
    :@param size: Size in pixels of the dialog window.
    :@type html: str
    :@param html: A string containing the HTML to be displayed.
    :@type htmlfile: str
    :@param htmlfile: The path to an HTML file that will be displayed.
    """
    def __init__(self, parent, title, size=(-1,-1), html="", htmlfile=None):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=size)
        self.CenterOnParent()
        
        self.htmlPanel = wx.html.HtmlWindow(self)
        
        if htmlfile is not None:
            self.htmlPanel.LoadPage(htmlfile)
        else:    
            self.htmlPanel.SetPage(html)
        
        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.htmlPanel, 1, wx.EXPAND)
        self.sizer.Add(self.CreateButtonSizer(wx.OK), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 10)
        self.SetSizer(self.sizer)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        