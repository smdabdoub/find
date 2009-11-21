from __future__ import with_statement

"""
This module provides the functionality to 
read and write CSV files from FACS data. 
"""
from plugins.pluginbase import IOPlugin 

class CSVPlugin(IOPlugin):
    
    def register(self):
        return [self.read, self.save]
    
    def read(self, file):
        """
        Load the specified FACS data file. It is assumed that the first line
        of the file contains the column labels.
        
        @type filename: string
        @param filename: The name of the FACS data file to be loaded
        
        @rtype: tuple
        @return: A tuple containing a list of column labels and numpy array 
            containing the actual FACS data.
        """
        print 'loading:',filename
        # Retrieve first line of column labels
        facsFile = open(filename,'r')
        labels = facsFile.readline().rstrip().replace('"','').split(',')
        facsFile.close()
        print 'Column labels:',labels
        # load actual data
        data = mlab.load(filename, delimiter=',', skiprows=1)
        return (labels,data)
    
    def save(self, file, data, labels):
        """
        Save the supplied FACS data to a file.
        """
        with open(file, 'w') as fp:
            fp.write(','.join(labels))
            for row in data:
                fp.write(','.join(map(str,row)))
                fp.write('\n')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        