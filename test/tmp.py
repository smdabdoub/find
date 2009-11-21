import wx

class Frame(wx.Frame):
     pass

class App(wx.App):

     def OnInit(self):
         self.frame = Frame(parent=None, title='Spare')
         #self.frame.SetBackGroundColour("light blue")
         self.panel = wx.Panel(parent=self.frame)
         self.panel.SetBackgroundColour("light blue")
         self.frame.Show()
         self.SetTopWindow(self.frame)
         return True

if __name__ == '__main__':
     app = App()
     app.MainLoop()
