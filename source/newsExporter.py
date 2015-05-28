# NewsExporter for Dan's training application.
# This contains specific functions for exporting data for Dan's news feed.

from exporter import Exporter
from datetime import timedelta
from datetime import datetime

class NewsExporter(Exporter):

    def writeRuns(self, data):
        
        for activity in data.training:
            line = ""
            line += activity.date.strftime("%Y-%m-%d")
            line += ","
            if activity.isRace():
                line += "Ran %s in %s"%(activity.raceName, activity.time)
            else:
                line += "Ran %.1fkm in %s"%(activity.distance, activity.time)
            line += ","
            if activity.isRace():
                score = 75
            else:
                score = activity.distance * 2
            line += "%d"%score
            line += "\n"
            self.outputfile.write(line)

    def writeMonthlySummaries(self, data):
        
        for month in data.getMonths():
            distance = 0.0
            for activity in month.training:
                distance += activity.distance
            
            if month.startDate.month == 12:
                reportDate = month.startDate.replace(year = month.startDate.year + 1, month = 1)
            else:
                reportDate = month.startDate.replace(month = month.startDate.month + 1)
            
            line = ""
            line += reportDate.strftime("%Y-%m-%d")
            line += ","
            line += "%s running total: %dkm"%(month.startDate.strftime("%B"), distance)
            line += ",50\n"
            if reportDate < datetime.today().date():
                self.outputfile.write(line)

    def publish(self, data):

        self.outputfile = open(self.filename, 'w')

        self.writeRuns(data)
        self.writeMonthlySummaries(data)
        #self.writeYearlySummaries(data)
        
        self.outputfile.close()

        return

