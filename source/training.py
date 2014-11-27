# Main source file for Dan's training python application
# This application will:
# - Import data from various sources and formats, including exports from Google sheets and Garmin Connect
# - Export/publish to various formats, including Dan's website and internal save formats
# - Provide a UI to interactively import, export, publish and examine data

import sys
from database import Database
from ui import UI

data = Database()

ui = UI(debug = False)

if len(sys.argv) == 1:
    ui.execute(data, "Interactive")

for argument in sys.argv[1:]:
    ui.execute(data, argument)

