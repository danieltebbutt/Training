# GoogleWebImporter for Dan's training application.
# This contains specific functions for importing data from a Google webpage with Form responses.

import os
import csv
import urllib2

from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

from importer import Importer
from database import Database
from activity import Activity
from googleFormImporter import GoogleFormImporter

class GoogleWebImporter(Importer):
    address = "https://docs.google.com/spreadsheets/d/1_JgI_c7KhC4nXs_LStbySvarm7Cz-wDTqKgtsli-4KA/export?format=csv"

    # File doesn't need to exist for this class
    def fileExists(self):
        return True
    
    def loadData(self, data):
        response = urllib2.urlopen(self.address)
        html = response.read()
        
        fileStream = open(self.filename, 'w')
        fileStream.write(html)
        fileStream.close()
        
        formImporter = GoogleFormImporter(self.filename)
        formImporter.loadData(data)
        
        