"""
This module provides the functionality to 
read and write CSV files from FACS data. 
"""
from data.io import FILE_INPUT, FILE_OUTPUT
from plugins.pluginbase import IOPlugin 

from matplotlib import mlab

__all__ = ['register_csv']

class CSVPlugin(IOPlugin):
    """Read and write CSV files."""
    
    def register(self):
        return {FILE_INPUT: self.read, FILE_OUTPUT: self.save}
    
    def fileType(self):
        return 'Comma Separated Values (*.csv)|*.csv' 
    
    def read(self):
        """
        Load the specified FACS data file. It is assumed that the first line
        of the file contains the column labels.
        
        @type filename: string
        @param filename: The name of the FACS data file to be loaded
        
        @rtype: tuple
        @return: A tuple containing a list of column labels and numpy array 
            containing the actual FACS data.
        """
        print 'loading:', self.filename
        # Retrieve first line of column labels
        facsFile = open(self.filename,'r')
        labels = facsFile.readline().rstrip().replace('"','').split(',')
        facsFile.close()
        print 'Column labels:',labels
        # load actual data
        data = mlab.load(self.filename, delimiter=',', skiprows=1)
        return (labels,data, None)
    
    def save(self, facsData):
        """
        Save the supplied FACS data to a file.
        """
        with open(self.filename, 'w') as fp:
            fp.write(','.join(facsData.labels))
            for row in facsData.data:
                fp.write(','.join(map(str,row)))
                fp.write('\n')
        
        
        
        
def register_csv():
    return ('csv', CSVPlugin)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        