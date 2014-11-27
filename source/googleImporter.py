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

class GoogleImporter(Importer):

    def loadData(self, data):
        fileStream = open(self.filename, 'rb')
        reader = csv.reader(fileStream)
        for row in reader:
            try:
                date = datetime.strptime(row[1], "%d-%b-%Y")
                distance = float(row[3])
                abstime = datetime.strptime(row[4], "%H:%M:%S")
                deltatime = timedelta(seconds = abstime.second, minutes = abstime.minute, hours = abstime.hour)
                if row[7] != "":
                    heartRate = float(row[7])
                else:
                    heartRate = 0
                if row[8] != "":
                    elevationGain = float(row[8])
                else:
                    elevationGain = 0
                route = row[16]
                notes = row[17]

                if (distance > 0):
                    activity = Activity(date, distance, deltatime, notes, heartRate, elevationGain, route)

                data.addActivity(activity)
            except Exception as exception:
                #print "Ignore %s because %s"%(row, str(exception))
                pass
        return