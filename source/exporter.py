# Exporter for Dan's training application.
# This contains generic functions for exporting data and is extended by other classes.

import os
from .database import Database

class Exporter:

    SINGLE = 1
    TEMPLATE = 2

    def __init__(self, filename = "", outputDir = "", templateDir = ""):
        self.filename = filename
        self.outputDir = outputDir
        self.templateDir = templateDir
        if self.templateDir != "":
            self.type = self.TEMPLATE
        else:
            self.type = self.SINGLE

    def publish(self, data):
        print("Error! publish not over-ridden")
        return
                    
        