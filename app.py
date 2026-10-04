import streamlit as st
import pandas as pd
import numpy as np
import math

# 1. Page Configuration
st.set_page_config(page_title="Multi-Market AI Football Predictor", page_icon="⚽", layout="centered")

st.title("⚽ Multi-Market AI Match Predictor")
st.write("Generates probabilities for Moneyline, Spreads, Over/Under Totals, Both Teams to Score, and Team Totals.")

# 2. Automated Historical Data Ingestion
@st.cache_data(ttl=86400)
def load_data():
    url = "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
    df = pd.read_csv(url)
    return df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']].dropna()

try:
    df = load_data()
    all_teams = sorted(list(set(df['HomeTeam'].unique()).union(set(df['AwayTeam'].unique()))))

    st.subheader("Select Upcoming Match")
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("Home Team", all_teams, index=0)
    with col2:
        away_team = st.selectbox("Away Team", all_teams, index=1 if len(all_teams) > 1 else 0)

    if home_team == away_team:
        st.warning("Please select two different teams.")
    else:
        # 3. Calculate Expected Goals (xG)
        home_games = df[df['HomeTeam'] == home_team]
        away_games = df[df['AwayTeam'] == away_team]

        league_avg_home_goals = df['FTHG'].mean()
        league_avg_away_goals = df['FTAG'].mean()

        home_attack = (home_games['FTHG'].mean() if len(home_games) > 0 else league_avg_home_goals) / league_avg_home_goals
        home_defense = (home_games['FTAG'].mean() if len(home_games) > 0 else league_avg_away_goals) / league_avg_away_goals

        away_attack = (away_games['FTAG'].mean() if len(away_games) > 0 else league_avg_away_goals) / league_avg_away_goals
        away_defense = (away_games['FTHG'].mean() if len(away_games) > 0 else league_avg_home_goals) / league_avg_home_goals

        # Expected goals for each team
        exp_home_goals = home_attack * away_defense * league_avg_home_goals
        exp_away_goals = away_attack * home_defense * league_avg_away_goals

        # 4. Generate Poisson Goal Matrix (up to 7 goals each)
        max_goals = 8
        prob_matrix = np.zeros((max_goals, max_goals))

        for i in range(max_goals):
            for j in range(max_goals):
                p_i = (exp_home_goals**i * np.exp(-exp_home_goals)) / math.factorial(i)
                p_j = (exp_away_goals**j * np.exp(-exp_away_goals)) / math.factorial(j)
                prob_matrix[i, j] = p_i * p_j

        prob_matrix /= prob_matrix.sum()  # Normalize probabilities

        # 5. Prediction Execution
        if st.button("Generate Full Market Line Predictions", type="primary"):
            # Market 1: Moneyline (Home / Draw / Away)
            home_win = np.sum(np.tril(prob_matrix, -1)) * 100
            draw = np.sum(np.diag(prob_matrix)) * 100
            away_win = np.sum(np.triu(prob_matrix, 1)) * 100

            # Market 2: Spreads (-1.5 / +1.5)
            home_cover_15 = 0
            for i in range(max_goals):
                for j in range(max_goals):
                    if i - j >= 2:
                        home_cover_15 += prob_matrix[i, j]
            home_cover_15 *= 100
            away_cover_15 = 100 - home_cover_15

            # Market 3: Totals (Over / Under 2.5)
            over_25 = 0
            for i in range(max_goals):
                for j in range(max_goals):
                    if i + j > 2.5:
                        over_25 += prob_matrix[i, j]
            over_25 *= 100
            under_25 = 100 - over_25

            # Market 4: Both Teams to Score (BTTS)
            btts_yes = np.sum(prob_matrix[1:, 1:]) * 100
            btts_no = 100 - btts_yes

            # Market 5: Individual Team Totals (Over 0.5)
            home_over_05 = np.sum(prob_matrix[1:, :]) * 100
            away_over_05 = np.sum(prob_matrix[:, 1:]) * 100

            # Display Results Matching Market Format
            st.markdown("---")
            st.subheader("📊 AI Probabilities Across All Game Lines")

            st.write("### 1. Moneyline (Match Result)")
            m1, m2, m3 = st.columns(3)
            m1.metric(f"{home_team} Win", f"{home_win:.1f}%", f"{int(home_win)}¢")
            m2.metric("Draw", f"{draw:.1f}%", f"{int(draw)}¢")
            m3.metric(f"{away_team} Win", f"{away_win:.1f}%", f"{int(away_win)}¢")

            st.write("### 2. Spreads")
            s1, s2 = st.columns(2)
            s1.metric(f"{home_team} -1.5", f"{home_cover_15:.1f}%", f"{int(home_cover_15)}¢")
            s2.metric(f"{away_team} +1.5", f"{away_cover_15:.1f}%", f"{int(away_cover_15)}¢")

            st.write("### 3. Totals (2.5 Goals)")
            t1, t2 = st.columns(2)
            t1.metric("Over 2.5 Goals", f"{over_25:.1f}%", f"{int(over_25)}¢")
            t2.metric("Under 2.5 Goals", f"{under_25:.1f}%", f"{int(under_25)}¢")

            st.write("### 4. Both Teams to Score?")
            b1, b2 = st.columns(2)
            b1.metric("YES", f"{btts_yes:.1f}%", f"{int(btts_yes)}¢")
            b2.metric("NO", f"{btts_no:.1f}%", f"{int(btts_no)}¢")

            st.write("### 5. Team Totals (> 0.5 Goals)")
            tt1, tt2 = st.columns(2)
            tt1.metric(f"{home_team} Over 0.5", f"{home_over_05:.1f}%", f"{int(home_over_05)}¢")
            tt2.metric(f"{away_team} Over 0.5", f"{away_over_05:.1f}%", f"{int(away_over_05)}¢")

except Exception as e:
    st.error(f"Error executing predictions: {e}")
