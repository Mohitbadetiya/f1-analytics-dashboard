import streamlit as st
import pandas as pd
import sqlite3
import joblib
import plotly.graph_objects as go

st.set_page_config(page_title="Podium Predictor", page_icon="🎯", layout="wide")

st.title("🎯 Podium Probability Predictor")
st.markdown("Estimate a driver's podium chances using our custom-trained model — based on starting grid position and the team's current season form.")

@st.cache_resource
def load_model():
    return joblib.load('app/podium_model.pkl')

@st.cache_resource
def get_connection():
    return sqlite3.connect('data/processed/f1.db', check_same_thread=False)

try:
    model = load_model()
except FileNotFoundError:
    st.error("⚠️ Prediction model not found. Please train and save the model first (see Day 12 notebook).")
    st.stop()

conn = get_connection()

@st.cache_data
def get_constructor_forms():
    return pd.read_sql_query("SELECT constructor_name, constructor_form FROM latest_constructor_form", conn)

form_data = get_constructor_forms()

col1, col2 = st.columns(2)
with col1:
    selected_constructor = st.selectbox("Team", sorted(form_data['constructor_name'].unique()))
with col2:
    grid_position = st.slider("Starting Grid Position", min_value=1, max_value=20, value=1)

constructor_form_value = form_data[form_data['constructor_name'] == selected_constructor]['constructor_form'].values[0]

input_data = pd.DataFrame({
    'grid': [grid_position],
    'constructor_form': [constructor_form_value]
})

probability = model.predict_proba(input_data)[0][1]

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=probability * 100,
    number={'suffix': "%"},
    title={'text': f"{selected_constructor} — Podium Chance from P{grid_position}"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#1f77b4"},
        'steps': [
            {'range': [0, 33], 'color': "#f8d7da"},
            {'range': [33, 66], 'color': "#fff3cd"},
            {'range': [66, 100], 'color': "#d4edda"}
        ]
    }
))

st.plotly_chart(fig, use_container_width=True)
st.caption("Model: Logistic Regression | Test ROC-AUC: 0.909 | Trained on 1950–2022, validated on 2023–2024")