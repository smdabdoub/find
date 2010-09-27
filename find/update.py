'''
Created on Sep 27, 2010

@author: dabdoubs
'''
import urllib2
import webbrowser
import wx


updateLoc = ['http://justicelab.org/find', 'version.txt']

def CheckForUpdate(parent, findVersion, errHandler):
    try:
        updateFile = urllib2.urlopen('/'.join(updateLoc))
        version = updateFile.readline()
        updateFile.close()
    except urllib2.URLError as urle:
        import socket
        err = wx.MessageDialog(parent, 'There was a problem checking for updates. '\
                      +'Please consider submitting an error report.',
                      'Error', wx.OK|wx.CANCEL|wx.ICON_ERROR)
        if err.ShowModal() == wx.ID_OK:
            if isinstance(urle, urllib2.HTTPError):
                value = str(urle.code) + ': ' + urle.msg
            elif isinstance(urle.reason, str):
                value = urle.reason
            elif isinstance(urle.reason, socket.error):
                value = str(urle.reason)
            errHandler('Update Check Error: ', value)
        err.Destroy()
        return
        
    if findVersion < version:
        dlg = wx.MessageDialog(parent, 'There is a newer version of FIND available, please '\
                      +'click OK to open the download page in your browser.', 
                      'Update Available', wx.OK|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_OK:
            webbrowser.open_new_tab(updateLoc[0])
    else:
        wx.MessageBox('You are running the current version of FIND.',
                      'No Update', wx.OK|wx.ICON_INFORMATION)