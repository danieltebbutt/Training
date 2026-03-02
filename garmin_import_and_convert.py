import sys
import os
import tempfile
from getpass import getpass
import pandas as pd
from datetime import datetime, date

try:
    from garminconnect import Garmin
except Exception as e:
    Garmin = None


def seconds_to_hms(seconds):
    try:
        seconds = int(seconds)
    except Exception:
        return "0:00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}:{m:02d}:{s:02d}"


# --- BEGIN converted code from garmin-csv-converter.py (slightly refactored) ---
import re
import csv


def extract_route_from_title(title):
    if pd.isna(title):
        return "Unknown"
    route = str(title).replace(" Running", "").strip()
    if "treadmill" in str(title).lower():
        return "Treadmill"
    if "track" in str(title).lower():
        return "Track"
    return route


def format_time(time_str):
    if pd.isna(time_str):
        return "0:00:00"
    if isinstance(time_str, (int, float)):
        return seconds_to_hms(time_str)
    if time_str.startswith("00:"):
        return "0:" + time_str[3:]
    return time_str


def convert_garmin_to_output_format(garmin_file, output_file, start_date=None, end_date=None):
    garmin_df = pd.read_csv(garmin_file)
    garmin_df['Date_parsed'] = pd.to_datetime(garmin_df['Date'])
    garmin_df['Date_only'] = garmin_df['Date_parsed'].dt.date
    output_data = []
    for _, row in garmin_df.iterrows():
        distance = round(float(row['Distance']), 1)
        output_row = {
            'Date': row['Date_only'].strftime('%Y-%m-%d'),
            'Distance': f"{distance:.1f}",
            'Time': format_time(row['Moving Time']),
            'Notes': 'Easy',
            'Heartrate': 0 if 'treadmill' in str(row['Title']).lower() else int(row['Avg HR']) if pd.notna(row['Avg HR']) else 0,
            'Elevation gain': int(row['Total Ascent']) if pd.notna(row['Total Ascent']) else 0,
            'Race name': '',
            'Route': extract_route_from_title(row['Title']),
            'Shoes': ''
        }
        if not start_date or pd.to_datetime(output_row['Date']) >= pd.to_datetime(start_date):
            output_data.append(output_row)
    output_df = pd.DataFrame(output_data)
    if output_df.empty:
        print("No activities to convert.")
        return output_df
    output_df['Date'] = pd.to_datetime(output_df['Date'])
    if start_date and end_date:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        all_dates = pd.date_range(start=start, end=end, freq='D')
        existing_dates = set(output_df['Date'].dt.date)
        for d in all_dates:
            if d.date() not in existing_dates:
                guessed_row = {
                    'Date': d,
                    'Distance': '3.0',
                    'Time': '0:18:00',
                    'Notes': 'Easy (guessed - no Garmin data)',
                    'Heartrate': 0,
                    'Elevation gain': 0,
                    'Race name': '',
                    'Route': 'Treadmill',
                    'Shoes': ''
                }
                output_df = pd.concat([output_df, pd.DataFrame([guessed_row])], ignore_index=True)
    output_df = output_df.sort_values('Date')
    output_df['Date'] = output_df['Date'].dt.strftime('%Y-%m-%d')
    column_order = ['Date', 'Distance', 'Time', 'Notes', 'Heartrate', 'Elevation gain', 'Race name', 'Route', 'Shoes']
    output_df = output_df[column_order]
    with open(output_file, 'w', newline='') as f:
        f.write('Date,Distance,Time,Notes,Heartrate,Elevation gain,Race name,Route,Shoes\n')
        for _, row in output_df.iterrows():
            line = f'{row["Date"]},{row["Distance"]},{row["Time"]},'
            line += f'"{row["Notes"]}",{row["Heartrate"]},{row["Elevation gain"]},'
            line += f'{row["Race name"]},"{row["Route"]}",""\n'
            f.write(line)
    print(f"Conversion complete! Output saved to {output_file}")
    print(f"Total activities: {len(output_df)}")
    print(f"Date range: {output_df['Date'].min()} to {output_df['Date'].max()}")
    return output_df


def fetch_activities_to_csv(email, password, start_date, end_date, csv_path):
    if Garmin is None:
        raise RuntimeError('garminconnect is not installed or could not be imported')
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
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    return csv_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fetch Garmin activities and convert to target CSV')
    parser.add_argument('--email', help='Garmin account email')
    parser.add_argument('--output', help='Output CSV path', required=True)
    parser.add_argument('--start', help='Start date YYYY-MM-DD', required=True)
    parser.add_argument('--end', help='End date YYYY-MM-DD', required=True)
    args = parser.parse_args()
    email = args.email or input('Garmin email: ')
    password = getpass('Garmin password: ')
    start = args.start
    end = args.end
    tmp = os.path.join(tempfile.gettempdir(), 'garmin_export_temp.csv')
    try:
        print('Fetching activities...')
        fetch_activities_to_csv(email, password, start, end, tmp)
    except Exception as e:
        print('Failed to fetch activities:', e)
        sys.exit(1)
    print('Converting to desired output format...')
    convert_garmin_to_output_format(tmp, args.output, start, end)


if __name__ == '__main__':
    main()
