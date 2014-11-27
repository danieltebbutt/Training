# Importer for Dan's training application.
# This contains generic functions for importing data and is extended by other classes.

import os
from database import Database

class Importer:

    def __init__(self, filename):
        self.filename = filename
        
    def fileExists(self):
        return os.path.isfile(self.filename)             
        
    def clashingData(self, data):
        temp = Database()
        self.loadData(temp)
        return temp.clash(data)    
        
    def loadData(self, data):
        print "Error! loadData not over-ridden"
        return
                    
        