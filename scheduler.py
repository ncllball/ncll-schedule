import csv
import os


def create_csv_from_events(events, filename):
    with open(filename, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "Date",
                "Day",
                "Game",
                "Away Team",
                "Home Team",
                "Start Time",
                "End Time",
                "Location",
            ]
        )
        for e in events:
            w.writerow(
                [
                    e.date,
                    e.day,
                    e.game_number,
                    e.away_team,
                    e.home_team,
                    e.start_time,
                    e.end_time,
                    e.location,
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
        date=row[2],
        day=row[1],
        game_number=row[0],
        away_team=row[6],
        home_team=row[7],
        start_time=row[4],
        end_time=row[5],
        location=row[3],
    )


def get_softball_events(filename):
    events = []
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row[0]) == 0:
                continue
            event = get_softball_event_from_row(row)
            if "NCLL" in event.away_team or "NCLL" in event.home_team:
                events.append(event)
    return events


def get_baseball_event_from_row(row):
    return Event(
        date=row[1],
        day=row[2],
        game_number=row[0],
        away_team=row[4],
        home_team=row[3],
        start_time=row[12],
        end_time=row[11],
        location=row[7],
    )


def get_baseball_events(filename):
    events = []
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0].isdigit():
                event = get_baseball_event_from_row(row)
                events.append(event)
    return events


if __name__ == "__main__":
    for f in os.listdir("original_games"):
        infile = os.path.join("original_games", f)
        outfile = os.path.join("games", f)
        if "softball" in f:
            events = get_softball_events(infile)
        elif "baseball" in f:
            events = get_baseball_events(infile)
        create_csv_from_events(events, outfile)
