# Importer for Dan's training application.
# This contains generic functions for importing data and is extended by other classes.

import os
import csv
import codecs
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

from .database import Database
from .activity import Activity

class Importer(object):

    def __init__(self, filename = None, inputStream = None):
        self.filename = filename
        self.inputStream = inputStream

    def fileExists(self):
        return os.path.isfile(self.filename)

    def clashingData(self, data):
        temp = Database()
        self.loadData(temp)
        return temp.clash(data)

    def parseDate(self, text):
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%b-%Y', '%d/%m/%Y %H:%M:%S', "%a, %d %b %Y %H:%M"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                pass
        raise ValueError('no valid date format found')

    def parseTime(self, text):
        for fmt in ('%H:%M:%S', '%M:%S'):
            try:
                abstime = datetime.strptime(text, fmt)
                deltatime = timedelta(seconds = abstime.second, minutes = abstime.minute, hours = abstime.hour)
                return deltatime
            except ValueError:
                pass
        raise ValueError('no valid date format found')

    def getValue(self, row, valueList, default = None):
        for value in valueList:
            if value in row and row[value]:
                return row[value]

        return default

    def loadData(self, data):
        if self.filename:
            fileStream = open(self.filename, 'rb')
        else:  
            #fileStream = codecs.iterdecode(self.inputStream, "utf-8")
            fileStream = iter(self.inputStream.splitlines())

        reader = csv.DictReader(fileStream)
        for row in reader:
            try:
                date = self.parseDate(self.getValue(row, ["Date", "Timestamp", "Start"]))

                distance = float(self.getValue(row, ["Distance", "Dist"], "0"))

                deltatime = self.parseTime(self.getValue(row, ["Time"]))

                heartRate = float(self.getValue(row, ["Heart rate", "Avg HR", "HR", "Heartrate"], "0"))

                elevationGain = float(self.getValue(row, ["Climb", "Elevation Gain", "Elevation gain"], "0"))

                route = self.getValue(row, ["Location", "Route"], "")

                notes = self.getValue(row, ["Notes", "Comment"], "")
                
                raceName = self.getValue(row, ["Race name"], "")

                shoes = self.getValue(row, ["Shoes"], "")

                activity = Activity(date, distance, deltatime, notes, heartRate, elevationGain, route, raceName, shoes)

                data.addActivity(activity)

            except Exception as exception:
                if float(self.getValue(row, ["Distance", "Dist"], "0")) != 0:
                    print("Found distance but could not parse row:\n%s\n%s"%(row, str(exception)))
                pass
        return
