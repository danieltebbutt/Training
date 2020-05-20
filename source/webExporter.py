# WebExporter for Dan's training application.
# This contains specific functions for exporting data to the web.

import pdb
import os
from database import Database
from exporter import Exporter
import webbrowser
from os import listdir
from os.path import isfile, join
from datetime import timedelta
from datetime import datetime

class WebExporter(Exporter):

    def writeHeader(self):
        self.outputfile.write("\
<html>\n\
  <head>\n")
        self.writeScriptHeader()

    def writeScriptHeader(self):
        self.outputfile.write("\
    <script type=\"text/javascript\" src=\"https://www.google.com/jsapi\"></script>\n\
    <script type=\"text/javascript\">\n\
      google.load(\"visualization\", \"1\", {packages:[\"corechart\"]});\n\
google.setOnLoadCallback(drawChart);\n\
function drawChart() {\n")

    def writeScriptFooter(self):
        self.outputfile.write("\
}\n\
    </script>\n")

    def writeFooter(self):
        self.writeScriptFooter()
        self.outputfile.write("\
  </head>\n\
  <body>\n")
        for ii in range(1,self.chartIndex):
            self.outputfile.write("<div id=\"chart_div%d\" style=\"width: 800px; height: 500px;\"></div>\n"%ii)

        self.outputfile.write("</body>\n\
</html>\n")

    def writeActivityScore(self, data, fun, name):
        # indexed by (isRace, isTreadmill)
        pointColors = { (False, False) : "0000ff",
                        (True, False)  : "ff0000",
                        (False, True)  : "32cd32",
                        }
        self.outputfile.write("\
  var data%d = google.visualization.arrayToDataTable([\n\
  ['Date', '%s', {'type' : 'string', 'role' : 'style' }],\n"%(self.chartIndex, name))

        for activity in data.getFitness():
            self.outputfile.write("[new Date(%d,%d,%d),{v:%.1f, f:'%s'}, %s],\n"%(\
                                   activity.date.year,
                                   activity.date.month - 1,
                                   activity.date.day,
                                   eval("activity.%s"%fun),
                                   activity.summaryString(),
                                   "'point {fill-color: #%s}'"%pointColors[(activity.isRace(), activity.isTreadmill())]))

        self.outputfile.write("]);\n\
\n\
  var options%d = {\n\
    title: '%s',\n\
    legend: {position: 'none'},\n\
    backgroundColor: { fill: 'transparent' },\n"%(self.chartIndex, name))
