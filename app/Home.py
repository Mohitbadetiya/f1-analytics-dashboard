import streamlit as st
import pandas as pd

st.set_page_config(page_title="F1 Analytics Dashboard", page_icon="🏎️", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/master_results.csv')
    return df

master = load_data()

st.title("🏎️ F1 Analytics Dashboard")
st.markdown("An end-to-end analysis of 75 years of Formula 1 history — from raw data to driver skill ratings.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Races", master['raceId'].nunique())
col2.metric("Total Drivers", master['driverId'].nunique())
col3.metric("Total Results", f"{len(master):,}")
col4.metric("Years Covered", f"{master['year'].min()}–{master['year'].max()}")

st.markdown("---")
st.subheader("Preview: Master Results Dataset")
st.dataframe(master.head(20))