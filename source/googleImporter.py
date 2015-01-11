# GoogleImporter for Dan's training application.
# This contains specific functions for importing data from a Google .csv export.

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

class GoogleImporter(Importer):

    def loadData(self, data):
        # Rewrite with a fixed csv header into a temp file and then call the parent class to parse
        with open(self.filename, 'rb') as inStream, open(tempFilename, 'wb') as outStream:
            # Discard first line
            line1 = inStream.readline()
            
            # Write to new file
            for line in inStream:
                outStream.write(line)
                
            outStream.close()
            inStream.close()
        
        self.filename = tempFilename
        super(GoogleImporter, self).loadData(data)
        os.remove(tempFilename)
        return