#        self.outputfile.write("trendlines: { 0: {} },\n")
        self.outputfile.write("explorer: { actions: ['dragToZoom', 'rightClickToReset'] }")
        
        self.outputfile.write("\
  };\n\
\n\
  var chart%d = new google.visualization.ScatterChart(document.getElementById('chart_div%d'));\n\
\n\
  chart%d.draw(data%d, options%d);\n"%(self.chartIndex, \
                                       self.chartIndex, \
                                       self.chartIndex, \
                                       self.chartIndex, \
                                       self.chartIndex))
        self.chartIndex += 1

    def writeFitness(self, data):
        self.writeActivityScore(data, "fitness()", "Fitness")
        
    def writeIntensity(self, data):
        self.writeActivityScore(data, "intensity()", "Intensity")

    def writeRaces12Weeks(self, data):
        self.writeRaces(data, 12)

    def writeRaces8Weeks(self, data):
        self.writeRaces(data, 8)

    def writeRaces(self, data, leadUp):  
        pointColors = { 5  : "#32cd32",
                        10 : "#ffd700",
                        21 : "#ff8000",
                        42 : "#ff0000"}

        self.outputfile.write("\
  var data%d = google.visualization.arrayToDataTable([\n\
  ['%d weeks', 'Performance', {'type' : 'string', 'role' : 'style' } ],\n"%(self.chartIndex, leadUp))

        for activity in data.getRaces():
            endDate = activity.date - timedelta(days = 1)
            startDate = endDate - timedelta(days = 1 + (leadUp * 7))
            training = data.range(startDate, endDate)

            self.outputfile.write("[{v:%.1f, f:'%s'},%.2f, 'point {fill-color: %s}'],\n"%( \
                                   training.kilometres(),                                     \
                                   activity.summaryString(),                                  \
                                   activity.raceFitness(),                                    \
                                   pointColors[activity.raceDistance()]))

        self.outputfile.write("]);\n\
\n\
  var options%d = {\n\
    title: 'Race performance vs training over last %d weeks',\n\
    legend: {position: 'none'},\n\
    backgroundColor: { fill: 'transparent' },\n"%(self.chartIndex, \
                                   leadUp))

        self.outputfile.write("trendlines: { 0: {} }")
        self.outputfile.write("\
  };\n\
\n\
  var chart%d = new google.visualization.ScatterChart(document.getElementById('chart_div%d'));\n\
\n\
  chart%d.draw(data%d, options%d);\n"%(self.chartIndex, \
                                       self.chartIndex, \
                                       self.chartIndex, \
                                       self.chartIndex, \
                                       self.chartIndex))
        self.chartIndex += 1

    def writeTraining(self, data):  
        pointColors = { False  : "null",
                        True  : "32cd32",
                        }

        leadUp = 12
                        
        self.outputfile.write("\
  var data%d = google.visualization.arrayToDataTable([\n\
  ['%d weeks', 'Performance', {'type' : 'string', 'role' : 'style' } ],\n"%(self.chartIndex, leadUp))

        for activity in data.training:
            if (activity.fitness() != 0):            
                endDate = activity.date - timedelta(days = 1)
                startDate = endDate - timedelta(days = 1 + (leadUp * 7))
                training = data.range(startDate, endDate)

                self.outputfile.write("[{v:%.1f, f:'%s'},%.2f, 'point {fill-color: %s}'],\n"%( \
                                       training.kilometres(),                                     \
                                       activity.summaryString(),                                  \
                                       activity.fitness(),                                    \
                                       pointColors[activity.isTreadmill()]))

        self.outputfile.write("]);\n\
\n\
  var options%d = {\n\
    title: 'Fitness vs training over last %d weeks',\n\
    legend: {position: 'none'},\n\
    backgroundColor: { fill: 'transparent' },\n"%(self.chartIndex, \
                                   leadUp))

        self.outputfile.write("trendlines: { 0: {} }")
        self.outputfile.write("\
  };\n\
\n\
  var chart%d = new google.visualization.ScatterChart(document.getElementById('chart_div%d'));\n\
\n\
  chart%d.draw(data%d, options%d);\n"%(self.chartIndex, \
                                       self.chartIndex, \
                                       self.chartIndex, \
                                       self.chartIndex, \
                                       self.chartIndex))
        self.chartIndex += 1
                
    def writeWeekly(self, data):
        self.writePeriods(data.getWeeks()[-208:], "week")

    def writePeriods(self, periods, periodName):
        self.outputfile.write("\
  var data%d = google.visualization.arrayToDataTable([\n\
  ['Week', 'Kilometres', {'type' : 'string', 'role' : 'style' }],\n"%self.chartIndex)

        for period in periods:
            self.outputfile.write("['%s',%.1f, %s],\n"%(\
                                   period.startDate.strftime("%b-%Y"),
                                   period.kilometres(),
                                   "'#ff0000'" if period.containsRace() else "null"))

        self.outputfile.write("]);\n\
\n\
  var options%d = {\n\
    title: 'Kilometres per %s',\n\
    legend: {position: 'none'},\n\
    backgroundColor: { fill: 'transparent' },\n\
    vAxis: {viewWindowMode:'explicit', viewWindow:{min:0}}\n\
  };\n\
\n\
  var chart%d = new google.visualization.ColumnChart(document.getElementById('chart_div%d'));\n\
\n\
  chart%d.draw(data%d, options%d);\n"%(self.chartIndex, \
                                   periodName,      \
                                   self.chartIndex, \
                                   self.chartIndex, \
                                   self.chartIndex, \
                                   self.chartIndex, \
                                   self.chartIndex))
        self.chartIndex += 1

    def writeHomeTreadmill(self, data):

        runs = data.getTreadmillPeriod()

        purchaseDate = datetime(year=2014, month=11, day = 21).date()

        runs = runs.range(purchaseDate)
        cost = 1600
        
        self.outputfile.write("<ul>\n\
<li>Owned for:      %d days\n\
<li>Times used:     %d</li>\n\
<li>Distance run:   %.0fkm</li>\n\
<li>Cost per km:    &pound;%.2f</li>\n\
<li>Cost per run:   &pound;%.2f</li>\n\
</ul>"%((datetime.today().date() - purchaseDate).days, \
          len(runs.training),                \
          runs.kilometres(),                 \
          cost / runs.kilometres(),          \
          cost / len(runs.training)))

    def writeGymTreadmill(self, data):

        runs = data.getTreadmillPeriod()

        endDate = datetime(year=2013, month=12, day = 1).date()
        startDate = datetime(year=2012, month=9, day = 1).date()

        runs = runs.range(startDate, endDate)
        cost = 200

        self.outputfile.write("<ul>\n\
<li>Member for:     1 year\n\
<li>Times used:     %d</li>\n\
<li>Distance run:   %.0fkm</li>\n\
<li>Cost per km:    &pound;%.2f</li>\n\
<li>Cost per run:   &pound;%.2f</li>\n\
</ul>"%(len(runs.training),                  \
          runs.kilometres(),                 \
          cost / runs.kilometres(),          \
          cost / len(runs.training)))

    def writeRecent(self, data):
        endDate = datetime.today().date()
        startDate = endDate - timedelta(weeks = 12)
 
        runs = data.range(startDate, endDate)

        self.outputfile.write("%.1f km run in the last 12 weeks."%runs.kilometres())

    def timedeltaToHMS(self, timedelta):
        hours = timedelta.total_seconds() / 3600
        minutes = (timedelta.total_seconds() / 60) % 60
        seconds = timedelta.total_seconds() % 60
        return (hours, minutes, seconds)
        
    def timedeltaToMS(self, timedelta):
        hours, minutes, seconds = self.timedeltaToHMS(timedelta)
        return (minutes, seconds)
          
    def writeRecords(self, data):
        
        self.outputfile.write("<p>Since March 2012:</p>\n")
        
        # Totals
        self.outputfile.write("<p>Total:</p>\n")
        self.outputfile.write("<ul>\n")
        self.outputfile.write("<li>Distance run:       %dkm</li>\n"%data.kilometres())
        self.outputfile.write("<li>Number of runs:     %d</li>\n"%len(data.training))
        self.outputfile.write("<li>Time spent running: %d hours</li>\n"%self.timedeltaToHMS(data.time())[0])
        self.outputfile.write("</ul>\n")

        # Per year
        self.outputfile.write("<p>Distance per year:</p>\n")
        self.outputfile.write("<ul>\n")
        
        for year in range(2012, datetime.now().year + 1):
            year_data = data.range(datetime(year=year,month=1,day=1).date(),datetime(year=year,month=12,day=31).date())
            self.outputfile.write("<li>%d:                 %dkm</li>\n"%(year, year_data.kilometres()))
        self.outputfile.write("</ul>\n")

 
        # Averages
        self.outputfile.write("<p>Average:</p>\n")
        self.outputfile.write("<ul>\n")
        self.outputfile.write("<li>Run length: %.1fkm</li>\n"%(data.kilometres() / len(data.training)))
        self.outputfile.write("<li>Run time:   %2d:%02d:%02d</li>\n"%self.timedeltaToHMS(data.time() / len(data.training)))
        seconds_per_km = data.time().total_seconds() / data.kilometres()
        self.outputfile.write("<li>Pace:       %d:%d per km</li>\n"%(seconds_per_km / 60, seconds_per_km % 60))
        heartbeats, timeMeasured = data.heartbeats()
        self.outputfile.write("<li>Heart rate: %dbpm</li>\n"%(heartbeats * 60 / timeMeasured.total_seconds()))
        self.outputfile.write("</ul>\n")
                  
        # Best
        self.outputfile.write("<p>Personal bests:</p>\n")
        self.outputfile.write("<ul>\n")
        self.outputfile.write("<li>Longest run:        %2d:%02d:%02d</li>\n"%self.timedeltaToHMS(data.longest()))
        self.outputfile.write("<li>Furthest run:       %dkm</li>\n"%data.furthest())
        self.outputfile.write("<li>Highest average HR: %d</li>\n"%data.highestHR())
        self.outputfile.write("<li>Longest running streak: %d days</li>\n"%data.longestStreak())
        self.outputfile.write("<li>5km:                %2d:%02d (%s)</li>\n"%(self.timedeltaToMS(data.bestTime(5)) + (data.bestDescription(5),)))
        self.outputfile.write("<li>10km:               %2d:%02d (%s)</li>\n"%(self.timedeltaToMS(data.bestTime(10)) + (data.bestDescription(10),)))
        self.outputfile.write("<li>21km:               %d:%02d:%02d (%s)</li>\n"%(self.timedeltaToHMS(data.bestTime(21.1)) + (data.bestDescription(21.1),)))
        self.outputfile.write("<li>42km:               %d:%02d:%02d (%s)</li>\n"%(self.timedeltaToHMS(data.bestTime(42.2)) + (data.bestDescription(42.2),)))
        self.outputfile.write("</ul>\n")
        
                  
    def actionTemplate(self, data, template):

        # tag: (function, isScript)
        tags = { "###WEEKLY###"    : (self.writeWeekly, True),
                 "###RACES###"     : (self.writeRaces12Weeks, True),
                 "###FITNESS###"   : (self.writeFitness, True),
                 "###TREADMILL###" : (self.writeHomeTreadmill, False),
                 "###GYM###"       : (self.writeGymTreadmill, False),
                 "###RECORDS###"   : (self.writeRecords, False),
                 "###INTENSITY###" : (self.writeIntensity, True),
                 "###TRAINING###"  : (self.writeTraining, True),
                 "###RECENT###"    : (self.writeRecent, False),
                 }

        fileStream = open(join(self.templateDir,template), 'r')
        self.outputfile = open(join(self.outputDir,template), 'w')

        self.chartIndex = 1

        weekly = False
        fitness = False

        writeTags = {}

        for line in fileStream:
            if line.strip() in tags and tags[line.strip()][1]:
                writeTags[line.strip()] = 0

        fileStream.seek(0)

        for line in fileStream:
            if "</head>" in line.lower():
                if len(writeTags) > 0:
                    self.writeScriptHeader()
                    for tag in writeTags:
                        writeTags[tag] = self.chartIndex
                        tags[tag][0](data)
                    self.writeScriptFooter()
                self.outputfile.write(line)
            elif line.strip() in writeTags:
                self.outputfile.write("<div id=\"chart_div%d\" style=\"width: 800px; height: 500px;\"></div>\n"%writeTags[tag])
            elif line.strip() in tags:
                tags[line.strip()][0](data)
            else:
                self.outputfile.write(line)
        self.outputfile.close()

    def publish(self, data):

        if self.type == self.SINGLE:
            self.chartIndex = 1

            self.outputfile = open(self.filename, 'w')

            self.writeHeader()
            self.writeWeekly(data)
            self.writeFitness(data)
            self.writeRaces(data, 12)
            self.writeFooter()

            self.outputfile.close()

            webbrowser.open(self.filename)

        elif self.type == self.TEMPLATE:
            templateFiles = [ f for f in listdir(self.templateDir) if isfile(join(self.templateDir,f)) ]

            for template in templateFiles:
                self.actionTemplate(data, template)
                #webbrowser.open(join(self.outputDir, template))

        return

