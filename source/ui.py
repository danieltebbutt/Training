# UI for Dan's training application
# This takes instructions as input and carries out actions


import sys

from database import Database
from googleImporter import GoogleImporter
from garminImporter import GarminImporter
from racesImporter import RacesImporter
from googleWebImporter import GoogleWebImporter
from importer import Importer
from webExporter import WebExporter
from webPublish import WebPublish
from datetime import datetime
from datetime import timedelta
from period import Period

class UI:

    def __init__(self, debug = False):
        self.debug = debug
        self.range = Period()
        self.instructions = {
            'test' : self.test,
            'debug' : self.changeDebug,
            'interactive' : self.interactive,
            'exit' : self.exit,
            'quit' : self.exit,
            'help' : self.help,
            'import' : self.importData,
            'dump' : self.dumpData,
            'weekly' : self.weekly,
            'export' : self.exportData,
            'publish' : self.publishHTML,
            'range' : self.makeRange,
            'filter' : self.filter,
            'rangekilometres' : self.rangeKilometres,
            'run' : self.run,
            '' : self.noOp,
            'races' : self.races,
            'bestfit' : self.bestFit,
            }

    def bestFit(self, data, arguments):
        if not self.range:
            print "Define range first"
        else:
            x = []
            y = []
            for activity in self.range.training:
                x.append(activity.date.days)
                y.append(activity.fitness())
            
            #slope, intercept, r, p, stderr = stats.lineregress(x, y)
            
            #print "%.2f Fit/month"%(slope*28)
                        
            
                
            
            
            
    def races(self, data, arguments):
        for race in data.getRaces():
            print
            print race.summaryString()
            endDate = race.date - timedelta(days = 1)
            sixWeeksPrior = endDate - timedelta(days = 1 + (6 * 7))
            twelveWeeksPrior = endDate - timedelta(days = 1 + (12 * 7))
            sixWeeks = data.range(sixWeeksPrior, endDate)
            twelveWeeks = data.range(twelveWeeksPrior, endDate)
            print "6 week lead-up: %.0fkm"%sixWeeks.kilometres()
            print "12 week lead-up: %.0fkm"%twelveWeeks.kilometres()
            print "Race fitness: %.1f"%race.raceFitness()

    def noOp(self, data, arguments):
        return

    def filter(self, data, arguments):
        tag = arguments
        
        self.range = data.filter(tag)
        
    def run(self, data, arguments):
        filename = arguments
        fileStream = open(filename)

        for line in fileStream:
            self.execute(data, line.strip())

    def makeRange(self, data, arguments):
        (startDate, endDate) = arguments.split(' ', 1)

        self.range = data.range(datetime.strptime(startDate, "%Y-%m-%d").date(), datetime.strptime(endDate, "%Y-%m-%d").date())

    def rangeKilometres(self, data, arguments):
        print "%.2fkm"%self.range.kilometres()

    def publishHTML(self, data, arguments):
        usage = "\
Usage: publish <sourceDir> <intermediateDir> <domain> <password>"

        if not " " in arguments:
            self.error(usage)
            return

        (sourceDir, intermediateDir, domain, password) = arguments.split(' ', 3)

        webPublish = WebPublish(sourceDir, intermediateDir, domain, password)

        webPublish.publish()

    def exportData(self, data, arguments):
        usage = "\
Usage: export HTMLCharts <filename>\n\
       export HTMLTemplate <outputDirectory> <templateDirectory>"
        if " " in arguments:
            (type, arguments) = arguments.split(' ', 1)
        else:
            self.error(usage)
            return

        if type == "HTMLCharts":
            filename = arguments
            exporter = WebExporter(filename = filename)
        elif type == "HTMLTemplate":
            if " " in arguments:
                (outputDir, templateDir) = arguments.split(' ', 1)
            else:
                self.error(usage)
                return
            exporter = WebExporter(outputDir = outputDir, templateDir = templateDir)
        else:
            self.error("Type '%s' not recognized"%type)
            self.error(usage)
            return

        exporter.publish(data)

    def weekly(self, data, arguments):
        for week in data.getWeeks():
            print "%s %.2f"%(week.startDate.strftime("%Y-%b-%d"), week.kilometres())

    def dumpData(self, data, arguments):
        print "Data:"
        data.dump()
        print "Range:"
        self.range.dump()

    def continuePrompt(self, text):
        print text
        print "Enter 'yes' to continue or any other input to cancel."
        answer = raw_input()
        return(answer == "yes")

    def importData(self, data, arguments):
        usage = "Usage: import Google/Garmin/GoogleForm/GoogleWeb/Races <filename>"
        if " " in arguments:
            (type, filename) = arguments.split(' ', 1)
        else:
            self.error(usage)
            return

        if type == "Google":
            importer = GoogleImporter(filename)
        elif type == "Garmin":
            importer = GarminImporter(filename)
        elif type == "GoogleForm":
            importer = Importer(filename)
        elif type == "GoogleWeb":
            importer = GoogleWebImporter(filename)
        elif type == "Races":
            importer = RacesImporter(filename)
        else:
            self.error("Type '%s' not recognized"%type)
            self.error(usage)
            return

        if not importer.fileExists():
            self.error("File '%s' not found"%filename)
            self.error(usage)
            return

        #if importer.clashingData(data) and \
        #        not self.continuePrompt("Data clash processing %s.  Overwrite existing data with newly imported data?"%filename):
        #    return;

        importer.loadData(data)

    def help(self, data, arguments):
        for instruction in self.instructions:
            print instruction

    def log(self, text):
        if self.debug:
            print text

    def test(self, data, arguments):
        print data
        print arguments

    def error(self, text):
        print text

    def changeDebug(self, data, arguments):
        yes = [ "True",
                "true",
                "TRUE",
                "Yes",
                "yes",
                "YES",
                "On",
                "on",
                "ON",
                "",
                ];
        no = [ "False",
               "false",
               "FALSE",
               "No",
               "no",
               "NO",
               "Off",
               "off",
               "OFF",
               ];
        if arguments in yes:
            self.debug = True;
        elif arguments in no:
            self.debug = False;
        else:
            self.error("Unrecognized Debug parameter: %s"%arguments)

    def interactive(self, data, arguments):
        while True:
            print(">"),
            line = raw_input()
            self.execute(data, line)

    def exit(self, data, arguments):
        sys.exit()

    def execute(self, data, instruction):
        if " " in instruction:
            (command, arguments) = instruction.split(' ', 1)
        else:
            command = instruction
            arguments = ""

        self.log("instruction = '%s'"%instruction)
        self.log("command = '%s'"%command)
        self.log("arguments = '%s'"%arguments)

        if command.lower() in self.instructions:
            self.instructions[command.lower()](data, arguments)
        else:
            self.error("Command %s not recognized"%command)
