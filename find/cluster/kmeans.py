'''
Created on Mar 1, 2010

@author: shareef
'''
import transforms.methods as tm

import numpy as np
from scipy.cluster.vq import whiten, vq, kmeans, kmeans2
import Pycluster as pc
#TODO: catch the following error and alert user
# /Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages/scipy/cluster/vq.py:570: UserWarning: One of the clusters is empty. Re-run kmean with a different initialization. 
def kmeans(data, **kwargs):
    """
    Perform k-means clustering on unstructured N-dimensional data.
    
    @type data: array
    @param data: The data to be clustered
    @type kwargs: dict
    @param kwargs: The following args are accepted:
        - numClusters: The number of clusters to form (returned number of clusters may be less than k).
        - npasses: The number of times the k-means clustering algorithm is performed, 
        each time with a different (random) initial condition.
        - method: describes how the center of a cluster is found: 
            - method=='a': arithmetic mean.
            - method=='m': median.
        - initialCenters: a set of points that should be used as the initial
                          cluster centers
            
    @rtype: tuple
    @return: A list where each element indicates the cluster membership of the 
        corresponding index in the original data and a message string
    """
    k = 1
    npasses = 1
    method = 'a'
    initialCenters = None
    smartCenters = False
    msg = ''
    
    if 'numClusters' in kwargs:
        k = int(kwargs['numClusters'])
    if 'npasses' in kwargs:
        npasses = int(kwargs['npasses'])
    if 'method' in kwargs:
        method = kwargs['method']
    if 'initialCenters' in kwargs:
        initialCenters = kwargs['initialCenters']
    if 'smartCenters' in kwargs:
        smartCenters = kwargs['smartCenters']
    
    
    logData = tm.getMethod('log')(data)
    if initialCenters is not None:
        (clusterIDs, err, nOpt) = pc.kcluster(logData, k, npass=npasses, method=method)
        msg = "Number of rounds optimal solution was found: %i" % nOpt
    else:
        logCenters = tm.getMethod('log')(np.array(initialCenters[:k]))
        (centroids, clusterIDs) = kmeans2(logData, logCenters, minit='matrix')
        if len(np.unique(clusterIDs)) < k:
            wx.MessageBox('Warning: One or more of the returned clusters are empty. Please choose different initial cluster centers and re-run k-means for better results.', 'Insufficiently varied cluster centers', wx.OK | wx.ICON_WARNING)
            
    
    return clusterIDs, msg



#----------------------------------
# K-MEANS DIALOG CLASS
#----------------------------------
from cluster.util import ClusterOptionsDialog
from cluster.util import MAX_CLUSTERS
import display.formatters as f
import wx

