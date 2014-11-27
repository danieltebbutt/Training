# Exporter for Dan's training application.
# This contains generic functions for exporting data and is extended by other classes.

import os
from database import Database

class Exporter:

    SINGLE = 1
    TEMPLATE = 2

    def __init__(self, filename = "", outputDir = "", templateDir = ""):
        self.filename = filename
        self.outputDir = outputDir
        self.templateDir = templateDir
        if not self.filename == "":
            self.type = self.SINGLE
        else:
            self.type = self.TEMPLATE

    def publish(self, data):
        print "Error! publish not over-ridden"
        return
                    
        