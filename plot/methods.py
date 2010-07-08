'''
Created on Aug 30, 2009

@author: shareef
'''
from data import store
import wx

ID_PLOTS_SCATTER_2D = "scatterplot2D"
ID_PLOTS_BOXPLOT    = "boxplot"
#ID_PLOTS_HISTOGRAM  = "histogram"
ID_PLOTS_BARPLOT    = "barplot"

methods = {}

def addPluginMethod(descriptor):
    """
    Adds a plotting method to the list of available methods.
    
    :@type descriptor: tuple
    :@param descriptor: Each tuple contains the following information in order:
        - ID (str)
        - ID (int)
        - name (string)
        - description (string)
        - method
        - applicable data types (as defined in data.store)
        - plugin flag
    """
    global methods
    methods[descriptor[0]] = descriptor
    
def AvailableMethods():
    """
    Retrieve the list of available plotting algorithms in this module.
    
    @rtype: list of tuples
    @return: A list descriptor (:@see: addPluginMethod) tuples for each registered method. 
    """
    return methods

def getMethod(id):
    """
    Retrieve a plotting method by its ID.
    
    :@type id: int or str
    :@param id: The identifier for a plotting method. An int id is required
                for the wx event subsystem, but a string id is required as a 
                unique id for plugin authors to specify dependencies on 
                plotting methods.
    :@rtype: method
    :@return: The method associated with the ID, or None.
    """
    try:
        int(id)
    except ValueError:
        return methods[id][-3]
        
    return methods[strID(id)][-3]


def strID(methodID):
    """
    Get the name of a plotting method by its ID.
    
    @type methodID: int
    @param methodID: One of the module-defined ID_* constants for the available methods.
    @rtype: string
    @return: The name of the specified plotting algorithm
    """
    #TODO:remove unnecessary check
    if (methodID is not None):
        for id in methods:
            if methods[id][1] == methodID:
                return methods[id][0]
    

# http://www.december.com/html/spec/color.html
# red, irish-flag green, blue, ??, maroon6, yellow, teal....
plotColors = ['#FF0000','#009900','#0000FF','#00EEEE','#8E236B','#FFFF00',
               '#008080',  'magenta', 'olive', 'orange', 'steelblue', 'darkviolet',
               'burlywood','darkgreen','sienna','crimson']

# For use with contour plotting
def colorcycle(index=None, colors=plotColors):
    """
    Returns the color cycle, or a color cycle, for manually advancing
    line colors.
    """
    return colors[index % len(colors)] if index != None else colors


# Plotting methods
import scatterplot2d, boxplot, barplot#, histogram
methods[ID_PLOTS_BARPLOT] = (ID_PLOTS_BARPLOT, wx.NewId(), "Bar plot", 
                             """Create a bar chart with one bar for each 
                             cluster, and the bar height equal to the percent 
                             of events contained within the cluster.""", 
                             barplot.barplot, [store.ID_CLUSTERING_ITEM], False)

methods[ID_PLOTS_BOXPLOT] = (ID_PLOTS_BOXPLOT, wx.NewId(), "Box plot",
                             """Create a standard boxplot for each dimension 
                             in parallel in the same plot""",
                             boxplot.boxplot, [store.ID_DATA_ITEM], False)


#methods[ID_PLOTS_HISTOGRAM] = (ID_PLOTS_HISTOGRAM, wx.NewId(), "Histogram", 
#                               """Display a 1D histogram using the dimension 
#                               currently selected for the x-axis""",
#                               histogram.histogram, [store.ID_DATA_ITEM], False)


methods[ID_PLOTS_SCATTER_2D] = (ID_PLOTS_SCATTER_2D, wx.NewId(), "2D Scatter Plot",
                             """Display a 2D Scatterplot of the currently 
                             selected x and y axes.""",
                             scatterplot2d.scatterplot2D, [store.ID_DATA_ITEM, store.ID_CLUSTERING_ITEM], False)
                             
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    