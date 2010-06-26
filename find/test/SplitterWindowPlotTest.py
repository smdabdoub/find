
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import  wx

class PlotPanel(wx.Panel):
    def __init__( self, parent, **kwargs ):
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE
        wx.Panel.__init__( self, parent, **kwargs )
        self.SetBackgroundColour("white")
        
        self.figure = Figure()
        self.canvas = FigureCanvas( self, -1, self.figure )
        self.draw()

    def draw(self):
        axes = self.figure.add_subplot(111)
        axes.plot([1,2,3,4,5], [1,2,3,4,5], '.', ms=1, color='black')
        self.canvas.draw()


class MainWindow(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, pos=(500,200), size=(700,500))
        
        splitter = wx.SplitterWindow(self, -1, style=wx.CLIP_CHILDREN | wx.SP_LIVE_UPDATE | wx.SP_3D)
    
        p1 = wx.Window(splitter)
        p1.SetBackgroundColour("pink")
        wx.StaticText(p1, -1, "Panel One", (5,5))
    
        p2 = wx.Window(splitter)
        p2.SetBackgroundColour("sky blue")
        wx.StaticText(p2, -1, "Panel Two", (5,5))
        
        plot = PlotPanel(splitter)
        
    
        splitter.SetMinimumPaneSize(20)
        splitter.SplitVertically(p1, plot, -300)
    
        self.Show()


#---------------------------------------------------------------------------


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MainWindow(None, -1, "Test FACS Splitter Display")
    app.MainLoop()