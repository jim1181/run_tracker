# streamlit_app.py

import streamlit as st
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>December Running Dashboard V2</h1>", unsafe_allow_html=True)

# Create three columns: left padding, main content, right padding
col_left, col_main, col_right = st.columns([1, 4, 1])

# Google Sheets setup
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Credentials for Google cleint - Try Streamlit first, if not use local.
try:
    creds_dict = st.secrets["google"]
    st.write("Using Cloud secrets")
except:
    with open("service_account.json") as f:
        creds_dict = json.load(f)
    st.write("Using local JSON credentials")

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open the sheet
sheet = client.open("strava_datapull").sheet1

# Get all rows
data = sheet.get_all_values()

# Convert to DataFrame
df = pd.DataFrame(data[1:], columns=data[0])

# Extract only date + distance (A and C)
actual_df = df[["Date", "Distance_km"]].copy()

# Convert types
actual_df["Date"] = pd.to_datetime(actual_df["Date"])
actual_df["Distance_km"] = pd.to_numeric(actual_df["Distance_km"], errors="coerce")

# Rename to match the rest of your app
actual_df = actual_df.rename(columns={
    "Date": "date",
    "Distance_km": "km"
})

# Sort
actual_df = actual_df.sort_values("date")

# Planned schedule (date, planned daily distance)
plan_df = pd.read_csv("planned_schedule.csv")

# Convert date to datetime.date
plan_df['date'] = pd.to_datetime(plan_df['date']).dt.date

# Compute cumulative planned distance
start_total = 2716  # your existing starting total, as at end of November
total = start_total
cum_list = []

for km in plan_df['km']:
    total += km
    cum_list.append(total)

# Add cumulative to DataFrame for convenience
plan_df['cum'] = cum_list

# Compute actual cumulative
actual_dates = []
actual_cum = []
t = start_total
for _, row in actual_df.iterrows():
    t += row["km"]
    actual_dates.append(row["date"].date())
    actual_cum.append(t)

# Target line: from Dec 1 to Dec 31 straight to 3000
start = plan_df['date'].iloc[0]
end = plan_df['date'].iloc[-1]
target_start = start_total
remaining = 3000 - target_start
num_days = (end - start).days
slope = remaining / num_days

target_dates = plan_df['date']

target_cum = []
for i in range(len(target_dates)):
    days_passed = (target_dates[i] - start).days
    target_cum.append(target_start + slope * days_passed)

# Plot
with col_main:
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    axs = axs.flatten()  # flatten 2x2 grid to 1D array for easier indexing

    # Quadrant 1: Cumulative comparison
    axs[0].plot(plan_df['date'].to_numpy(), plan_df['cum'].to_numpy(), label='Planned', marker='o')
    axs[0].plot(np.array(actual_dates), np.array(actual_cum), label='Actual', marker='s')
    axs[0].plot(np.array(target_dates), np.array(target_cum), label='Target (straight)', linestyle='--')
    axs[0].set_title('Cumulative Distance')
    axs[0].legend()
    axs[0].tick_params(axis='x', rotation=45)

    # Quadrant 2: Planned daily distances
    axs[1].bar(plan_df['date'].to_numpy(), plan_df['km'].to_numpy())
    axs[1].set_title('Planned Daily km')
    axs[1].tick_params(axis='x', rotation=45)

    # Quadrant 3: Remaining to 3000 based on plan
    remaining_plan = (3000 - plan_df['cum']).to_numpy()
    axs[2].plot(plan_df['date'].to_numpy(), remaining_plan)
    axs[2].set_title('Remaining to 3000 (Plan)')
    axs[2].tick_params(axis='x', rotation=45)

    # Quadrant 4: Actual vs Target difference
    target_for_actual = [target_start + slope * (d - start).days for d in actual_dates]
    diff = np.array(actual_cum) - np.array(target_for_actual)
    axs[3].plot(np.array(actual_dates), diff, marker='d')
    axs[3].axhline(0, linestyle='--')
    axs[3].set_title('Actual minus Target')
    axs[3].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    st.pyplot(fig)


















