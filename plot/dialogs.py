'''
This module handles requests and plugins for data plots

@author: shareef
'''
import methods

dialogs = {}

def addPluginDialog(ID, dialog):
    global dialogs
    dialogs[ID] = dialog


def getPlotOptionsDialog(parent, subplot):
    try:
        int(subplot.plotType)
    except ValueError:
        return dialogs[subplot.plotType](parent, subplot)
        
    subplot.plotType = methods.strID(subplot.plotType)
    return dialogs[subplot.plotType](parent, subplot)


import scatterplot2d, boxplot, barplot#, histogram
dialogs[methods.ID_PLOTS_SCATTER_2D] = scatterplot2d.ScatterPlot2dOptionsDialog
#dialogs[methods.ID_PLOTS_HISTOGRAM] = histogram.HistogramOptionsDialog
dialogs[methods.ID_PLOTS_BARPLOT] = barplot.BarplotOptionsDialog
dialogs[methods.ID_PLOTS_BOXPLOT] = boxplot.BoxplotOptionsDialog











