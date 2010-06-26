'''
This module contains wx Validator classes for validating user input
'''
import wx

class TextValidator(wx.PyValidator):
    """
    http://www.daniweb.com/forums/thread203441.html#
    """
    def __init__(self):
        wx.PyValidator.__init__(self)
    def Clone(self): # Required method
        return TextValidator()
    def TransferToWindow(self):
        return True # Prevent wxDialog from complaining.
    def TransferFromWindow(self):
        return True # Prevent wxDialog from complaining.

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()

        if len(text) == 0:
            wx.MessageBox("text input is required", "Error")
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True
        

class FloatValidator(wx.PyValidator):
    def __init__(self,data,key):
        wx.PyValidator.__init__(self)
        self.data = data
        self.key = key

    def Clone(self):
        """
        Note all validators must implement Clone()
        """
        return FloatValidator(self.data, self.key)
        
    def Validate(self,win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        
        try:
            float(text)
        except ValueError:
            #print text
            textCtrl.SetBackgroundColour('pink')
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        
        textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        textCtrl.Refresh()
        return True
    def TransferToWindow(self):
        pass
    def TransferFromWindow(self):
        textCtrl = self.GetWindow()
        self.data[self.key] = float(textCtrl.GetValue())