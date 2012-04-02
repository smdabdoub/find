'''
Currently this module is non-functional and serves only as a code
example for developers of Analysis plugins.

@author: Shareef Dabdoub
'''
__all__ = ['pca_register']

from matplotlib.mlab import PCA
import wx

def pca(data, **kwargs):
    """
    pca; PCA; Principle Components Analysis
    """
    win = None
    if 'parentWindow' in kwargs:
        win = kwargs['parentWindow']
    
    
    # if no window available, then something else is calling->return results
    res = None #call pca
    
    return (res, 'PCA completed')
    
    
class PCA_Display(wx.Dialog):
    def __init__(self, parent, data):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Principle Components Analysis', size=(250, 150))
        self.CenterOnParent()
        


def pca_register():
    return (pca, True)