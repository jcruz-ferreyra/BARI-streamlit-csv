import json
import os
from datetime import datetime, time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


@st.cache_data(ttl=3600)
def get_sensor_readings():
    script_dir = Path(__file__).parent
    csv_file = script_dir / "data.csv"
    return pd.read_csv(csv_file, dtype={"sensor_id": str}, parse_dates=["timestamp"])


@st.cache_data
def get_sensor_metadata():
    script_dir = Path(__file__).parent
    csv_file = script_dir / "metadata.csv"
    return pd.read_csv(csv_file, dtype={"sensor_id": str})


def get_sensor_address_from_id(metadata_df, sensor_id):
    result = metadata_df[metadata_df["sensor_id"] == sensor_id]["address"].values
    return result[0] if len(result) > 0 else f"Sensor {sensor_id}"


sensor_readings = get_sensor_readings()
sensor_metadata = get_sensor_metadata()

# Check for sensor filtering parameter in the URL
sensor_to_display = st.query_params.get("sensor", None)
if sensor_to_display:
    filtered = sensor_metadata[sensor_metadata["sensor_id"] == sensor_to_display][
        "address"
    ].values
    sensor_to_display_address = (
        filtered[0] if len(filtered) > 0 else f"Sensor {sensor_to_display}"
    )
else:
    sensor_to_display_address = None

header_text = (
    "All Sensors" if not sensor_to_display else f"Sensor: {sensor_to_display_address}"
)

st.header(header_text)

if sensor_to_display:
    sensor_readings = sensor_readings[sensor_readings["sensor_id"] == sensor_to_display]

# <!-- Filtering Options -->

# Inputs: Aggregation Options
st.subheader("Aggregation")
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    btn_1min = st.button("1 min avg", use_container_width=True)
with col_btn2:
    btn_1h = st.button("1 h avg", use_container_width=True)
with col_btn3:
    btn_1day = st.button("1 day avg", use_container_width=True)

# Set aggregation based on button clicks
if btn_1min:
    aggregation_freq = "1min"
    aggregation_label = "1 Minute"
elif btn_1h:
    aggregation_freq = "1h"
    aggregation_label = "1 Hour"
elif btn_1day:
    aggregation_freq = "1D"
    aggregation_label = "1 Day"
else:
    # Default
    aggregation_freq = "1h"
    aggregation_label = "1 Hour"

aggregation_func = "mean"  # Always use mean (avg)

st.divider()

# Inputs: Filter Options
st.subheader("Filter Options")
st.write("Select the start and end timestamps to refine the data selection.")

min_val = sensor_readings["timestamp"].min()
max_val = sensor_readings["timestamp"].max()

col1, col2, col3, col4 = st.columns([2, 1, 2, 1])

with col1:
    start_date = st.date_input(
        "Start Date",
        min_value=min_val.date(),
        max_value=max_val.date(),
        value=min_val.date(),
        format="YYYY-MM-DD",
    )
with col2:
    start_time = st.time_input("Start Time", value=time(0, 0))

with col3:
    end_date = st.date_input(
        "End Date",
        min_value=min_val.date(),
        max_value=max_val.date(),
        value=max_val.date(),
        format="YYYY-MM-DD",
    )
with col4:
    end_time = st.time_input("End Time", value=time(23, 59))

start_dt = datetime.combine(start_date, start_time)
end_dt = datetime.combine(end_date, end_time)


# <!-- Main Content - Tabs First -->

# Define the tabs with their content
tab1, tab2, tab3 = st.tabs(["Temperature", "Noise", "Raw Data"])

# Placeholder values for initial render
aggregation_freq = "15min"
aggregation_func = "mean"

with tab1:
    temp_chart_placeholder = st.empty()

with tab2:
    noise_chart_placeholder = st.empty()

with tab3:
    raw_data_placeholder = st.empty()

# <!-- Filter and Aggregation Options Below Charts -->

st.divider()

# Filter data
if start_dt and end_dt and start_dt > end_dt:
    st.warning(
        "Start date should be before end date. We will flip the two for your convenience."
    )
    start_dt, end_dt = end_dt, start_dt
if start_date:
    st.caption(f"Filtering by start date: :green[{start_dt}]")
    sensor_readings = sensor_readings[sensor_readings["timestamp"] >= start_dt]
if end_date:
    st.caption(f"Filtering by end date: :green[{end_dt}]")
    sensor_readings = sensor_readings[sensor_readings["timestamp"] <= end_dt]


# Aggregate filtered data
agg_sensor_readings = (
    sensor_readings.groupby(
        ["sensor_id", pd.Grouper(key="timestamp", freq=aggregation_freq)]
    )
    .agg(aggregation_func)
    .reset_index()
    .round(2)
)
agg_sensor_readings = agg_sensor_readings.sort_values(by="timestamp", ascending=False)

agg_sensor_readings["SensorLocation"] = agg_sensor_readings.apply(
    lambda x: get_sensor_address_from_id(sensor_metadata, x["sensor_id"]), axis=1
)

# Update the charts with actual data
with temp_chart_placeholder:
    g = px.line(
        agg_sensor_readings,
        x="timestamp",
        y="Heat",
        color="SensorLocation",
        title=f"Temperature readings (°F) every {aggregation_options[aggregation_freq]} ({aggregation_func})",
        hover_data=[
            "SensorLocation",
            "timestamp",
            "Heat",
        ],
    )
    st.plotly_chart(g, use_container_width=True)

with noise_chart_placeholder:
    g = px.line(
        agg_sensor_readings,
        x="timestamp",
        y="Noise",
        color="SensorLocation",
        title=f"Noise readings (db) every {aggregation_options[aggregation_freq]} ({aggregation_func})",
        hover_data=[
            "SensorLocation",
            "timestamp",
            "Noise",
        ],
    )
    st.plotly_chart(g, use_container_width=True)

with raw_data_placeholder:
    st.write(
        "This table shows the raw sensor readings. You can filter and aggregate the data using the options below."
    )
    df = (
        agg_sensor_readings[
            ["sensor_id", "SensorLocation", "timestamp", "Heat", "Noise"]
        ]
        .sort_values(by=["sensor_id", "timestamp"], ascending=[True, False])
        .reset_index(drop=True)
    )

    df["agg_freq"] = aggregation_freq
    df["agg_func"] = aggregation_func

    df = df.style.format(
        {
            "sensor_id": lambda x: f"Sensor {x}",
            "timestamp": lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
            "Heat": "{:.2f} °F",
            "Noise": "{:.2f} dB",
        }
    )
    st.dataframe(data=df, use_container_width=True)
