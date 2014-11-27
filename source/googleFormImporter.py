# GoogleFormImporter for Dan's training application.
# This contains specific functions for importing data from a Google .csv export from a sheet with Form responses.

import os
import csv

from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

from importer import Importer
from database import Database
from activity import Activity

class GoogleFormImporter(Importer):

    def loadData(self, data):
        fileStream = open(self.filename, 'rb')
        reader = csv.reader(fileStream)
        for row in reader:
            try:
                date = datetime.strptime(row[1], "%d/%m/%Y")
                distance = float(row[2])
                abstime = datetime.strptime(row[3], "%H:%M:%S")
                deltatime = timedelta(seconds = abstime.second, minutes = abstime.minute, hours = abstime.hour)
                if row[4]:
                    heartRate = float(row[4])
                else:
                    heartRate = 0
                if row[5]:
                    elevationGain = float(row[5])
                else:
                    elevationGain = 0
                route = row[6]
                notes = row[7]

                activity = Activity(date, distance, deltatime, notes, heartRate, elevationGain, route)

                data.addActivity(activity)
            except Exception as exception:
                #print "Ignore %s because %s"%(row, str(exception))
                pass
        return