Managing North Central Little League permits.

Steps:
1. Get permits excel spreadsheet from Seattle Parks and Rec.
2. Save as parks_permits_yyyy_etc_as_of_mmm_dd.csv. (comma separated, UTF-8)
3. run process_parks_permits.py parks_permits_yyyy_etc_as_of_mmm_dd.csv. This creates 2 files:
  * permits_60ft.csv.
  * permits_90ft.csv. Give this to whoever is scheduling 90ft fields.
4. Look at changes to permits_60ft.csv in git diff to make sure they are reasonable.
5. Merge permits_60ft.csv into assigned_permits_60ft.csv.
6. Update assigned_permits_60ft.csv as necessary.
