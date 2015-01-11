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
            self.outputfile.write("<div id=\"chart_div%d\" style=\"width: 900px; height: 500px;\"></div>\n"%ii)

        self.outputfile.write("</body>\n\
</html>\n")

    def writeFitness(self, data):
        # indexed by (isRace, isTreadmill)
        pointColors = { (False, False) : "null",
                        (True, False)  : "ff0000",
                        (False, True)  : "32cd32",
                        }
        self.outputfile.write("\
  var data%d = google.visualization.arrayToDataTable([\n\
  ['Date', 'Fitness', {'type' : 'string', 'role' : 'style' }],\n"%self.chartIndex)

        for activity in data.getFitness():
            self.outputfile.write("[new Date(%d,%d,%d),{v:%.1f, f:'%s'}, %s],\n"%(\
                                   activity.date.year,
                                   activity.date.month - 1,
                                   activity.date.day,
                                   activity.fitness(),
                                   activity.summaryString(),
                                   "'point {fill-color: #%s}'"%pointColors[(activity.isRace, activity.isTreadmill())]))

        self.outputfile.write("]);\n\
\n\
  var options%d = {\n\
    title: 'Fitness',\n\
    legend: {position: 'none'},\n"%(self.chartIndex))
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

    def writeRaces12Weeks(self, data):
        self.writeRaces(data, 12)

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

            self.outputfile.write("[{v:%.1f, f:'%s'},%.1f, 'point {fill-color: %s}'],\n"%( \
                                   training.kilometres(),                                     \
                                   activity.summaryString(),                                  \
                                   activity.raceFitness(),                                    \
                                   pointColors[activity.raceDistance()]))

        self.outputfile.write("]);\n\
\n\
  var options%d = {\n\
    title: 'Race performance vs training over last %d weeks',\n\
    legend: {position: 'none'},\n"%(self.chartIndex, \
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
        self.writePeriods(data.getWeeks(), "week")

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

    def actionTemplate(self, data, template):

        # tag: (function, isScript)
        tags = { "###WEEKLY###"    : (self.writeWeekly, True),
                 "###RACES###"     : (self.writeRaces12Weeks, True),
                 "###FITNESS###"   : (self.writeFitness, True),
                 "###TREADMILL###" : (self.writeHomeTreadmill, False),
                 "###GYM###"       : (self.writeGymTreadmill, False),
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
                self.outputfile.write("<div id=\"chart_div%d\" style=\"width: 900px; height: 500px;\"></div>\n"%writeTags[tag])
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

