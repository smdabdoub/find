'''
This module contains classes for plot-option dialogs

@author: shareef
'''
import data.plot as dp
from display.text import StyledStaticText
import formatters as f
import validators as v

import wx


dialogs = {}

def getPlotOptionsDialog(parent, subplot):
    if (subplot.plotType in dialogs):
        return dialogs[subplot.plotType](parent, subplot)
    else:
        return OptionsDialog(parent, subplot, True)

class OptionsDialog(wx.Dialog):
    def __init__(self, parent, subplot, autoLoadOptions=False, title="Plot Options", size=(200,180)):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=size)
        self.CenterOnParent()
        
        self.NB = wx.Notebook(self)

        # Add tabs to the notebook
        self.pnlGeneralOpts = GeneralOptionsPanel(self.NB)
        if (autoLoadOptions):
            self.loadOptions(subplot.opts)

        self.NB.AddPage(self.pnlGeneralOpts, "General Options")
        
        # sizer for layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.NB, 1, wx.EXPAND)
        self.SetSizer(sizer)
                
    
    def loadOptions(self, opts):
        """
        Loads saved options into all notebook pages via the loadOptions() 
        method that must exist in each.
        
        Unless specific functionality is needed, subclasses of OptionsDialog
        should not need to override this method.
        
        :@type opts: dict
        :@param opts: The saved plot options.
        """
        for i in range(self.NB.PageCount):
            self.NB.GetPage(i).loadOptions(opts)

    @property
    def Options(self):
        """
        The Options property will retrieve all settings from each notebook page in self.NB
        
        Unless specific functionality is needed, subclasses of OptionsDialog
        should not need to override this property.
        
        :@rtype: dict
        :@return: The specified plot options.
        """
        options = {}
        for i in range(self.NB.PageCount):
            options.update(self.NB.GetPage(i).Options)
        
        return options



class GeneralOptionsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.X_RANGE = wx.NewId()
        self.Y_RANGE = wx.NewId()
                
        # Init controls
        self.txtX_RangeLow = wx.TextCtrl(self, size=(40,20), validator=v.FloatValidator(0, 'xRangeLow'))
        self.txtX_RangeHigh = wx.TextCtrl(self, size=(80,20))
        self.txtY_RangeLow = wx.TextCtrl(self, size=(40,20))
        self.txtY_RangeHigh = wx.TextCtrl(self, size=(80,20))
        
        self.chkAutoX_range = wx.CheckBox(self, self.X_RANGE, label="Auto")
        self.chkAutoY_range = wx.CheckBox(self, self.Y_RANGE, label="Auto")
        
        
        # Layout
        fgRange = wx.FlexGridSizer(2, 6, 5, 5)
        fgRange.Add(wx.StaticText(self, wx.ID_ANY, "X-axis:"), 0, wx.RIGHT, 5)
        fgRange.Add(wx.StaticText(self, wx.ID_ANY, "Low"), 0)
        fgRange.Add(self.txtX_RangeLow, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT, 10)
        fgRange.Add(wx.StaticText(self, wx.ID_ANY, "High"), 0)
        fgRange.Add(self.txtX_RangeHigh, 1, wx.EXPAND)
        fgRange.Add(self.chkAutoX_range, 1, wx.EXPAND)
        self.chkAutoX_range.Bind(wx.EVT_CHECKBOX, self.chkRangeAuto_Click)
        
        fgRange.Add(wx.StaticText(self, wx.ID_ANY, "Y-axis:"), wx.RIGHT, 5)
        fgRange.Add(wx.StaticText(self, wx.ID_ANY, "Low"))
        fgRange.Add(self.txtY_RangeLow, 1, wx.EXPAND | wx.RIGHT, 10)
        fgRange.Add(wx.StaticText(self, wx.ID_ANY, "High"), 0)
        fgRange.Add(self.txtY_RangeHigh, 1, wx.EXPAND)
        fgRange.Add(self.chkAutoY_range, 1, wx.EXPAND)
        self.chkAutoY_range.Bind(wx.EVT_CHECKBOX, self.chkRangeAuto_Click)
        
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(StyledStaticText(self, wx.ID_ANY, "**Axes Range**"), 0)
        self.Sizer.Add(fgRange, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        
    def chkRangeAuto_Click(self, event):
        if event.GetId() == self.X_RANGE:
            self.txtX_RangeLow.Enable(not self.chkAutoX_range.Value)
            self.txtX_RangeHigh.Enable(not self.chkAutoX_range.Value)
        if event.GetId() == self.Y_RANGE:
            self.txtY_RangeLow.Enable(not self.chkAutoY_range.Value)
            self.txtY_RangeHigh.Enable(not self.chkAutoY_range.Value) 
        
        
    def loadOptions(self, opts):
        """
        This method loads the form input controls with saved/default data.
        
        :@type opts: dict  
        :@param opts: A dict of plot settings.
        """
        self.chkAutoX_range.Value = opts['xRangeAuto']
        self.chkAutoY_range.Value = opts['yRangeAuto']
        
        # disable the range txt boxes if auto is checked
        if self.chkAutoX_range.Value:
            self.txtX_RangeLow.Enable(False)
            self.txtX_RangeHigh.Enable(False)
        else:
            self.txtX_RangeLow.Value  = str(opts['xRange'][0])
            self.txtX_RangeHigh.Value = str(opts['xRange'][1])
        
        if self.chkAutoX_range.Value:
            self.txtY_RangeLow.Enable(False)
            self.txtY_RangeHigh.Enable(False)
        else:
            self.txtY_RangeLow.Value  = str(opts['yRange'][0])
            self.txtY_RangeHigh.Value = str(opts['yRange'][1])
    
    def validate(self):
        """
        Checks the validity of all the input in the controls on the panel.
        
        :@rtype: list
        :@return: A list of error strings to be used as messages to the user.
        """
        floatVal = f.FloatFormatter()
        msg = []
        
        if not self.chkAutoX_range.Value:
            if not floatVal.validate(self.txtX_RangeLow.Value) or \
               not floatVal.validate(self.txtX_RangeHigh.Value):
                msg.append('Both x-range values must be filled in and must be numbers.')
                
        if not self.chkAutoY_range.Value:
            if not floatVal.validate(self.txtY_RangeLow.Value) or \
               not floatVal.validate(self.txtY_RangeHigh.Value):
                msg.append('Both y-range values must be filled in and must be numbers.')
        
        return msg
    
    @property
    def Options(self):
        """
        Gathers the x and y range information.
        
        @rtype: dict
        @return: A dictionary of algorithm options.
        """
        options = {}
        options['xRangeAuto'] = self.chkAutoX_range.Value
        options['yRangeAuto'] = self.chkAutoY_range.Value

        if self.chkAutoX_range.Value:
            options['xRange'] = ()
        else:
            options['xRange'] = (float(self.txtX_RangeLow.Value), float(self.txtX_RangeHigh.Value))
            
        if self.chkAutoX_range.Value:
            options['yRange'] = ()
        else:
            options['yRange'] = (float(self.txtY_RangeLow.Value), float(self.txtY_RangeHigh.Value))
                    
        
        return options
        

class ScatterPlot2dOptionsDialog(OptionsDialog):
    def __init__(self, parent, subplot, dims = None):
        """
        @type parent: Window
        @param parent: The parent window for the dialog
        @type subplot: Subplot
        @param subplot: The Subplot instance for which to specify settings
        """
        super(ScatterPlot2dOptionsDialog, self).__init__(parent, 
                                                         subplot, 
                                                         title="2D Scatterplot Options", 
                                                         size=(400,180))
        
        self.pnlS2Dopts = ScatterPlot2dOptionsPanel(self.NB)
        self.NB.AddPage(self.pnlS2Dopts, "2D Scatter Plot Options")
        
        self.loadOptions(subplot.opts)
        
        # create button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.buttonSizer.AffirmativeButton.Bind(wx.EVT_BUTTON, self.cmdOK_Click)
        
        # Sizer
        self.Sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        
        
    def cmdOK_Click(self,event):
        event.Skip()
    

class ScatterPlot2dOptionsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Init controls
        transformLabel = StyledStaticText(self, wx.ID_ANY, "**Transforms**")
        
        #TODO: Retrieve these from the future Transforms module
        self.transforms = ['linear','log'] 
        self.cbxX_Transform = wx.ComboBox(self, choices=self.transforms, 
                                          style=wx.CB_READONLY)
        self.cbxY_Transform = wx.ComboBox(self, choices=self.transforms, 
                                          style=wx.CB_READONLY)
        self.chkTransformAuto = wx.CheckBox(self, label="Auto")
        self.chkTransformAuto.Bind(wx.EVT_CHECKBOX, self.chkTransformAuto_Click)
        

        # Layout
        fgTransform = wx.FlexGridSizer(1, 5, 5, 5)
        fgTransform.Add(wx.StaticText(self, wx.ID_ANY, "X-axis:"))
        fgTransform.Add(self.cbxX_Transform, 1, wx.ALIGN_LEFT | wx.RIGHT, 10)
        fgTransform.Add(wx.StaticText(self, wx.ID_ANY, "Y-axis:"))
        fgTransform.Add(self.cbxY_Transform, 1, wx.ALIGN_LEFT)
        fgTransform.Add(self.chkTransformAuto, 1, wx.EXPAND)

        # Sizer
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(transformLabel, 0)
        self.Sizer.Add(fgTransform, 0, wx.ALIGN_CENTER_HORIZONTAL)


    def chkTransformAuto_Click(self, event):
        self.cbxX_Transform.Enable(not event.Selection)
        self.cbxY_Transform.Enable(not event.Selection)


    def loadOptions(self, opts):
        """
        This method loads the form input controls with saved/default data.
        
        :@type opts: dict  
        :@param opts: A dict of plot settings.
        """
        self.cbxX_Transform.StringSelection = opts['xTransform']
        self.cbxY_Transform.StringSelection = opts['yTransform']
        self.chkTransformAuto.Value = opts['transformAuto']
        
        # If auto is checked, disable the combo boxes
        if self.chkTransformAuto.Value:
            self.cbxX_Transform.Enable(False)
            self.cbxY_Transform.Enable(False)
            
    
    def validate(self):
        return []


    @property
    def Options(self):
        options = {}
        options['xTransform'] = self.cbxX_Transform.StringSelection
        options['yTransform'] = self.cbxY_Transform.StringSelection
        options['transformAuto'] = self.chkTransformAuto.Value
        return options









dialogs[dp.ID_PLOTS_SCATTER_2D] = ScatterPlot2dOptionsDialog












