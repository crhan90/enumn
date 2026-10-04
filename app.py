import streamlit as st
import pandas as pd
import numpy as np
import math

# 1. Page Configuration
st.set_page_config(page_title="Multi-League & Nations League AI Predictor", page_icon="⚽", layout="centered")

st.title("⚽ Multi-League AI Game Line Predictor")
st.write("Predict Moneyline, Spreads, Over/Under Totals, BTTS, and Team Totals for top leagues and UEFA Nations League.")

# 2. League Mapping & Configuration
LEAGUES = {
    "🏆 UEFA Nations League / National Teams": "INTERNATIONAL",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League": "E0",
    "🇪🇸 Spanish La Liga": "SP1",
    "🇮🇹 Italian Serie A": "I1",
    "🇩🇪 German Bundesliga": "D1",
    "🇫🇷 French Ligue 1": "F1",
    "🇳🇱 Dutch Eredivisie": "N1",
    "🇵🇹 Portuguese Primeira Liga": "P1"
}

selected_league_label = st.selectbox("Select Competition / League", list(LEAGUES.keys()))
league_code = LEAGUES[selected_league_label]

# 3. Data Loader Function with Multi-Season Fallback
@st.cache_data(ttl=86400)
def load_match_data(code):
    if code == "INTERNATIONAL":
        # Public dataset of international results (Includes Nations League, World Cup Qualifiers, Euros)
        url = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
        df = pd.read_csv(url)
        # Filter for recent years to reflect current team strength
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'] >= '2021-01-01'].copy()
        df.rename(columns={'home_team': 'HomeTeam', 'away_team': 'AwayTeam', 
                           'home_score': 'FTHG', 'away_score': 'FTAG'}, inplace=True)
        return df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].dropna()
    else:
        # Try latest season URLs for club leagues
        seasons = ['2526', '2627', '2425']
        for season in seasons:
            try:
                url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
                df = pd.read_csv(url)
                if 'HomeTeam' in df.columns and len(df) > 0:
                    return df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].dropna()
            except Exception:
                continue
        raise ValueError("Could not fetch data for selected league.")

try:
    df = load_match_data(league_code)
    all_teams = sorted(list(set(df['HomeTeam'].unique()).union(set(df['AwayTeam'].unique()))))

    st.subheader("Select Teams")
    col1, col2 = st.columns(2)
    
    with col1:
        # Defaults to Azerbaijan if present in International selection
        default_home = all_teams.index("Azerbaijan") if "Azerbaijan" in all_teams else 0
        home_team = st.selectbox("Home Team", all_teams, index=default_home)
    with col2:
        # Defaults to Lithuania if present
        default_away = all_teams.index("Lithuania") if "Lithuania" in all_teams else (1 if len(all_teams) > 1 else 0)
        away_team = st.selectbox("Away Team", all_teams, index=default_away)

    if home_team == away_team:
        st.warning("Please select two different teams.")
    else:
        # 4. Calculate Expected Goals (xG) using Poisson Model
        home_games = df[df['HomeTeam'] == home_team]
        away_games = df[df['AwayTeam'] == away_team]

        league_avg_home_goals = df['FTHG'].mean() if df['FTHG'].mean() > 0 else 1.35
        league_avg_away_goals = df['FTAG'].mean() if df['FTAG'].mean() > 0 else 1.10

        home_attack = (home_games['FTHG'].mean() if len(home_games) > 0 else league_avg_home_goals) / league_avg_home_goals
        home_defense = (home_games['FTAG'].mean() if len(home_games) > 0 else league_avg_away_goals) / league_avg_away_goals

        away_attack = (away_games['FTAG'].mean() if len(away_games) > 0 else league_avg_away_goals) / league_avg_away_goals
        away_defense = (away_games['FTHG'].mean() if len(away_games) > 0 else league_avg_home_goals) / league_avg_home_goals

        exp_home_goals = home_attack * away_defense * league_avg_home_goals
        exp_away_goals = away_attack * home_defense * league_avg_away_goals

        # 5. Poisson Matrix Construction
        max_goals = 8
        prob_matrix = np.zeros((max_goals, max_goals))

        for i in range(max_goals):
            for j in range(max_goals):
                p_i = (exp_home_goals**i * np.exp(-exp_home_goals)) / math.factorial(i)
                p_j = (exp_away_goals**j * np.exp(-exp_away_goals)) / math.factorial(j)
                prob_matrix[i, j] = p_i * p_j

        prob_matrix /= prob_matrix.sum()

        # 6. Execute Multi-Market Line Predictions
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

            # Market 5: Individual Team Totals (> 0.5 Goals)
            home_over_05 = np.sum(prob_matrix[1:, :]) * 100
            away_over_05 = np.sum(prob_matrix[:, 1:]) * 100

            # Display Results Matching Market Formats
            st.markdown("---")
            st.subheader(f"📊 Market Line Predictions: {home_team} vs {away_team}")

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
    st.error(f"Error loading league data: {e}")
