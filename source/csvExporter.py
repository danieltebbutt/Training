from .exporter import Exporter
from datetime import timedelta
from datetime import datetime

class CsvExporter(Exporter):

    def publish(self, data):
        
        if self.filename:
            self.outputfile = open(self.filename, 'w')

        page = ""

        line = "Date,Distance,Time,Notes,Heartrate,Elevation gain,Race name,Route\n"
        page += line
        for activity in data.training:
            line = "%s,%.2f,%s,\"%s\",%d,%d,%s,\"%s\"\n"%(
                                      activity.date.strftime("%Y-%m-%d"), 
                                      activity.distance, 
                                      activity.time, 
                                      activity.notes, 
                                      activity.heartrate, 
                                      activity.elevation, 
                                      activity.raceName,
                                      activity.route)
            page += line

        if self.filename:        
            self.outputfile.write(page)
            self.outputfile.close()

        return page

