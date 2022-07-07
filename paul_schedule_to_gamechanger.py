# Convert Paul's summer ball schedule to sportsengine format.
import csv
import sys

new_csv_headers = [
    "Start_Date",
    "Start_Time",
    "End_Date",
    "End_Time",
    "Title",
    "Description",
    "Location",
    "Location_URL",
    "Location_Details",
    "All_Day_Event",
    "Event_Type",
    "Tags",
    "Team1_ID",
    "Team1_Division_ID",
    "Team1_Is_Home",
    "Team2_ID",
    "Team2_Division_ID",
    "Team2_Name",
    "Custom_Opponent",
    "Event_ID",
    "Game_ID",
    "Affects_Standings",
    "Points_Win",
    "Points_Loss",
    "Points_Tie",
    "Points_OT_Win",
    "Points_OT_Loss",
    "Division_Override",
]


def get_location(old_row):
    old_location = old_row[9]
    old_field_num = old_row[10]
    if old_location == "Ross Playfield Lower Ballfield":
        return "Lower Ross"
    elif old_location[0:3] == "BYE":
        return "BYE"

    return old_location + " " + str(old_field_num)


def get_old_home_team(old_row):
    return old_row[12]


def get_old_away_team(old_row):
    return old_row[13]


def is_row_ncll(old_row):
    return "NC-" in get_old_home_team(old_row) or "NC-" in get_old_away_team(old_row)


def convert_row(old_row):
    """convert old row list into new spreadsheet row"""
    l = [""] * len(new_csv_headers)

    l[0] = old_row[3]  # Start_Date
    l[1] = old_row[6]  # Start_Time
    l[2] = old_row[3]  # End_Date
    l[3] = old_row[7]  # End_Time
    l[4] = "Game"  # Title
    l[6] = get_location(old_row)  # Location
    l[10] = "Game"  # Event Type
    old_home_team = get_old_home_team(old_row)
    old_away_team = get_old_away_team(old_row)
    if "NC-" in old_home_team:
        l[12] = old_home_team  # Team 1 ID
        l[14] = "1"  # Team 1 is home
        l[15] = old_away_team  # Team 2 ID
    else:
        assert "NC-" in old_away_team
        l[12] = old_away_team  # Team 1 ID
        l[14] = ""  # Team 1 is home
        l[15] = old_home_team  # Team 2 ID

    # If away team isn't a valid team id, move it to the Team 2 Name field.
    if "NC-" not in l[15]:
        l[17] = l[15]
        l[15] = ""

    return l


new_rows = []

with open(sys.argv[1], newline="") as f:
    reader = csv.reader(f)
    next(reader)  # Ignore the first row
    for old_row in reader:
        if is_row_ncll(old_row):
            new_rows.append(convert_row(old_row))

with open("sportsengine_schedule.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(new_csv_headers)

    for new_row in new_rows:
        writer.writerow(new_row)
