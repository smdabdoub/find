'''
Created on Jun 2, 2010

@author: dabdoubs
'''
import wx
import wx.html

class HelpDialog(wx.Dialog):
    """
    Creates a window for displaying help information from HTML source.
    
    :@type parent: wx.Window
    :@param parent: The parent window for this dialog
    :@type title: str
    :@param title: A title for the dialog
    :@type html:  
    """
    def __init__(self, parent, title, html, size):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=size)