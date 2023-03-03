Managing North Central Little League permits.

Steps:
1. Get permits excel spreadsheet from Seattle Parks and Rec.
2. Save as permits_from_parks.csv. (comma separated, UTF-8). The diff isn't that great because although they sort by date, the field order is random.
3. run process_parks_permits.py permits_from_parks.csv. This creates 2 files:
  * permits_60ft.csv.
  * permits_90ft.csv. Give this to whoever is scheduling 90ft fields.
4. Look at git diff of permits_60ft.csv make sure changes are reasonable.
5. Merge permits_60ft.csv into assigned_permits_60ft.csv.
6. Update assigned_permits_60ft.csv as necessary.
7. Commit changes.
