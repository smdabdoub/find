'''
Created on Sep 27, 2010

@author: dabdoubs
'''
import socket
import urllib2
import webbrowser
import wx


updateSites = {'http://www.mathmed.org/~dabdoubs/find': 'version.txt',
               'http://justicelab.org/find': 'version.txt'}

def CheckForUpdate(parentWin, findVersion, errHandler):
    err = []
    for site in updateSites:
        ret = _grabVersion('/'.join([site, updateSites[site]]))
        if not ret[0]:
            err.append(ret[1])
            print ret[1]
        else:
            _notifyUser(findVersion, ret[1], site, parentWin)
            return
    
    errDlg = wx.MessageDialog(parentWin, 'There was a problem checking for updates. '\
                  +'Please consider submitting an error report.',
                  'Error', wx.OK|wx.CANCEL|wx.ICON_ERROR)
    if errDlg.ShowModal() == wx.ID_OK:
        msg = []
        for urle in err:
            if isinstance(urle, urllib2.HTTPError):
                msg.append(str(urle.code) + ': ' + urle.msg)
            elif isinstance(urle.reason, str):
                msg.append(urle.reason)
            elif isinstance(urle.reason, socket.error):
                msg.append(str(urle.reason))
        errHandler('Update Check Error: ', '\n'.join(msg))
    errDlg.Destroy()
    

def _notifyUser(findVersion, latestVersion, site, parentWin):
    if findVersion < latestVersion:
        dlg = wx.MessageDialog(parentWin, 'There is a newer version of FIND available, please '\
                      +'click OK to open the download page in your browser.', 
                      'Update Available', wx.OK|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_OK:
            webbrowser.open_new_tab(site)
    else:
        wx.MessageBox('You are running the current version of FIND.',
                      'No Update', wx.OK|wx.ICON_INFORMATION)


def _grabVersion(updateLoc):
    try:
        updateFile = urllib2.urlopen(updateLoc)
        version = updateFile.readline()
        updateFile.close()
    except urllib2.URLError as urle:
        return (False, urle)
        
    return (True, version)