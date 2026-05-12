import sys
import os
import tempfile
from getpass import getpass
import pandas as pd
from datetime import datetime, date, timedelta
import requests
from garminconnect import Garmin
import re
import csv

def seconds_to_hms(seconds):
    try:
        seconds = int(seconds)
    except Exception:
        return "0:00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}:{m:02d}:{s:02d}"


def extract_route_from_title(title):
    if pd.isna(title):
        return "Unknown"
    route = str(title).replace(" Running", "").strip()
    if "treadmill" in str(title).lower():
        return "Treadmill"
    if "track" in str(title).lower():
        return "Track"
    return route

def fetch_activities(email, password, start_date, end_date):
    api = Garmin(email, password)
    api.login()
    activities = api.get_activities_by_date(start_date, end_date)
    rows = []
    for act in activities:
        data = act
        if not all(k in data for k in ('distance', 'startTimeLocal', 'duration')):
            try:
                aid = data.get('activityId') or data.get('activity_id') or data.get('id')
                if aid:
                    data = api.get_activity_details(aid)
            except Exception:
                pass
        start_time = data.get('startTimeLocal') or data.get('startTime') or data.get('startTimestamp')
        if isinstance(start_time, (int, float)):
            start_time = datetime.fromtimestamp(int(start_time)).strftime('%Y-%m-%d %H:%M:%S')
        dist_m = data.get('distance') or data.get('distanceMeters') or data.get('distanceInMeters') or 0
        try:
            dist_km = float(dist_m) / 1000.0
        except Exception:
            dist_km = 0.0
        duration = data.get('duration') or data.get('movingDuration') or data.get('moving_time') or 0
        avg_hr = data.get('averageHR') or data.get('avgHR') or data.get('average_heart_rate') or ''
        ascent = data.get('elevationGain') or data.get('totalAscent') or data.get('elevation') or 0
        title = data.get('activityName') or data.get('name') or ''
        date_only = ''
        if start_time:
            try:
                date_only = datetime.fromisoformat(start_time.split('.')[0]).strftime('%Y-%m-%d')
            except Exception:
                try:
                    date_only = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                except Exception:
                    date_only = str(start_time).split(' ')[0]
        rows.append({
            'Date': date_only,
            'Distance': f"{dist_km:.3f}",
            'Moving Time': seconds_to_hms(duration),
            'Title': title,
            'Avg HR': avg_hr,
            'Total Ascent': ascent
        })
    return(rows)

def upload_activities(data, api_url, submit_password):
    for row in data:
        payload = {
            'date': row['Date'],
            'distance': row['Distance'],
            'hours': row['Moving Time'].split(':')[0],
            'minutes': row['Moving Time'].split(':')[1],
            'seconds': row['Moving Time'].split(':')[2],
            'location': extract_route_from_title(row['Title']),
            'notes': 'Easy',
            'heartrate': row['Avg HR'] if row['Avg HR'] else 0,
            'climb': row['Total Ascent'] if row['Total Ascent'] else 0,
            'password': submit_password,
            'action': 'run'
        }
        response = requests.post(api_url, json=payload)
        print(response)

def find_first_run_gap():
    response = requests.get("https://danieltebbuttstorage.blob.core.windows.net/$web/data.json")
    data = response.json()
    dates_in_2026 = [ row["date"] for row in data["activities"] if row["date"] >= "2026" ]
    cur_day = datetime(2026, 1, 1)
    while cur_day.strftime("%Y-%m-%d") in dates_in_2026:
        cur_day += timedelta(days = 1)
    return(cur_day)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fetch Garmin activities and submit to website')
    parser.add_argument('--email', help='Garmin account email', required=True)
    parser.add_argument('--api', help='API to submit to', required=True)
    parser.add_argument('--submitpw', help='Password to use with submit', required=True)

    args = parser.parse_args()
    password = getpass('Garmin password: ')
    start = find_first_run_gap().strftime("%Y-%m-%d")
    end = datetime.today().strftime("%Y-%m-%d")
    email = args.email
    
    data = fetch_activities(email, password, start, end)
    upload_activities(data, args.api, args.submitpw)

if __name__ == '__main__':
    main()
