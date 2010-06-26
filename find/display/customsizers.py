
import wx

ID_CBX   = wx.NewId()

def ChannelSelectorSizer(parent):
    """
    Create a sizer containing combo boxes for selecting displayed axes
    
    @var parent: The parent container into which the sizer will be inserted. 
                 The parent needs to implement a function called onCBXClick 
                 to handle the
    @rtype: tuple
    @return A tuple containing a list of the combo boxes and a wx.BoxSizer 
            for their layout
    """
    selectorSizer = wx.BoxSizer(wx.HORIZONTAL)
    dataSelectors = []
    dimensions = ['X axis', 'Y axis']
    # add combo boxes
    for i in range(len(dimensions)):
        dataSelectors.append(wx.ComboBox(parent, ID_CBX+i, "", (-1,-1), (160, -1), [], wx.CB_READONLY))
        selectorSizer.Add(dataSelectors[i],0,wx.EXPAND | wx.RIGHT, 10)
        selectorSizer.Add(wx.StaticText(parent, -1, dimensions[i], (20, 10)), 1, wx.EXPAND)
        parent.Bind(wx.EVT_COMBOBOX, parent.OnCBXClick, id=ID_CBX+i)
    
    return (dataSelectors, selectorSizer)

def populateSelectors(dataSelectors, labels, ids):
    """
    Set the axis selection list
    """
    for i in range(len(dataSelectors)):
        dataSelectors[i].SetItems(labels)
        dataSelectors[i].SetSelection(i)
        # associate the dimension number with each label item
        for j in range(len(labels)):
            dataSelectors[i].SetClientData(j, ids[j])













