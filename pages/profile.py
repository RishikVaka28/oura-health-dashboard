import streamlit as st

st.set_page_config(page_title="Profile", layout="wide")

# Dummy profile info (can be replaced with DB later)
profile_info = {
    "Name": "John Doe",
    "Age": 28,
    "Gender": "Male",
    "Fitness Level": "Intermediate",
    "Goals": "Build muscle, stay active",
    "Preferred Workouts": "Strength training, Cardio"
}

st.markdown("""
    <h2 style='color:#1abc9c;'>👤 User Profile</h2>
    <p style='color:#555;'>Your fitness identity, preferences, and wellness goals.</p>
    <hr style='border:1px solid #eee;'>
""", unsafe_allow_html=True)

# Display profile info
st.markdown("### 📝 Personal Details")
with st.container():
    col1, col2 = st.columns(2)
    for idx, (label, value) in enumerate(profile_info.items()):
        if idx % 2 == 0:
            col1.markdown(f"**{label}:** {value}")
        else:
            col2.markdown(f"**{label}:** {value}")

# Editable Goals
st.markdown("---")
st.markdown("### 🎯 Update Your Fitness Goals")
with st.form("update_goals_form"):
    new_goals = st.text_input("What are your new fitness goals?", value=profile_info["Goals"])
    preferred_workouts = st.text_input("Preferred Workouts", value=profile_info["Preferred Workouts"])
    submitted = st.form_submit_button("💾 Save Changes")

    if submitted:
        profile_info["Goals"] = new_goals
        profile_info["Preferred Workouts"] = preferred_workouts
        st.success("✅ Profile updated successfully!")

# Level Display
st.markdown("---")
st.markdown("### 🧬 Fitness Level Tracker")
st.info("🔰 Current Level: Intermediate")
st.progress(65, text="Progress to next level")

st.markdown("""
    <p style='color: #999; font-size: 0.9em;'>Level up by staying consistent with workouts and sleep, and maintaining healthy heart rate averages.</p>
""", unsafe_allow_html=True)