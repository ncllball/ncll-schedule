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


def get_permit_dict(filename, start_date, end_date):
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
            if dt < start_date or dt > end_date:
                continue
            if row[1] in ["Friday", "Sunday"]:
                continue
            n_location = get_normalized_location(row[3])
            permit_dict[(dt, n_location)] = row[2]
    return permit_dict


def set_event_permits(events, permit_dict):
    for e in events:
        if is_home_field(e.location):
            key = (e.date, e.location)
            if key in permit_dict:
                e.permit = permit_dict[key]
            else:
                e.permit = "XXXXXXXX"
                print(
                    f"No permit for {e.date}, {e.location}, {e.away_team}, {e.home_team}"
                )


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
                "Permit",
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
                    e.permit,
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
        permit,
    ):
        self.date = date
        self.day = day
        self.game_number = game_number
        self.away_team = away_team
        self.home_team = home_team
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.permit = permit


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
        permit="",
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
        permit="",
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


def get_practices_to_add(all_game_events, team_lists, dates):
    practices_to_add = []
    for dt in dates:
        events_with_date = [e for e in all_game_events if e.date == dt]
        for team_list in team_lists:
            for team in team_list:
                team_has_event = False
                for e in events_with_date:
                    if e.away_team == team or e.home_team == team:
                        team_has_event = True
                        break
                if not team_has_event:
                    practices_to_add.append(
                        Event(
                            date=dt,
                            day="",
                            game_number="",
                            away_team="",
                            home_team=team,
                            start_time=dt,
                            end_time=dt,
                            location="",
                            permit="",
                        )
                    )
    return practices_to_add


def backfill_with_practices(all_game_events):

    baseball_majors_teams = ["Ken's Market", "Reuben's Brewers", "Rough Riders"]
    baseball_aaa_teams = [
        "TNT Taqueria",
        "Morgan's Plumbing",
        "Seattle Stained Glass",
        "Greenwood Hardware",
    ]
    softball_majors_teams = ["NCLL/QALL Reignmakers"]
    softball_aaa_teams = [
        "NCLL Harjo Construction",
        "NCLL SantoriniDave.com",
        "NCLL Dynamite",
    ]
    softball_aa_teams = [
        "NCLL Cheeto Sloths",
        "NCLL Cube Smart Cats",
        "NCLL Lightning Dogs",
    ]
    softball_a_teams = [
        "NCLL Bluebirds",
        "NCLL Koalas",
        "NCLL Purple",
    ]

    practices_to_add = []
    # Mondays
    practices_to_add.extend(
        get_practices_to_add(
            all_game_events,
            [softball_majors_teams, baseball_aaa_teams],
            [
                datetime.datetime(2021, 4, 19),
                datetime.datetime(2021, 4, 26),
                datetime.datetime(2021, 5, 3),
                datetime.datetime(2021, 5, 10),
                datetime.datetime(2021, 5, 17),
                datetime.datetime(2021, 5, 24),
            ],
        )
    )
    # Tuesdays
    practices_to_add.extend(
        get_practices_to_add(
            all_game_events,
            [baseball_majors_teams, softball_aaa_teams, softball_a_teams],
            [
                datetime.datetime(2021, 4, 20),
                datetime.datetime(2021, 4, 27),
                datetime.datetime(2021, 5, 4),
                datetime.datetime(2021, 5, 11),
                datetime.datetime(2021, 5, 18),
                datetime.datetime(2021, 5, 25),
            ],
        )
    )
    # Wednesdays
    practices_to_add.extend(
        get_practices_to_add(
            all_game_events,
            [softball_majors_teams, baseball_aaa_teams, softball_aa_teams],
            [
                datetime.datetime(2021, 4, 21),
                datetime.datetime(2021, 4, 28),
                datetime.datetime(2021, 5, 5),
                datetime.datetime(2021, 5, 12),
                datetime.datetime(2021, 5, 19),
                datetime.datetime(2021, 5, 26),
            ],
        )
    )
    # Thursdays
    practices_to_add.extend(
        get_practices_to_add(
            all_game_events,
            [baseball_majors_teams, softball_aaa_teams],
            [
                datetime.datetime(2021, 4, 22),
                datetime.datetime(2021, 4, 29),
                datetime.datetime(2021, 5, 6),
                datetime.datetime(2021, 5, 13),
                datetime.datetime(2021, 5, 20),
                datetime.datetime(2021, 5, 27),
            ],
        )
    )
    # Saturdays
    practices_to_add.extend(
        get_practices_to_add(
            all_game_events,
            [
                baseball_majors_teams,
                baseball_aaa_teams,
                softball_aaa_teams,
                softball_aa_teams,
                softball_a_teams,
            ],
            [
                datetime.datetime(2021, 4, 24),
                datetime.datetime(2021, 5, 1),
                datetime.datetime(2021, 5, 8),
                datetime.datetime(2021, 5, 15),
                datetime.datetime(2021, 5, 22),
            ],
        )
    )

    return all_game_events + practices_to_add


def backfill_permits(all_events, permit_dict):
    permit_events_to_add = []
    for key, items in permit_dict.items():
        dt, location = key
        if location == "LW1" or location == "B.F. Day":
            continue
        found_one = False
        for e in all_events:
            if e.date == dt and e.location == location:
                found_one = True
                break
        if not found_one:
            permit_events_to_add.append(
                Event(
                    date=dt,
                    day="",
                    game_number="",
                    away_team="",
                    home_team="",
                    start_time=dt,
                    end_time=dt,
                    location=location,
                    permit=items,
                )
            )
    return all_events + permit_events_to_add


if __name__ == "__main__":

    start_date = datetime.datetime(2021, 4, 19)
    end_date = datetime.datetime(2021, 5, 28)

    all_game_events = []
    for f in os.listdir("original_games"):
        infile = os.path.join("original_games", f)
        outfile = os.path.join("games", f)
        if "softball" in f:
            events = get_softball_events(infile)
        elif "baseball" in f:
            events = get_baseball_events(infile)
        all_game_events.extend(events)
        create_csv_from_events(events, outfile)

    # only look at ones we care about.
    all_game_events = [
        e for e in all_game_events if e.date >= start_date and e.date <= end_date
    ]
    permit_dict = get_permit_dict("permits.csv", start_date, end_date)
    set_event_permits(all_game_events, permit_dict)

    all_events = backfill_with_practices(all_game_events)

    all_events_and_available_permits = backfill_permits(all_events, permit_dict)

    all_events_and_available_permits.sort(
        key=lambda x: (x.date, x.location, x.start_time)
    )

    create_csv_from_events(all_events_and_available_permits, "all_events.csv")
