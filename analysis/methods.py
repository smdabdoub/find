'''
@author: Shareef Dabdoub
'''

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
        - plugin flag
    """
    global methods
    methods[descriptor[0]] = descriptor
    
def AvailableMethods():
    """
    Retrieve the list of available analysis methods in this module.
    
    @rtype: list of tuples
    @return: A list descriptor (:@see: addPluginMethod) tuples for each registered method. 
    """
    return methods

def getMethod(id):
    """
    Retrieve an analysis method by its ID.
    
    :@type id: int or str
    :@param id: The identifier for a plotting method. An int id is required
                for the wx event subsystem, but a string id is required as a 
                unique id for plugin authors to specify dependencies on 
                analysis methods.
    :@rtype: method
    :@return: The method associated with the ID, or None.
    """
    try:
        int(id)
    except ValueError:
        return methods[id][-2]
        
    return methods[strID(id)][-2]


def strID(methodID):
    """
    Get the string identifier of an analysis method by its int ID.
    
    @type methodID: int
    @param methodID: One of the module-defined ID_* constants for the available methods.
    @rtype: string
    @return: The string ID of the specified analysis method
    """
    if (methodID is not None):
        for id in methods:
            if methods[id][1] == methodID:
                return methods[id][0]
    


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    