class KMeansDialog(ClusterOptionsDialog):
    """
    Provide an options dialog for the k-means clustering algorithm 
    """
    
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'k-means Options', size=(350, 300))
        self.CenterOnParent()
        
        # create form controls
        self.txtNumClusters   = wx.TextCtrl(self, wx.ID_ANY, '', size=(50,20))
        self.cbxMethod        = wx.ComboBox(self, wx.ID_ANY, 'Mean', (-1,-1), (160, -1), ['Mean','Median'], wx.CB_READONLY)
        self.txtNumPasses     = wx.TextCtrl(self, wx.ID_ANY, '5', size=(50,20))
        self.chkInitialCenters = wx.CheckBox(self, wx.ID_ANY, 'Manually select centers?')
        self.initialCenters = []
        
        self.chkInitialCenters.Bind(wx.EVT_CHECKBOX, self.chkInitialCenters_Click)
        
        # create a table of label-input controls
        self.formSizer = wx.GridSizer(4, 2, vgap=20) #rows,cols,vgap,hgap
        self.formSizer.Add(wx.StaticText(self, wx.ID_ANY, 'Number of clusters:', (20, 10)), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtNumClusters, 1)
        self.formSizer.Add(wx.StaticText(self, wx.ID_ANY, 'Center calculation:', (20, 5)), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.cbxMethod, 1, wx.EXPAND)
        self.formSizer.Add(wx.StaticText(self, wx.ID_ANY, 'Number of passes:', (20, 10)), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.formSizer.Add(self.txtNumPasses, 1)
        
        # create the button row
        self.buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL | wx.HELP)
        self.buttonSizer.AffirmativeButton.Bind(wx.EVT_BUTTON, self.cmdOK_Click)
        self.buttonSizer.HelpButton.Bind(wx.EVT_BUTTON, self.cmdHelp_Click)
        
        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.formSizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.Add(self.chkInitialCenters, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.Add(self.getApplySizer(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 20)
        self.SetSizer(self.sizer)
        
        
    def cmdOK_Click(self,event):
        if self.chkInitialCenters.IsChecked():
            from cluster.dialogs import CenterChooserDialog
            dlg = CenterChooserDialog(self)
            if dlg.ShowModal() == wx.ID_OK:
                self.initialCenters = dlg.GetCenters()
            dlg.Destroy()
        
        super(KMeansDialog, self).cmdOK_click(event)
    
    
    def cmdHelp_Click(self, event):
        from display.help import HelpDialog
        HelpDialog(self, "k-means help", htmlfile="help/k-means_clustering.html").Show()
    
            
    def chkInitialCenters_Click(self, event):
        if (event.Selection):
            self.txtNumPasses.Enable(False)
            self.txtNumPasses.Value = '0'
        else:
            self.txtNumPasses.Enable(True)
    
    
    def validate(self):
        intVal = f.IntFormatter()
        msg = []
        
        if not intVal.validate(self.txtNumClusters.Value):
            msg.append("Number of clusters: A valid number must be entered.")
        else:
            val = int(self.txtNumClusters.Value)
            if val < 1 or val > MAX_CLUSTERS:
                msg.append("Number of clusters: A value between 1 and %d must be entered." % MAX_CLUSTERS)
            
            if self.chkInitialCenters.IsChecked() and len(self.initialCenters) < val:
                msg.append("The number of specified cluster centers is less than the number of desired clusters.")
        
        if not intVal.validate(self.txtNumPasses.Value):
            msg.append("Number of passes: A valid number must be entered.")
        else:
            if not self.chkInitialCenters.IsChecked():
                val = int(self.txtNumPasses.Value)
                if val < 1:
                    msg.append("Number of passes: A value greater than 1 must be entered")
                    
        return msg
    
    
    def getMethodArgs(self):
        """
        Gather all options specified in the dialog.
        
        @rtype: dict
        @return: A dictionary of algorithm options.
        """
        options = {}
        options['numClusters'] = self._getNumClusters()
        options['method'] = self._getMethod()
        options['numPasses'] = self._getNumPasses()
        options['initialCenters'] = self._getInitialCenters()
        return options
    
    def getStrMethodArgs(self):
        """
        Define an equivalency between the variable form of algorithm options 
        and the full string representation of the options.
        
        @rtype: tuple
        @return: A tuple containing:
            - A dictionary equating the short form of method option names
            with the full string descriptions.
            - A dictionary containing translations for any argument values
            that are not easily understandable
        """
        options = {}
        options['numClusters'] = 'Number of Clusters'
        options['method'] = 'Method'
        options['numPasses'] = 'Number of Passes'
        options['initialCenters'] = 'Manually chosen centers'
        values = {}
        values['method'] = {'a':'Mean', 'm':'Median'}
        return (options, values)
        
        
    def _getNumClusters(self):
        """
        Retrieve the specified cluster target for the algorithm.
        
        @rtype: int
        @return: The number of clusters to find.
        """
        return int(self.txtNumClusters.GetValue())
    
    def _getMethod(self):
        """
        Retrieve the specified method for determining the cluster center.
        
        @rtype: char
        @return: The method by which the cluster center is determined.
        """
        if (self.cbxMethod.GetValue() == 'Mean'):
            return 'a'
        if (self.cbxMethod.GetValue() == 'Median'):
            return 'm'
    
    def _getNumPasses(self):
        """
        Retrieve the specified number of times the k-means algorithm should
        be run.
        
        @rtype: int
        @return: The number of passes the algorithm should perform.
        """
        return int(self.txtNumPasses.GetValue())
    
    def _getInitialCenters(self):
        """
        Retrieve the user-specified points to be used as initial centers for the 
        k-means algorithm
        
        @rtype: list
        @return: A list of 2D points
        """
        return self.initialCenters