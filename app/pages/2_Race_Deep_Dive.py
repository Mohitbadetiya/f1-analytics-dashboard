import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Race Deep-Dive", page_icon="🏁", layout="wide")

@st.cache_resource
def get_connection():
    return sqlite3.connect('data/processed/f1.db', check_same_thread=False)

conn = get_connection()

st.title("🏁 Race Deep-Dive")

@st.cache_data
def get_years():
    query = "SELECT DISTINCT year FROM results ORDER BY year DESC"
    return pd.read_sql_query(query, conn)['year'].tolist()

years = get_years()
selected_year = st.selectbox("Select Year", years)

@st.cache_data
def get_races(year):
    query = f"SELECT DISTINCT raceId, race_name FROM results WHERE year = {year} ORDER BY round"
    return pd.read_sql_query(query, conn)

races_in_year = get_races(selected_year)
selected_race_name = st.selectbox("Select Race", races_in_year['race_name'])
selected_race_id = races_in_year[races_in_year['race_name'] == selected_race_name]['raceId'].values[0]

@st.cache_data
def get_race_results(race_id):
    query = f"""
    SELECT positionOrder, driver_name, constructor_name, grid, position, points, status
    FROM results
    WHERE raceId = {race_id}
    ORDER BY positionOrder
    """
    return pd.read_sql_query(query, conn)

race_results = get_race_results(selected_race_id)

podium = race_results.head(3)
medals = ["🥇", "🥈", "🥉"]
cols = st.columns(3)
for i in range(min(3, len(podium))):
    cols[i].metric(f"{medals[i]} P{i+1}", podium.iloc[i]['driver_name'])

st.subheader(f"{selected_race_name} {selected_year} — Full Results")
st.dataframe(race_results, use_container_width=True, hide_index=True)

@st.cache_data
def get_lap_times(race_id):
    query = f"""
    SELECT lap_times.lap, lap_times.milliseconds, drivers.forename || ' ' || drivers.surname AS driver_name
    FROM lap_times
    JOIN drivers ON lap_times.driverId = drivers.driverId
    WHERE lap_times.raceId = {race_id}
    ORDER BY lap
    """
    df = pd.read_sql_query(query, conn)
    df['seconds'] = df['milliseconds'] / 1000
    return df

lap_data = get_lap_times(selected_race_id)

driver_options = sorted(lap_data['driver_name'].unique())
default_drivers = race_results.head(5)['driver_name'].tolist()
selected_drivers = st.multiselect("Compare drivers' lap times", driver_options, default=default_drivers)

chart_data = lap_data[lap_data['driver_name'].isin(selected_drivers)]

fig = px.line(chart_data, x='lap', y='seconds', color='driver_name', markers=True,
              title=f"{selected_race_name} {selected_year} — Lap Time Comparison")
fig.update_layout(xaxis_title="Lap", yaxis_title="Lap Time (seconds)")
st.plotly_chart(fig, use_container_width=True)

