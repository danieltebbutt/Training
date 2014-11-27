# RacesImporter for Dan's training application.
# This contains specific functions for importing data from a simple .csv file containing date & race name.

import os
import csv

from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

from importer import Importer
from database import Database
from activity import Activity

class RacesImporter(Importer):


    def loadData(self, data):
        fileStream = open(self.filename, 'rb')
        reader = csv.reader(fileStream)
        for row in reader:
            try:
                date = datetime.strptime(row[0], "%d-%b-%Y")
                name = row[1]

                data.registerRace(date, name)
            except Exception as exception:
                #print "Ignore %s because %s"%(row, str(exception))
                pass
        return