# Code Walkthrough: process_permits_from_parks.py

This document provides a detailed walkthrough of how the permit processing script works.

## Purpose
Converts Seattle Parks permit data into separate CSV files for 60ft and 90ft baseball fields, making it easier to manage field scheduling for North City Little League.

## Code Structure

### 1. Field Name Mappings (Lines 7-38)
```python
fields = {
    "Bitter Lake Playfield Ballfield 01": "bitter lake 1",
    "Lower Woodland Playfield Ballfield 01": "lw1",
    ...
}
```
**What it does:** Creates a dictionary mapping long official Seattle Parks field names to shorter, more manageable names for internal use.

### 2. Day Abbreviations (Lines 40-48)
```python
days = {
    "Monday": "Mon",
    "Tuesday": "Tue",
    ...
}
```
**What it does:** Maps full day names to 3-letter abbreviations for cleaner CSV output.

### 3. Date Formatting Functions

#### `sortable_date_format()` (Lines 51-57)
```python
def sortable_date_format(date_string):
    """April 6, 2023 → 04/06"""
    return datetime.datetime.strptime(date_string, "%b %d, %Y").strftime("%m/%d")
```
**What it does:** Converts dates from "Apr 6, 2023" format to "04/06" for proper chronological sorting.

#### `csv_date_format()` (Lines 60-66)
```python
def csv_date_format(date_string):
    """Apr 6, 2023 → 6-Apr"""
    dt = datetime.datetime.strptime(date_string, "%b %d, %Y")
    return f"{dt.day}-{dt.strftime('%b')}"
```
**What it does:** Formats dates as "6-Apr" to prevent Excel from auto-converting them to its own date format.

### 4. Field Classification (Lines 69-76)
```python
def is_90ft_field(field_name):
    return fields[field_name] in (
        eagle_staff_90,
        ingraham,
        lw1,
        whitman,
        loyal_heights_1,
        view_ridge_1,
    )
```
**What it does:** Determines if a field is a 90ft baseball field. Only 6 specific fields are 90ft; all others are 60ft.

### 5. Data Reading and Sorting (Lines 79-86)
```python
def get_rows(permits_filename):
    with open(permits_filename, "r", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows[0:1] + sorted(
        rows[1:], key=lambda x: (sortable_date_format(x[0]), x[4])
    )
```
**What it does:** 
1. Reads the CSV file
2. Preserves the header row (row 0)
3. Sorts data rows by date (column 0) and field name (column 4)

### 6. Creating 60ft Fields File (Lines 89-107)
```python
def create_60ft_fields_csvfile(csv_rows, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(
            ["Date", "Day", "Permit", "Field", "Start time", "End time", "Home", "Away"]
        )
        for row in csv_rows[1:]:
            field_name = row[4]
            if not is_90ft_field(field_name):
                writer.writerow([...])
```
**What it does:**
1. Creates a new CSV with custom headers for game scheduling
2. Filters to only include 60ft fields
3. Reformats data with:
   - Excel-safe date format
   - Day abbreviations
   - Simplified field names
   - Empty columns for game details (to be filled manually)

### 7. Creating 90ft Fields File (Lines 110-117)
```python
def create_90ft_fields_csvfile(csv_rows, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(csv_rows[0])
        for row in csv_rows[1:]:
            field_name = row[4]
            if is_90ft_field(field_name):
                writer.writerow(row)
```
**What it does:**
1. Creates a CSV for 90ft fields
2. Preserves the original format and headers
3. Filters to only include the 6 designated 90ft fields

### 8. Main Execution (Lines 120-123)
```python
if __name__ == "__main__":
    csv_rows = get_rows("permits_from_parks_summer.csv")
    create_60ft_fields_csvfile(csv_rows, "permits_60ft_summer.csv")
    create_90ft_fields_csvfile(csv_rows, "permits_90ft_summer.csv")
```
**What it does:**
1. Loads and sorts the permit data
2. Creates the 60ft fields file with reformatted data
3. Creates the 90ft fields file with filtered original data

## Data Flow

```
permits_from_parks_summer.csv
            ↓
     [Read & Sort]
            ↓
        /       \
       /         \
[Filter 60ft]  [Filter 90ft]
      ↓              ↓
[Reformat]    [Keep Original]
      ↓              ↓
permits_60ft    permits_90ft
_summer.csv     _summer.csv
```

## Expected Input Format

The script expects the input CSV to have:
- Column 0: Date (e.g., "Apr 6, 2023")
- Column 1: Day name (e.g., "Monday")
- Column 3: Permit number
- Column 4: Official field name

## Output Files

**60ft fields:** Reformatted with scheduling columns added  
**90ft fields:** Original format, filtered to specific fields

## Error Handling

Note: The script assumes:
- Input file exists in the same directory
- All field names in the input match the predefined mapping
- Date format is consistent ("MMM D, YYYY")

Consider adding error handling for production use.
