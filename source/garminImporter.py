# GarminImporter for Dan's training application.
# This contains specific functions for importing data from a Garmin .csv export.

import os
import csv

from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

from importer import Importer
from database import Database
from activity import Activity

tempFilename = ".\\temp.csv"

class GarminImporter(Importer):

    def loadData(self, data):
        with open(self.filename, 'rb') as inStream, open(tempFilename, 'wb') as outStream:
            # Only write to new file if the line contains a comma
            for line in inStream:
                if "," in line:
                    outStream.write(line)
                
            outStream.close()
            inStream.close()
        
        self.filename = tempFilename
        super(GarminImporter, self).loadData(data)
        os.remove(tempFilename)
        return
        
