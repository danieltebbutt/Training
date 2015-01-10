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
        reader = csv.DictReader(fileStream)
        for row in reader:
            try:
                if "Date" in row and row["Date"]:
                    date = datetime.strptime(row["Date"], "%d/%m/%Y")
                else:
                    date = datetime.strptime(row["Timestamp"], "%d/%m/%Y %H:%M:%S")
                distance = float(row["Distance"])
                abstime = datetime.strptime(row["Time"], "%H:%M:%S")
                deltatime = timedelta(seconds = abstime.second, minutes = abstime.minute, hours = abstime.hour)
                
                heartRate = 0
                elevationGain = 0
                route = ""
                notes = ""
                
                if "Heart rate" in row and row["Heart rate"]:
                    heartRate = float(row["Heart rate"])
                if "Climb" in row and row["Climb"]:
                    elevationGain = float(row["Climb"])
                if "Location" in row:
                    route = row["Location"]                
                if "Notes" in row:
                    notes = row["Notes"]                    
                if "Comment" in row:
                    notes = row["Comment"]

                activity = Activity(date, distance, deltatime, notes, heartRate, elevationGain, route)

                data.addActivity(activity)
            except Exception as exception:
                print "Ignore %s because %s"%(row, str(exception))
                pass
        return