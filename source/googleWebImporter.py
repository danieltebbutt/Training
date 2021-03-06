# GoogleWebImporter for Dan's training application.
# This contains specific functions for importing data from a Google webpage with Form responses.

import os
import csv
import urllib2
import ConfigParser
import ssl

from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

from importer import Importer
from database import Database
from activity import Activity

tempFilename = "./temp.csv"

class GoogleWebImporter(Importer):

    def __init__(self, address):
        config = ConfigParser.ConfigParser()
        config.readfp(open('training.ini'))
        self.address = config.get("GoogleWebImporter", address)
        super(GoogleWebImporter, self).__init__(tempFilename)
    
    # File doesn't need to exist for this class
    def fileExists(self):
        return True
    
    def loadData(self, data):
        response = urllib2.urlopen(self.address)
        html = response.read()
        
        fileStream = open(tempFilename, 'w')
        fileStream.write(html)
        fileStream.close()
        
        super(GoogleWebImporter, self).loadData(data)
        
        os.remove(tempFilename)
        
        