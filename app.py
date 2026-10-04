import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# 1. Dashboard Page Configuration
st.set_page_config(page_title="AI Sports Outcome Predictor", page_icon="⚽", layout="centered")

st.title("⚽ AI Sports Match Outcome Predictor")
st.write("Enter upcoming match metrics below to generate AI probabilistic predictions.")

# 2. Historical Training Data
# In production, this can be loaded from a CSV file or live sports API.
# Features: [home_win_rate, away_win_rate, home_avg_goals, away_avg_goals]
data = {
    'home_win_rate': [0.80, 0.40, 0.60, 0.20, 0.90, 0.30, 0.70, 0.50],
    'away_win_rate': [0.30, 0.70, 0.40, 0.80, 0.20, 0.60, 0.30, 0.50],
    'home_avg_goals': [2.5, 1.1, 1.8, 0.9, 3.0, 1.2, 2.1, 1.5],
    'away_avg_goals': [0.8, 2.1, 1.0, 2.4, 0.5, 1.9, 1.1, 1.5],
    'outcome': [1, 0, 1, 0, 1, 0, 1, 0]  # 1 = Home Win, 0 = Away Win/Draw
}
df = pd.DataFrame(data)

X = df[['home_win_rate', 'away_win_rate', 'home_avg_goals', 'away_avg_goals']]
y = df['outcome']

# 3. Train the AI Machine Learning Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 4. User Inputs on Web Dashboard
st.subheader("Match Setup")

col1, col2 = st.columns(2)

with col1:
    home_team = st.text_input("Home Team", "Arsenal")
    home_win_pct = st.slider("Home Recent Win Rate (%)", 0, 100, 75) / 100.0
    home_goals = st.number_input("Home Avg Goals / Game", 0.0, 5.0, 2.2, step=0.1)

with col2:
    away_team = st.text_input("Away Team", "Chelsea")
    away_win_pct = st.slider("Away Recent Win Rate (%)", 0, 100, 45) / 100.0
    away_goals = st.number_input("Away Avg Goals / Game", 0.0, 5.0, 1.1, step=0.1)

# 5. Prediction Trigger Button
if st.button("Generate AI Prediction", type="primary"):
    match_features = [[home_win_pct, away_win_pct, home_goals, away_goals]]
    
    # Calculate probability distributions
    probabilities = model.predict_proba(match_features)[0]
    home_prob = int(probabilities[1] * 100)
    away_prob = int(probabilities[0] * 100)

    st.markdown("---")
    st.subheader("Match Outcome Probability")

    res_col1, res_col2 = st.columns(2)
    res_col1.metric(label=f"{home_team} Win Chance", value=f"{home_prob}%")
    res_col2.metric(label=f"{away_team} Win Chance", value=f"{away_prob}%")

    if home_prob >= away_prob:
        st.success(f"**Predicted Winner:** {home_team}")
    else:
        st.warning(f"**Predicted Winner:** {away_team}")