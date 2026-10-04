import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# 1. Page Setup
st.set_page_config(page_title="Automated AI Football Predictor", page_icon="⚽", layout="centered")

st.title("⚽ Automated AI Football Predictor")
st.write("Select any two teams. The AI automatically fetches team form, calculates goals/win rates, and predicts match outcomes.")

# 2. Automated Data Fetching Function
@st.cache_data(ttl=86400) # Caches data for 24 hours
def load_live_football_data():
    # Downloads official international/league match data automatically
    # E0 = Premier League. You can swap or add other league CSV URLs from football-data.co.uk
    url = "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
    df = pd.read_csv(url)
    
    # Filter key statistical columns
    cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    df = df[cols].dropna()
    return df

try:
    df = load_live_football_data()
    
    # Extract unique team names for the dropdown
    all_teams = sorted(list(set(df['HomeTeam'].unique()).union(set(df['AwayTeam'].unique()))))

    st.subheader("Select Match")
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("Home Team", all_teams, index=0)
    with col2:
        away_team = st.selectbox("Away Team", all_teams, index=1 if len(all_teams) > 1 else 0)

    if home_team == away_team:
        st.warning("Please select two different teams.")
    else:
        # 3. AI Data Processing (Calculates Form Automatically)
        def calculate_team_metrics(team_name, dataset):
            home_games = dataset[dataset['HomeTeam'] == team_name]
            away_games = dataset[dataset['AwayTeam'] == team_name]
            
            total_games = len(home_games) + len(away_games)
            if total_games == 0:
                return 0.50, 1.0  # Fallback defaults if new team

            home_wins = len(home_games[home_games['FTR'] == 'H'])
            away_wins = len(away_games[away_games['FTR'] == 'A'])
            total_wins = home_wins + away_wins
            
            total_goals = home_games['FTHG'].sum() + away_games['FTAG'].sum()
            
            win_rate = total_wins / total_games
            avg_goals = total_goals / total_games
            return win_rate, avg_goals

        # Calculate metrics for both teams behind the scenes
        h_win_rate, h_avg_goals = calculate_team_metrics(home_team, df)
        a_win_rate, a_avg_goals = calculate_team_metrics(away_team, df)

        # 4. Display Auto-Calculated Form
        st.markdown("---")
        st.subheader("Auto-Pulled Team Form Statistics")
        stat_col1, stat_col2 = st.columns(2)
        
        stat_col1.metric(f"{home_team} Win Rate", f"{int(h_win_rate * 100)}%", f"{h_avg_goals:.2f} Avg Goals")
        stat_col2.metric(f"{away_team} Win Rate", f"{int(a_win_rate * 100)}%", f"{a_avg_goals:.2f} Avg Goals")

        # 5. Train Random Forest AI Model
        df['Target'] = (df['FTR'] == 'H').astype(int) # 1 = Home Win, 0 = Draw/Away Win
        
        training_features = []
        for _, row in df.iterrows():
            hw, hg = calculate_team_metrics(row['HomeTeam'], df)
            aw, ag = calculate_team_metrics(row['AwayTeam'], df)
            training_features.append([hw, aw, hg, ag])

        X = pd.DataFrame(training_features, columns=['h_wr', 'a_wr', 'h_g', 'a_g'])
        y = df['Target']

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)

        # 6. Prediction Output
        if st.button("Generate AI Prediction", type="primary"):
            match_input = [[h_win_rate, a_win_rate, h_avg_goals, a_avg_goals]]
            probabilities = model.predict_proba(match_input)[0]
            
            home_prob = int(probabilities[1] * 100)
            away_draw_prob = 100 - home_prob

            st.markdown("---")
            st.subheader("AI Match Probabilities")
            
            res1, res2 = st.columns(2)
            res1.metric(f"{home_team} Win Probability", f"{home_prob}%")
            res2.metric(f"{away_team} / Draw Probability", f"{away_draw_prob}%")

            if home_prob > 55:
                st.success(f"**AI Prediction:** Strong statistical favor for {home_team} to win.")
            elif home_prob < 40:
                st.warning(f"**AI Prediction:** Advantage for {away_team} or Draw.")
            else:
                st.info("**AI Prediction:** Close match. High probability of a Draw or narrow victory.")

except Exception as e:
    st.error(f"Error fetching data: {e}")
