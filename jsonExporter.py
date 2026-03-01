"""
JsonExporter for Dan's training application.
Produces JSON files that can be fetched by static HTML pages.
"""
import json
import io
from datetime import datetime
from .exporter import Exporter

class JsonExporter(Exporter):

    def _activity_to_dict(self, activity):
        return {
            "date": activity.date.isoformat(),
            "distance": activity.distance,
            "time_seconds": int(activity.time.total_seconds()) if hasattr(activity.time, 'total_seconds') else activity.time,
            "notes": activity.notes,
            "heartrate": activity.heartrate,
            "elevation": activity.elevation,
            "raceName": activity.raceName,
            "route": activity.route,
            "shoes": activity.shoes,
            "tags": activity.tags,
        }

    def publish(self, data):
        """Return list of (filename, bytes) tuples ready for upload."""
        payload = {
            "generated": datetime.utcnow().isoformat() + 'Z',
            "summary": {
                "total_distance": data.kilometres(),
                "num_runs": len(data.training)
            },
            "activities": [ self._activity_to_dict(a) for a in data.sorted() ]
        }

        text = json.dumps(payload, indent=2, ensure_ascii=False)
        # Return a single JSON file named data.json
        return [("data.json", text.encode('utf-8'))]
