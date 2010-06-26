import wx

# Every wxWidgets application must have a class derived from wx.App
class MyApp(wx.App):

    # wxWindows calls this method to initialize the application
    def OnInit(self):
        # Most constructors expect a parent object as the first parameter
        # and an id number as second parameter.
        dialog = wx.Dialog(None, -1, "Title")
        button = wx.Button(dialog, wx.ID_OK, "Hello world")
        
        # A simple way to describe a window-layout is to use sizers.
        # Add a five pixel border to ALL sides and allow the button to
        # EXPAND in all directions.
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button, 1, wx.EXPAND|wx.ALL, 5)
        dialog.SetSizer(sizer)
        dialog.Fit()    # Make the dialog as small as possible.
        dialog.Layout() # Calculate the position of the button.
        
        # Tell the dialog to call our_event_handler if the button is pressed.
        wx.EVT_BUTTON(dialog, button.GetId(), our_event_handler)
        
        dialog.ShowModal()
        dialog.Destroy()   # Yes, you have to destroy dialogs explicitly. :-(
        
        # Tell wxWindows that this is our main window
        self.SetTopWindow(frame)

        # Return a success flag
        return True
    
    def our_event_handler(event):
        event.Skip() # Try to call another handler.



app = MyApp(0)     # Create an instance of the application class
app.MainLoop()     # Tell it to start processing events








