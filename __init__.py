import logging

from azure.storage.blob import BlobServiceClient, ContentSettings
import azure.functions as func

import re
import os
import pathlib

from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

from .importer import Importer
from .csvImporter import CsvImporter
from .database import Database
from .activity import Activity
from .csvExporter import CsvExporter
from .jsonExporter import JsonExporter

def get_param(req, name, default = None):
    val = req.params.get(name)
    if not val:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            val = req_body.get(name)
    if not val and default != None:
        val = default
    return val

def main(req: func.HttpRequest, inputblob: bytes, outputblob: func.Out[bytes], runlog: func.Out[bytes]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    password = get_param(req, 'password', '')
    if password != 'excellentbornchildproperty':
         return func.HttpResponse("invalid password")

    distance = float(get_param(req, 'distance','0'))
    hours = int(get_param(req, 'hours', 0))
    minutes = int(get_param(req, 'minutes', 0))
    seconds = int(get_param(req, 'seconds', 0))
    time = timedelta(seconds = seconds, minutes = minutes, hours = hours)
    heartrate = int(get_param(req, 'heartrate', '0'))
    location = get_param(req, 'location', '')
    notes = get_param(req, 'notes', '')
    if distance:
        date = datetime.strptime(get_param(req, 'date'), '%Y-%m-%d').date()
    climb = int(get_param(req, 'climb', '0'))
    raceName = get_param(req, 'racename', '')
    if raceName == 'None':
        raceName = ''
    test = (get_param(req, 'test', 'off') == 'on')
    shoes = get_param(req, 'shoes', '')

    data = Database()
    importer = CsvImporter(inputStream = inputblob)
    importer.loadData(data)

    if distance:
        if not hours and not minutes and not seconds:
            return func.HttpResponse("invalid time")

        activity = Activity(date, distance, time, notes, heartrate, climb, location, raceName, shoes)

        data.addActivity(activity)

    exporter = CsvExporter()

    if not test:
        outputblob.set(exporter.publish(data))
    else:
        text = exporter.publish(data)

    # News publishing removed per refactor: no-op for runlog

    summary = "https://www.danieltebbutt.com/fitness.html"

    # Publish JSON data files instead of HTML templates
    exporter = JsonExporter()
    to_upload = exporter.publish(data)

    if not test:
        connect_str = os.getenv('blobconnection')
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        for upload in to_upload:
            blob_client = blob_service_client.get_blob_client(container="$web", blob=upload[0])
            blob_client.upload_blob(upload[1], overwrite=True, content_settings=ContentSettings(content_type='application/json'))

    return func.HttpResponse(summary, status_code=302, headers = {"Location" : "https://www.danieltebbutt.com/fitness.html"})
