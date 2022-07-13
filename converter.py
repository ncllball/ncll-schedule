import pandas as pd
import math
import csv
import datetime

teams_map = {'NCLL SantoriniDave.com' : 'SantoriniDave.com',
             'NCLL Harjo Construction': 'Harjo Construction',
             'NCLL Dynamite': 'TNT Taqueria Dynamite',
             'NCLL Cheeto Sloths': 'Ballard Pediatric Dentistry Cheeto Sloths',
             'NCLL Lightning Dogs': 'Anytime Fitness Lighting Dogs',
             'NCLL Cube Smart Cats': 'Cube Smart Cats',
             'NCLL/QALL Reignmakers' : 'Windemere Greenwood',
             
             "Ken's Market" : "Ken's Market",
             "Rough Riders" : "Rough Riders",
             "Reuben's Brewers" : "Reuben's Brewers"
             }

other_teams_map = {'NESLL/RUGLL LLC' : 'NESLL/RUGLL Laurelhurst Community Club',
                   'MLL Criminals': 'MLL Washington Alarm'}

def get_team_name(team_name):
    if team_name in teams_map:
        return teams_map[team_name]
    elif team_name in other_teams_map:
        return other_teams_map[team_name]
    return team_name

class Event:
    def __init__(self, away_team, home_team, date, start_time, end_time, location, field):
        self.away_team = away_team
        self.home_team = home_team
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.field = field

def time_str(dt):
    """Time as h:mm without leading zero padding."""
    return f"{dt.hour}:{dt.minute:02}"

def create_csv_from_events(events, filename):
    with open(filename, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Away Team', 'Home Team', 'Date', 'Start Time', 'End Time', 'Location', 'Field'])
        for e in events:
            w.writerow([e.away_team, e.home_team, f'{e.date.month}/{e.date.day}/{e.date.year}', f'{time_str(e.start_time)}', f'{time_str(e.end_time)}', e.location, e.field])

def split_location_and_field(combined_location):
    location = combined_location.strip()
    field = "1"
    s = combined_location.split('#')
    if len(s) == 2:
        location = s[0].strip()
        field = s[1].strip()

    if location == 'Ravenna Park':
        return ('Ravenna', 'Softball Field')
    elif location == 'Ross Playground - Lower':
        return ('Ross Park', 'Lower Ross')
    elif location == 'Ingraham High School - Softball Field':
        return ('Ingram High School', 'Softball Field')

    fields_map = {'Gilman Playfield': 'Gilman',
                  'Magnolia Playfield': 'Magnolia',
                  'Mickey Merriam Playfield': 'Mickey Merriam',
                  'Micky Merriam Park': 'Micky Merriam',
                  'Northacres Park': 'Northacres',
                  'Laurelhurst Playfield': 'Laurelhurst',
                  'Lawton Park': 'Lawton',
                  'Loyal Heights Playfield': 'Loyal Heights',
                  'Lower Woodland Playfield': 'Lower Woodland Cloverleaf',
                  'West Queen Anne Playfield': 'Queen Anne'}
    if location in fields_map:
        location = fields_map[location]
    if location == 'Ballard Community Center' and field == '2':
        field = "2 (West)"
    return (location, "Field " + field)

def get_softball_events(filename):
    df = pd.read_excel(filename)

    events = []
    for row in df.values.tolist():
        if math.isfinite(row[0]):
            away_team = row[6]
            home_team = row[7]
            if away_team in teams_map or home_team in teams_map:
                location, field = split_location_and_field(row[3])
                events.append(Event(get_team_name(away_team),
                       get_team_name(home_team),
                       date = pd.to_datetime(row[2]),
                       start_time = row[4],
                       end_time = row[5],
                       location = location,
                       field = field))
    return events

def get_baseball_location_and_field(combined_location):
    location = combined_location.strip()
    field = "1"
    if location[-1].isdigit():
        field = location[-1]
        location = location[:-1].strip()

    fields_map = {'Bayview Playground (Raye Field)': 'Bayview',
                  'Lower Woodland Park Field': 'Lower Woodland Cloverleaf',
                  'QA': 'Queen Anne',
                  'Shorewood H.S.': 'Shorewood HS',
                  'Soundview Field': 'Soundview'}
    if location in fields_map:
        location = fields_map[location]
    return (location, "Field " + field)

def get_baseball_events(filename):
    df = pd.read_excel(filename)
    events = []
    for row in df.values.tolist():
        if math.isfinite(row[0]):
            away_team = row[4]
            home_team = row[3]
            if away_team in teams_map or home_team in teams_map:
                location, field = get_baseball_location_and_field(row[7])
                events.append(Event(get_team_name(away_team),
                       get_team_name(home_team),
                       date = row[1].to_pydatetime(),
                       start_time = datetime.datetime.strptime(row[12], "%H:%M:%S"),
                       end_time = datetime.datetime.strptime(row[11], "%H:%M:%S"),
                       location = location,
                       field = field))
    return events

if __name__ == '__main__':
    #events = get_softball_events("../../../NCLL/game schedules/NCLL - Majors- RevA.xlsx")
    events = get_baseball_events("../../../NCLL/game schedules/NCLL - Majors- RevA.xlsx")
    create_csv_from_events(events, "baseball_majors.csv")
