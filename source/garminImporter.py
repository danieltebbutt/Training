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

class GarminImporter(Importer):


    def loadData(self, data):
        fileStream = open(self.filename, 'rb')
        reader = csv.reader(fileStream)
        for row in reader:
            try:
                (crap,day,month,year,crap2) = row[4].split(" ", 4)
                datestring = "%s-%s-%s"%(day,month,year)
                date = datetime.strptime(datestring, "%d-%b-%Y")
                distance = float(row[6])
                try:
                    abstime = datetime.strptime(row[5], "%H:%M:%S")
                except:
                    abstime = datetime.strptime(row[5], "%M:%S")
                    pass
                deltatime = timedelta(seconds = abstime.second, minutes = abstime.minute, hours = abstime.hour)
                heartRate = float(row[10])
                elevationGain = float(row[7])

                if (distance > 0):
                    activity = Activity(date, distance, deltatime, "", heartRate, elevationGain)

                data.addActivity(activity)
            except Exception as exception:
                #print "Ignore %s because %s"%(row, str(exception))
                pass
        return