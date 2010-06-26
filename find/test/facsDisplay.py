#
#  facsDisplay.py
#  
#  Purpose: Given a set of FACS data, display a 2D scatter plot of the 
#           data as selected per attribute by the user
#
#  Created by Shareef Dabdoub on 11/12/08.
#
#  much of the matplotlib embedding code taken from:
#  http://www.scipy.org/Matplotlib_figure_in_a_wx_panel


#!/usr/bin/env python

import matplotlib
from matplotlib import mlab
import sys

# uncomment the following to use wx rather than wxagg
#matplotlib.use('WX')
#from matplotlib.backends.backend_wx import FigureCanvasWx as FigureCanvas

# comment out the following to use wx rather than wxagg
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure

import wx
from pylab import *


PLOT_FONT_SIZE = 9
ID_FILE_OPEN = 111
ID_ABOUT     = 101
ID_EXIT      = 110


class DisplayFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,wx.ID_ANY, 'FACS Display',size=(550,550))
        self.labDat = []
        
        # Setting up the menu.
        fileMenu= wx.Menu()
        fileMenu.Append(ID_FILE_OPEN, "&Open"," Open an FCS data file")
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_ABOUT, "&About"," Information about this program")
        fileMenu.Append(ID_EXIT,"E&xit"," Terminate the program")
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu,"&File") 
        self.SetMenuBar(menuBar)  
        
        # menu events
        wx.EVT_MENU(self, ID_FILE_OPEN, self.OnOpen) 
        wx.EVT_MENU(self, ID_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, ID_EXIT, self.OnExit)
        
        # Set up main visual elements of the frame
        
        # will contain the data column selection boxes
        self.selectorSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dataSelectors = []
        self.dimensions = ['X axis', 'Y axis']
        for i in range(len(self.dimensions)):
            self.dataSelectors.append(wx.ComboBox(self, 500, "default value", (90, 50), 
                                                  (160, -1), ['1','2','3'],
                                                  wx.CB_DROPDOWN
                                                  #| wx.TE_PROCESS_ENTER
                                                  #| wx.CB_SORT
                                                  ))
            self.selectorSizer.Add(wx.StaticText(self, -1, self.dimensions[i], (20, 10)), 1, wx.EXPAND)
            self.selectorSizer.Add(self.dataSelectors[i], 1, wx.EXPAND)
        
        # will contain the plot panel and the selector sizer
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        #self.facsPlotPanel = FacsPlotPanel(self, self.labDat, [])
        #self.mainSizer.Add(self.facsPlotPanel, 1, wx.EXPAND)
        self.mainSizer.Add(wx.TextCtrl(self, 1, style=wx.TE_MULTILINE))
        #self.mainSizer.Add(self.selectorSizer, 0, wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(1)
        self.mainSizer.Fit(self)
        
        self.Show(True)
    
    
    # assume first line contains column labels
    def loadFacsCSV(self, filename):
        print 'loading:',filename
        labels = open(filename,'r').readline().rstrip().replace('"','').split(',')
        print 'Column labels:',labels
        data = mlab.load(filename, delimiter=',', skiprows=1)
        return (labels,data)
    
    ## EVENT METHODS ##
    def OnOpen(self,e):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            self.facsPlotPanel.updateData(self.loadFacsCSV(self.filename))
            self.facsPlotPanel.draw()
        dlg.Destroy()
        

    def OnSave(self,e):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            self.facsPlotPanel.updateData(self.loadFacsCSV(self.filename))
            self.facsPlotPanel.draw()
        dlg.Destroy()

    
    def OnAbout(self,e):
        dlg = wx.MessageDialog( self, " FACS Data Display \n"
                                      " Displays clustered FACS data","About", wx.OK)
        dlg.ShowModal() 
        dlg.Destroy() 
                
    
    def OnExit(self,e):
        self.Close(True)
        

class PlotPanel(wx.Panel):
    def __init__( self, parent, color=None, dpi=None, **kwargs ):
        # initialize Panel
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE
        wx.Panel.__init__( self, parent, **kwargs )
        
        # initialize matplotlib stuff
        self.figure = Figure( None, dpi )
        self.canvas = FigureCanvas( self, -1, self.figure )
        self.SetColor( color )
        #self.SetBackgroundColour(NamedColor("WHITE"))
        
        self._SetSize()
        self.draw()

        self._resizeflag = False

        self.Bind(wx.EVT_IDLE, self._onIdle)
        self.Bind(wx.EVT_SIZE, self._onSize)

    def SetColor( self, rgbtuple=None ):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor( clr )
        self.figure.set_edgecolor( clr )
        self.canvas.SetBackgroundColour( wx.Colour( *rgbtuple ) )

    def _onSize( self, event ):
        self._resizeflag = True

    def _onIdle( self, evt ):
        if self._resizeflag:
            self._resizeflag = False
            self._SetSize()

    def _SetSize( self ):
        pixels = tuple( self.parent.GetClientSize() )
        self.SetSize( pixels )
        self.canvas.SetSize( pixels )
        self.figure.set_size_inches( float( pixels[0] )/self.figure.get_dpi(),
                                     float( pixels[1] )/self.figure.get_dpi() )

    def draw(self): pass # abstract, to be overridden by child classes

class FacsPlotPanel(PlotPanel):
    """Displays a scatter plot of the FACS data"""
    def __init__( self, parent, labDat, colors, **kwargs ):
        self.parent = parent
        self.updateData(labDat)
        self.color_list = colors

        # initiate plotter
        PlotPanel.__init__( self, parent, **kwargs )
        self.SetColor( (255,255,255) )
    
    def updateData(self, labDat):
        if (len(labDat) != 2):
            self.data_labels = []
            self.point_array = []
        else:
            self.data_labels = labDat[0]
            self.point_array = labDat[1]
            print 'Data updated'
            print self.data_labels
            self._resizeflag = True
            
    
    def draw( self ):
        """Draw data."""            
        if not hasattr( self, 'subplot' ):
            self.subplot = self.figure.add_subplot( 111, xlim=(1e-1, 3e5), ylim=(1e-1, 3e5), 
                                                         autoscale_on=False, 
                                                         yscale='log',xscale='log')
            
        if (len(self.data_labels) > 0):
            print 'feh'
            self.subplot.set_xlabel(self.data_labels[3])
            self.subplot.set_ylabel(self.data_labels[4])

            # draw the supplied FACS data
            self.subplot.scatter(self.point_array[:,3], self.point_array[:,4], s=1)
        
        
#class App(App):

#    def OnInit(self):
#        'Create the main window and insert the custom frame'
#        frame = DisplayFrame()
#        frame.Show(True)

#        return True

if __name__ == '__main__':
    #app = App(0)
    app = wx.PySimpleApp()
    frame = DisplayFrame()
    frame.Show(True)
    app.MainLoop()












