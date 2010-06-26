import wx
ID_About = 101
ID_Exit = 102

class BasicApp(wx.App):
  def OnInit(self):
    frame = BasicFrame(None, -1, "Hello from wxPython")
    frame.Show(True)

    frame.Connect(ID_About, -1, # see line 34
                  wx.wxEVT_COMMAND_MENU_SELECTED, frame.OnAbout)
    frame.Connect(ID_Exit, -1,  # see line 35
                  wx.wxEVT_COMMAND_MENU_SELECTED, frame.OnExit)

    self.SetTopWindow(frame)
    return True;

class BasicFrame(wx.Frame):
  def __init__(self, parent, ID, title):
    wx.Frame.__init__(self, parent, ID, title,
                     wx.DefaultPosition, wx.Size(200, 150))
    self.CreateStatusBar()
    self.SetStatusText("This is the statusbar")
    menu = wx.Menu()
    menu.Append(ID_About, "&About",
                "More information about this program")
    menu.AppendSeparator()
    menu.Append(ID_Exit, "&Exit", "Terminate program")
    menuBar = wx.MenuBar()
    menuBar.Append(menu, "&File")
    self.SetMenuBar(menuBar)

   # see line 11 - EVT_MENU(self, ID_About, self.OnAbout)
   # see line 12 - EVT_MENU(self, ID_Exit, self.OnExit)

  def OnAbout(self, event):
    dlg = wx.MessageDialog(self, "No EVT_MENU!",
                          "About No EVT_MENU", wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()

  def OnExit(self, event):
    self.Close(True)


app = BasicApp(0)
app.MainLoop()
