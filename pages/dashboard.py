import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import random

st.set_page_config(page_title="Dashboard", layout="wide")

# Simulated daily data
def generate_sample_data():
    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i) for i in range(7)][::-1]
    data = {
        "Date": dates,
        "Steps": [random.randint(4000, 10000) for _ in range(7)],
        "Heart Rate": [random.randint(65, 120) for _ in range(7)],
        "Sleep Hours": [round(random.uniform(5.5, 8.5), 1) for _ in range(7)]
    }
    return pd.DataFrame(data)

data = generate_sample_data()

# --- HEADER ---
st.markdown("""
    <h2 style='color:#1abc9c;'>🏠 Your Personalized Dashboard</h2>
    <p style='color:#555;'>Track your progress, see trends, and follow your personalized recommendations.</p>
    <hr style='border:1px solid #eee;'>
""", unsafe_allow_html=True)

# --- METRICS ROW ---
col1, col2, col3 = st.columns(3)
col1.metric("👣 Steps Today", f"{data['Steps'].iloc[-1]} steps")
col2.metric("❤️ Avg Heart Rate", f"{sum(data['Heart Rate'])//7} bpm")
col3.metric("🛌 Sleep Last Night", f"{data['Sleep Hours'].iloc[-1]} hrs")

# --- CHARTS ---
st.markdown("### 📊 Weekly Trends")
chart1, chart2 = st.columns(2)

with chart1:
    fig, ax = plt.subplots()
    ax.plot(data['Date'], data['Steps'], marker='o', color='#3498db')
    ax.set_title("Steps Over the Week")
    ax.set_xlabel("Date")
    ax.set_ylabel("Steps")
    ax.grid(True)
    st.pyplot(fig)

with chart2:
    fig, ax = plt.subplots()
    ax.plot(data['Date'], data['Heart Rate'], marker='x', color='#e74c3c')
    ax.set_title("Heart Rate Over the Week")
    ax.set_xlabel("Date")
    ax.set_ylabel("BPM")
    ax.grid(True)
    st.pyplot(fig)

# --- WELLNESS TIP ---
st.markdown("""
    <div style='background-color: #f0f9f8; padding: 20px; border-radius: 10px; margin-top: 30px;'>
        <h4 style='color: #16a085;'>💡 Wellness Tip of the Day</h4>
        <p style='color: #333;'>Hydration is key! Aim to drink at least 8 cups of water daily to keep your metabolism running and your mind sharp.</p>
    </div>
""", unsafe_allow_html=True)

# --- NEXT WORKOUT PLAN ---
st.markdown("""
    <div style='background-color: #fef7ea; padding: 20px; border-radius: 10px; margin-top: 30px;'>
        <h4 style='color: #d35400;'>🔥 Your Next Workout Plan</h4>
        <ul style='color: #444;'>
            <li>10-min warm-up walk</li>
            <li>20-min full body strength training</li>
            <li>10-min HIIT cardio (jumping jacks, burpees, mountain climbers)</li>
            <li>5-min cooldown and stretching</li>
        </ul>
    </div>
""", unsafe_allow_html=True)