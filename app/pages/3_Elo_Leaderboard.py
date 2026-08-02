import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Elo Leaderboard", page_icon="👑", layout="wide")

@st.cache_resource
def get_connection():
    return sqlite3.connect('data/processed/f1.db', check_same_thread=False)

conn = get_connection()

st.title("👑 Driver Elo Ratings")
st.markdown("A custom rating system, built from teammate head-to-head results — isolating driver skill from car performance. Same car, same race: whoever finishes ahead 'wins' the comparison and gains rating; loses it otherwise.")

min_comparisons = st.slider("Minimum teammate comparisons (reliability filter)", 
                              min_value=0, max_value=200, value=50, step=10)

@st.cache_data
def get_leaderboard(min_comp):
    query = f"""
    SELECT driver_name, elo_rating, comparisons
    FROM elo_ratings
    WHERE comparisons >= {min_comp}
    ORDER BY elo_rating DESC
    """
    return pd.read_sql_query(query, conn)

leaderboard = get_leaderboard(min_comparisons)
leaderboard['rank'] = range(1, len(leaderboard) + 1)
leaderboard['elo_rating'] = leaderboard['elo_rating'].round(1)

st.dataframe(leaderboard[['rank', 'driver_name', 'elo_rating', 'comparisons']], 
             use_container_width=True, hide_index=True)

st.subheader("Elo Rating History")

driver_options = sorted(leaderboard['driver_name'].unique())
selected_driver = st.selectbox("Select a driver to see rating history", driver_options)

@st.cache_data
def get_driver_history(driver_name):
    query = f"""
    SELECT date, elo_rating
    FROM elo_history
    WHERE driver_name = '{driver_name}'
    ORDER BY date
    """
    return pd.read_sql_query(query, conn)

history = get_driver_history(selected_driver)

fig = px.line(history, x='date', y='elo_rating', 
              title=f"{selected_driver} — Elo Rating Over Time")
fig.update_layout(xaxis_title="Date", yaxis_title="Elo Rating")
fig.add_hline(y=1500, line_dash="dash", line_color="gray", annotation_text="Starting Elo (1500)")

st.plotly_chart(fig, use_container_width=True)