# streamlit_app.py

import streamlit as st
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

st.title("December Running Dashboard")
st.set_page_config(layout="wide")

# Create three columns: left padding, main content, right padding
col_left, col_main, col_right = st.columns([1, 4, 1])

# Load actual data from CSV
# Expecting a file called actual.csv in the same folder
# with columns: date, km
try:
    actual_df = pd.read_csv("actual.csv", parse_dates=["date"])
    actual_df = actual_df.sort_values("date")
except FileNotFoundError:
    st.error("actual.csv not found. Please create the file with columns: date, km")
    st.stop()

# Starting total at end of November
start_total = 2716

# Planned schedule (date, planned daily distance)
plan = [
    ('2025-12-01', 0),
    ('2025-12-02', 10),
    ('2025-12-03', 10),
    ('2025-12-04', 10),
    ('2025-12-05', 0),
    ('2025-12-06', 10),
    ('2025-12-07', 25),
    ('2025-12-08', 0),
    ('2025-12-09', 10),
    ('2025-12-10', 10),
    ('2025-12-11', 10),
    ('2025-12-12', 0),
    ('2025-12-13', 10),
    ('2025-12-14', 25),
    ('2025-12-15', 0),
    ('2025-12-16', 10),
    ('2025-12-17', 10),
    ('2025-12-18', 10),
    ('2025-12-19', 0),
    ('2025-12-20', 10),
    ('2025-12-21', 40),
    ('2025-12-22', 0),
    ('2025-12-23', 10),
    ('2025-12-24', 10),
    ('2025-12-25', 10),
    ('2025-12-26', 0),
    ('2025-12-27', 10),
    ('2025-12-28', 25),
    ('2025-12-29', 0),
    ('2025-12-30', 10),
    ('2025-12-31', 10),
]

# Compute plan cumulative
plan_dates = []
plan_cum = []
total = start_total
for d_str, dist in plan:
    d = dt.datetime.strptime(d_str, '%Y-%m-%d').date()
    total += dist
    plan_dates.append(d)
    plan_cum.append(total)

# Compute actual cumulative
actual_dates = []
actual_cum = []
t = start_total
for _, row in actual_df.iterrows():
    t += row["km"]
    actual_dates.append(row["date"].date())
    actual_cum.append(t)

# Target line: from Dec 1 to Dec 31 straight to 3000
start = plan_dates[0]
end = plan_dates[-1]
target_start = start_total
remaining = 3000 - target_start
num_days = (end - start).days
slope = remaining / num_days

target_dates = plan_dates

target_cum = []
for i in range(len(target_dates)):
    days_passed = (target_dates[i] - start).days
    target_cum.append(target_start + slope * days_passed)

# Plot
with col_main:
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    # Quadrant 1: Cumulative comparison
    axs[0, 0].plot(plan_dates, plan_cum, label='Planned', marker='o')
    axs[0, 0].plot(actual_dates, actual_cum, label='Actual', marker='s')
    axs[0, 0].plot(target_dates, target_cum, label='Target (straight)', linestyle='--')
    axs[0, 0].set_title('Cumulative Distance')
    axs[0, 0].legend()
    axs[0, 0].tick_params(axis='x', rotation=45)
    
    # Quadrant 2: Planned daily distances
    plan_daily = [d for _, d in plan]
    axs[0, 1].bar(plan_dates, plan_daily)
    axs[0, 1].set_title('Planned Daily km')
    axs[0, 1].tick_params(axis='x', rotation=45)
    
    # Quadrant 3: Remaining to 3000 based on plan
    remaining_plan = [3000 - c for c in plan_cum]
    axs[1, 0].plot(plan_dates, remaining_plan)
    axs[1, 0].set_title('Remaining to 3000 (Plan)')
    axs[1, 0].tick_params(axis='x', rotation=45)
    
    # Quadrant 4: Actual vs Target difference
    # Interpolate target for actual dates
    target_for_actual = []
    for d in actual_dates:
        days_passed = (d - start).days
        target_for_actual.append(target_start + slope * days_passed)
    
    diff = np.array(actual_cum) - np.array(target_for_actual)
    axs[1, 1].plot(actual_dates, diff, marker='d')
    axs[1, 1].axhline(0, linestyle='--')
    axs[1, 1].set_title('Actual minus Target')
    axs[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    st.pyplot(fig)






