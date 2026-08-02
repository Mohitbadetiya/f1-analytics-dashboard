import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Driver Explorer", page_icon="🏁", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/master_results.csv')
    return df

master = load_data()

st.title("🏁 Driver Explorer")

driver_list = sorted(master['driver_name'].dropna().unique())
selected_driver = st.selectbox("Choose a driver", driver_list, index=driver_list.index("Lewis Hamilton") if "Lewis Hamilton" in driver_list else 0)

driver_data = master[master['driver_name'] == selected_driver]

col1, col2, col3 = st.columns(3)
col1.metric("Total Races", driver_data['raceId'].nunique())
col2.metric("Wins", (driver_data['position'] == 1).sum())
col3.metric("Podiums", (driver_data['position'] <= 3).sum())

st.subheader(f"{selected_driver}'s Points Over Time")

points_by_year = driver_data.groupby('year')['points'].sum().reset_index()

fig = px.line(points_by_year, x='year', y='points', markers=True,
              title=f"{selected_driver} — Championship Points by Season")
fig.update_layout(xaxis_title="Season", yaxis_title="Total Points")

st.plotly_chart(fig, use_container_width=True)