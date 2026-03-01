"""
Main source file for Dan's training python application
"""

import sys
from .database import Database
from .ui import UI

data = Database()

ui = UI(debug = False)

if len(sys.argv) == 1:
    ui.execute(data, "Interactive")

for argument in sys.argv[1:]:
    ui.execute(data, argument)
