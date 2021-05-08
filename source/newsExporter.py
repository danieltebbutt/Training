# NewsExporter for Dan's training application.
# This contains specific functions for exporting data for Dan's news feed.

from .exporter import Exporter

from datetime import timedelta
from datetime import datetime
import io

class NewsExporter(Exporter):

    def writeRuns(self, data):
        
        for activity in data.training:
            date = activity.date.strftime("%Y-%m-%d")

            if activity.isRace():
                score = 75
                type = "RACE"
                desc = "Ran %s in %s"%(activity.raceName, activity.time)
            else:
                score = 10 + activity.distance
                type = "RUN"
                desc = "Ran %.1fkm in %s"%(activity.distance, activity.time)

            line = "%s,%s,%s,%d\n"%(type, date, desc, score)
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
            line += "RUNTOTAL,"
            line += reportDate.strftime("%Y-%m-%d")
            line += ","
            line += "%s running total: %dkm"%(month.startDate.strftime("%B"), distance)
            line += ",%d\n"%(10 + (distance / 4))
            if reportDate <= datetime.today().date():
                self.outputfile.write(line)

    def writeYearlySummaries(self, data):
        
        for year in data.getYears():
            distance = 0.0
            for activity in year.training:
                distance += activity.distance
            
            reportDate = year.startDate.replace(year = year.startDate.year + 1)
            
            line = ""
            line += "RUNTOTAL,"
            line += reportDate.strftime("%Y-%m-%d")
            line += ","
            line += "%d running total: %dkm"%(year.startDate.year, distance)
            line += ",%d\n"%(10 + (distance / 10))
            if reportDate < datetime.today().date():
                self.outputfile.write(line)

    def publish(self, data):

        if self.filename:
            self.outputfile = open(self.filename, 'w')
        else:
            self.outputfile = io.StringIO()

        self.writeRuns(data)
        self.writeMonthlySummaries(data)
        self.writeYearlySummaries(data)

        if not self.filename:
            html = self.outputfile.getvalue()
        else:
            html = ""

        self.outputfile.close()

        return html

