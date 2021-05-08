# GoogleImporter for Dan's training application.
# This contains specific functions for importing data from a Google .csv export.

import os
import csv

from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

from .importer import Importer
from .database import Database
from .activity import Activity

class CsvImporter(Importer):

    def loadData(self, data):
        super(CsvImporter, self).loadData(data)
        return
