"""
This module contains the base classes and implementation information needed
for creating FWAC plugins.

MODULE IMPLEMENTATION:
All modules must be placed in the appropriate plugin folder. 
Certain assumptions (as described below) are made for the different
plugin types, and plugins in each folder will be expected to follow
those assumptions.

Each module must make use of the __all__ magic list to provide the plugin 
methods. Depending on the plugin type, different assumptions are made as to 
what the provided methods should be.

Every visible (specified in __all__) plugin method must provide inside of its
doc string a short name for use as the menu listing, as well as a longer 
description string to aid the user. These will be delimited by semicolons(;),
and any additional documentation the programmer wishes to provide will be 
placed after the final ; delimiter. If these are not provided, the method name 
and a blank string will be used as the short name and descriptor respectively.

* Clustering Plugins:

  Each method specified in the __all__ list must return a tuple of the 
  following form:
  
  (clustering method, clustering options dialog class)
  
  The clustering method will have the following signature:
  
  cluster(data, **kwargs)
  @type data: ndarray (Numpy) 
  @var data: An mxn array containing all the numeric data
  @type kwargs: dict
  @var kwargs: A dict of user-selected options provided by the
               options dialog class
  @rtype: tuple (list, str)
  @return: A tuple containing an m-length list specifying the cluster 
           membership of each row entry in the data array, and a string message
           to be displayed to the user.
           
  The options dialog must inherit from ClusterOptionsDialog, provided in 
  this module. Note that each of the specified virtual methods in the class
  must be implemented to properly function within the program.   

@author: Shareef Dabdoub
@organization: The Ohio State University
@organization: Nationwide Children's Hospital
"""
import wx

class Plugin(object):
    """
    This virtual method must be implemented by all subclasses. 
    It should report a list of implemented methods it wants to make 
    available for use by the main program.
    
    @rtype: list
    @return: All the methods to be made available to the user as plugins.
    """
    def register():
        pass
    

#TODO: Consider making a dialog-creator class that would get around the need to import wx
#TODO: Figure out how to make an egg (jar) of FWAC so this class doesn't need to be duplicated
class ClusterOptionsDialog(wx.Dialog):
    """
    Provides a base options dialog to specify a consistent interface for
    retrieving data from clustering-related dialogs
    """
    
    def getMethodArgs(self):
        """
        Gather all options specified in the dialog. The values of the 
        user-selected options will be passed to the clustering method 
        as well as being displayed to the user.
        
        @rtype: dict
        @return: A dictionary of algorithm options. This will be passed to the 
                 associated clustering method as the **kwargs parameter.
        """ 
        pass
    
    def getStrMethodArgs(self): 
        """
        Define an equivalency between the variable form of algorithm options 
        and the full string representation of the options. This will be used
        to display the selected options to the user.
        
        @rtype: tuple
        @return: A tuple containing:
                    - A dictionary equating the short form of method option 
                    names with the full string descriptions.
                    - A dictionary containing translations for any argument 
                    values that are not easily understandable
        """
        pass
    
    def getApplySizer(self, parent):
        self.chkApplyToCurrentSuplot = wx.CheckBox(parent, wx.ID_ANY, 'Apply to current subplot')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.chkApplyToCurrentSuplot)
        return sizer
    
    def isApplyChecked(self):
        return self.chkApplyToCurrentSuplot.GetValue()



class IOPlugin(Plugin):
    """
    All IOPlugins are expected to provide methods for opening and/or saving 
    data files.
    """
    def open(self, file):
        """
        Given the specified path of a data file, input the data and return
        it along with the column labels. 
        """
        pass
        
    def save(self, file, data, labels):
        """
        Write the FACS data to the specified file.
        """
        pass
    
    
    
    
    
    
    
    