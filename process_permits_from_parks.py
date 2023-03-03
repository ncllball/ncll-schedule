# convert permits*.csv to
# 1. 60ft_fields.csv
# 2. 90ft_fields.csv
import datetime
import sys
import csv

lw1 = "lw1"
whitman = "whitman"
loyal_heights_1 = "loyal heights 1"
eagle_staff_90 = "eagle staff 90"
green_lake_1 = "green lake 1"

fields = {
    "Bitter Lake Playfield Ballfield 01": "bitter lake 1",
    "Bitter Lake Playfield Ballfield 02": "bitter lake 2",
    "B F Day Playfield Ballfield": "bfday",
    "Eagle Staff Middle School Baseball Field": eagle_staff_90,
    "Eagle Staff Middle School Softball Field": "eagle staff 60",
    "Green Lake Playfield Ballfield 01": green_lake_1,
    "Lower Woodland Playfield Ballfield 01": lw1,
    "Lower Woodland Playfield Ballfield 03": "lw3",
    "Lower Woodland Playfield Ballfield 04": "lw4",
    "Lower Woodland Playfield Ballfield 05": "lw5",
    "Lower Woodland Playfield Ballfield 06": "lw6",
    "Northacres Park Ballfield 02": "northacres 2",
    "Loyal Heights Playfield Ballfield 01": loyal_heights_1,
    "Ross Playfield Lower Ballfield": "ross",
    "University Playfield Ballfield 01": "university",
    "Whitman Middle School Baseball": whitman,
}

days = {
    "Monday": "Mon",
    "Tuesday": "Tue",
    "Wednesday": "Wed",
    "Thursday": "Thu",
    "Friday": "Fri",
    "Saturday": "Sat",
    "Sunday": "Sun",
}


def sortable_date_format(date_string):
    """Suitable for sorting.

    >>> sortable_date_format("April 6, 2023")
    "04/06"
    """
    return datetime.datetime.strptime(date_string, "%b %d, %Y").strftime("%m/%d")


def csv_date_format(date_string):
    """Date that excel won't reformat.

    >>> csv_date_format("Apr 6, 2023")
    "6-Apr"
    """
    dt = datetime.datetime.strptime(date_string, "%b %d, %Y")
    return f"{dt.day}-{dt.strftime('%b')}"


def is_90ft_field(field_name):
    return fields[field_name] in (eagle_staff_90, lw1, whitman, loyal_heights_1)


def get_rows(permits_filename):
    with open(permits_filename, "r", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows[0:1] + sorted(
        rows[1:], key=lambda x: (sortable_date_format(x[0]), x[4])
    )


def create_60ft_fields_csvfile(csv_rows, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(
            ["Date", "Day", "Permit", "Field", "Start time", "End time", "Home", "Away"]
        )
        for row in csv_rows[1:]:
            field_name = row[4]
            if not is_90ft_field(field_name):
                writer.writerow(
                    [
                        csv_date_format(row[0]),
                        days[row[1]],
                        row[3],
                        fields[row[4]],
                        "",
                        "",
                        "",
                        "",
                    ]
                )


def create_90ft_fields_csvfile(csv_rows, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(csv_rows[0])
        for row in csv_rows[1:]:
            field_name = row[4]
            if is_90ft_field(field_name):
                writer.writerow(row)


if __name__ == "__main__":
    csv_rows = get_rows("permits_from_parks.csv")
    create_60ft_fields_csvfile(csv_rows, "permits_60ft.csv")
    create_90ft_fields_csvfile(csv_rows, "permits_90ft.csv")