import csv
import datetime
import os


def is_home_field(n_location):
    return n_location in ["LW1", "LW3", "LW4", "LW5", "LW6", "Lower Ross", "B.F. Day"]


def get_normalized_location(location):
    if "woodland" in location.lower():
        if location[-1].isdigit():
            return "LW" + location[-1]
        assert false, f"bad location: {location}"
    if "ross" in location.lower():
        return "Lower Ross"
    if "b f day" in location.lower():
        return "B.F. Day"
    return location


def get_normalized_day(day_str):
    return day_str[0:3]


def get_permit_dict(filename):
    """Returns (datetime, field) -> start end time map from permits.

    datetime: datetime object
    field: string in the set {"LW1", "LW3", "LW4", "LW5", "LW6", "Lower Ross", "B.F. Day"}
    start end string: e.g. "05:00 PM - 07:00 PM"
    """
    permit_dict = {}
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            dt = datetime.datetime.strptime(row[0], "%d-%b-%y")
            n_location = get_normalized_location(row[3])
            permit_dict[(dt, n_location)] = row[2]
    return permit_dict


def time_str(dt):
    """Time as h:mm without leading zero padding."""
    return dt.strftime("%H:%M")


def date_str(dt):
    return dt.strftime("%m/%d/%Y")


def create_csv_from_events(events, filename):
    with open(filename, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "Date",
                "Day",
                "Location",
                "Start Time",
                "End Time",
                "Game",
                "Away Team",
                "Home Team",
            ]
        )
        for e in events:
            w.writerow(
                [
                    date_str(e.date),
                    e.day,
                    e.location,
                    time_str(e.start_time),
                    time_str(e.end_time),
                    e.game_number,
                    e.away_team,
                    e.home_team,
                ]
            )


class Event:
    def __init__(
        self,
        date,
        day,
        game_number,
        away_team,
        home_team,
        start_time,
        end_time,
        location,
    ):
        self.date = date
        self.day = day
        self.game_number = game_number
        self.away_team = away_team
        self.home_team = home_team
        self.start_time = start_time
        self.end_time = end_time
        self.location = location


def get_softball_event_from_row(row):
    return Event(
        date=datetime.datetime.strptime(row[2], "%m/%d/%Y"),
        day=get_normalized_day(row[1]),
        game_number=row[0],
        away_team=row[6],
        home_team=row[7],
        start_time=datetime.datetime.strptime(row[4], "%I:%M %p"),
        end_time=datetime.datetime.strptime(row[5], "%I:%M %p"),
        location=get_normalized_location(row[3]),
    )


def get_softball_events(filename):
    events = []
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            if len(row[0]) == 0:
                continue
            event = get_softball_event_from_row(row)
            if "NCLL" in event.away_team or "NCLL" in event.home_team:
                events.append(event)
    return events


def get_baseball_event_from_row(row):
    return Event(
        date=datetime.datetime.strptime(row[1], "%Y-%m-%d"),
        day=get_normalized_day(row[2]),
        game_number=row[0],
        away_team=row[4],
        home_team=row[3],
        start_time=datetime.datetime.strptime(row[12], "%H:%M:%S"),
        end_time=datetime.datetime.strptime(row[11], "%H:%M:%S"),
        location=get_normalized_location(row[7]),
    )


def get_baseball_events(filename):
    events = []
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            event = get_baseball_event_from_row(row)
            events.append(event)
    return events


if __name__ == "__main__":

    permit_dict = get_permit_dict("permits.csv")
    for f in os.listdir("original_games"):
        infile = os.path.join("original_games", f)
        outfile = os.path.join("games", f)
        if "softball" in f:
            events = get_softball_events(infile)
        elif "baseball" in f:
            events = get_baseball_events(infile)
        create_csv_from_events(events, outfile)
