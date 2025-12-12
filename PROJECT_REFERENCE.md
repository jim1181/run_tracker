Strava Running Dashboard – Project Reference
1️⃣ Architecture Overview
Component	Role	Notes / Links
Google Sheet (strava_datapull)	Holds Strava run data	Updated hourly; currently focused on December 2025; historical runs stored in separate tab or sheet
Google Apps Script	Pulls data from Strava API	- Handles token refresh
- Currently clears & writes new data; to be amended to append new runs
- Scheduled hourly via time-based trigger
Google Cloud / API	Service account authentication	Keys stored in Streamlit Secrets; Sheets & Drive API enabled; free account sufficient
Streamlit App (Run_tracker_v3.py)	Dashboard	Pulls December data from Sheet; plots cumulative, daily, target vs actual; live updating
Streamlit Secrets	Holds service account JSON	Provides secure authentication; JSON file not stored in GitHub
GitHub	Version control for code	Stores Python + Apps Script; do not store secrets or JSON
2️⃣ Current Data Flow

Strava → Google Apps Script → Google Sheet

Apps Script calls Strava API, refreshes token, pulls runs.

Currently clears sheet, then writes latest runs.

Scheduled hourly for near-real-time updates.

Google Sheet → Streamlit Dashboard

Streamlit app authenticates using service account from secrets.

Reads sheet (filtered to December 2025).

Plots cumulative, daily planned, target vs actual distances.

3️⃣ Next Steps & Tasks
Step 1: One-time historical data pull

Goal: Populate Google Sheet with all historical runs.

Method:

Modify fetchStravaActivities in Apps Script to accept a month range (start/end dates).

Pull month by month to avoid truncation (~200 activity limit per request).

Append to a historical sheet or tab in the same spreadsheet.

Step 2: Incremental updates

Goal: Hourly script only adds new runs.

Method:

Track latest date in sheet.

Request only runs after that date from Strava.

Append new rows instead of clearing the sheet.

Trigger: Keep hourly time-based trigger.

Step 3: Streamlit dashboard adjustments

Goal: Dashboard shows only December 2025 data.

Method:

actual_df = actual_df[actual_df["Date"].dt.month == 12]
actual_df = actual_df[actual_df["Date"].dt.year == 2025]


Optional: Add manual refresh button or caching (st.cache_data(ttl=60)) for near-live updates.

Step 4: Architecture / component summary

Google Sheet: Data store (live + historical).

Google Apps Script: Strava API → Sheet; handles token refresh; hourly trigger.

Streamlit app: Dashboard; reads Sheet via service account; live updates for December 2025.

Streamlit Secrets: Securely store JSON credentials.

GitHub: Version control for code, not secrets.

Step 5: Optional enhancements

Filter dashboard by other months/years.

Add historical summary charts using full history sheet.

Cache Sheet reads in Streamlit to avoid excessive API calls.

4️⃣ Recommended Sequence for Implementation

Pull historical Strava data month-by-month into Sheet.

Update Apps Script to append only new runs for hourly updates.

Adjust Streamlit dashboard to filter December 2025.

Verify live updates and caching.

Document architecture and workflow for reference.

5️⃣ Apps Script trigger snippet (hourly)
function scheduleHourlyUpdate() {
  ScriptApp.newTrigger("updateSheetIncremental")
    .timeBased()
    .everyHours(1)
    .create();
}


Run scheduleHourlyUpdate() once manually to enable automatic hourly pulls.

6️⃣ Notes / Best Practices

Do not store JSON credentials in GitHub; use Streamlit Secrets.

Verify service account has Editor access to Google Sheet.

Use full Drive + Sheets API scopes for listing sheets & robust access:

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


Dashboard refresh is on user rerun or via caching TTL; hourly Apps Script trigger ensures Sheet is up to date.
