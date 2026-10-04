import streamlit as st
import pandas as pd
import numpy as np
import math

# 1. Page Configuration
st.set_page_config(page_title="AI Game Line Predictor - Sports & Esports", page_icon="🎮", layout="centered")

st.title("🏆 AI Multi-Sport & Esports Game Line Predictor")
st.write("Predict Moneyline, Spreads, Over/Under Totals, and Exact Scores across Football, VALORANT, CS2, and LoL.")

# Category Selector
category = st.radio("Select Category", ["⚽ Football", "🎯 VALORANT", "🔫 Counter-Strike 2", "⚔️ League of Legends"], horizontal=True)

# ---------------------------------------------------------
# FOOTBALL PREDICTION ENGINE
# ---------------------------------------------------------
if category == "⚽ Football":
    LEAGUES = {
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League (2026/2027)": "E0",
        "🏆 UEFA Nations League / National Teams": "INTERNATIONAL",
        "🇪🇸 Spanish La Liga": "SP1",
        "🇮🇹 Italian Serie A": "I1",
        "🇩🇪 German Bundesliga": "D1",
        "🇫🇷 French Ligue 1": "F1"
    }

    selected_league_label = st.selectbox("Select Competition", list(LEAGUES.keys()))
    league_code = LEAGUES[selected_league_label]

    @st.cache_data(ttl=3600)
    def load_match_data(code):
        if code == "INTERNATIONAL":
            url = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
            df = pd.read_csv(url)
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] >= '2022-01-01'].copy()
            df.rename(columns={'home_team': 'HomeTeam', 'away_team': 'AwayTeam', 
                               'home_score': 'FTHG', 'away_score': 'FTAG'}, inplace=True)
            return df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].dropna()
        else:
            seasons = ['2627', '2526']
            dfs = []
            for season in seasons:
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
                    temp_df = pd.read_csv(url)
                    if 'HomeTeam' in temp_df.columns and len(temp_df) > 0:
                        dfs.append(temp_df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']])
                except Exception:
                    continue
            if dfs:
                return pd.concat(dfs, ignore_index=True).dropna()
            raise ValueError("Data unavailable.")

    try:
        df = load_match_data(league_code)
        all_teams = sorted(list(set(df['HomeTeam'].unique()).union(set(df['AwayTeam'].unique()))))

        st.subheader("Select Matchup")
        c1, c2 = st.columns(2)
        with c1:
            home_team = st.selectbox("Home Team", all_teams, index=0)
        with c2:
            away_team = st.selectbox("Away Team", all_teams, index=1 if len(all_teams) > 1 else 0)

        if home_team != away_team and st.button("Generate Football Market Lines", type="primary"):
            home_games = df[df['HomeTeam'] == home_team]
            away_games = df[df['AwayTeam'] == away_team]
            avg_h = df['FTHG'].mean() or 1.35
            avg_a = df['FTAG'].mean() or 1.10

            h_att = (home_games['FTHG'].mean() if len(home_games) > 0 else avg_h) / avg_h
            h_def = (home_games['FTAG'].mean() if len(home_games) > 0 else avg_a) / avg_a
            a_att = (away_games['FTAG'].mean() if len(away_games) > 0 else avg_a) / avg_a
            a_def = (away_games['FTHG'].mean() if len(away_games) > 0 else avg_h) / avg_h

            exp_h = h_att * a_def * avg_h
            exp_a = a_att * h_def * avg_a

            max_g = 8
            prob_matrix = np.zeros((max_g, max_g))
            for i in range(max_g):
                for j in range(max_g):
                    p_i = (exp_h**i * np.exp(-exp_h)) / math.factorial(i)
                    p_j = (exp_a**j * np.exp(-exp_a)) / math.factorial(j)
                    prob_matrix[i, j] = p_i * p_j
            prob_matrix /= prob_matrix.sum()

            home_win = np.sum(np.tril(prob_matrix, -1)) * 100
            draw = np.sum(np.diag(prob_matrix)) * 100
            away_win = np.sum(np.triu(prob_matrix, 1)) * 100

            cover_15 = sum(prob_matrix[i, j] for i in range(max_g) for j in range(max_g) if i - j >= 2) * 100
            over_25 = sum(prob_matrix[i, j] for i in range(max_g) for j in range(max_g) if i + j > 2.5) * 100
            btts_yes = np.sum(prob_matrix[1:, 1:]) * 100

            st.markdown("---")
            st.subheader(f"📊 Market Line Predictions: {home_team} vs {away_team}")
            
            st.write("### 1. Moneyline")
            m1, m2, m3 = st.columns(3)
            m1.metric(f"{home_team} Win", f"{home_win:.1f}%", f"{int(home_win)}¢")
            m2.metric("Draw", f"{draw:.1f}%", f"{int(draw)}¢")
            m3.metric(f"{away_team} Win", f"{away_win:.1f}%", f"{int(away_win)}¢")

            st.write("### 2. Spreads & Totals")
            s1, s2, s3 = st.columns(3)
            s1.metric(f"{home_team} -1.5", f"{cover_15:.1f}%", f"{int(cover_15)}¢")
            s2.metric("Over 2.5 Goals", f"{over_25:.1f}%", f"{int(over_25)}¢")
            s3.metric("BTTS Yes", f"{btts_yes:.1f}%", f"{int(btts_yes)}¢")
    except Exception as e:
        st.error(f"Error loading football data: {e}")

# ---------------------------------------------------------
# ESPORTS PREDICTION ENGINE (VALORANT, CS2, LOL)
# ---------------------------------------------------------
else:
    # Latest 2026 Rosters & Tournament Databases
    ESPORTS_TEAMS = {
        "🎯 VALORANT": {
            "Tournament": "VALORANT Champions 2026",
            "Teams": {
                "Paper Rex": 1850, "G2 Esports": 1820, "100 Thieves": 1780, "Team Vitality": 1810,
                "NRG": 1790, "FUT Esports": 1750, "Fnatic": 1830, "LOUD": 1770,
                "EDward Gaming": 1800, "T1": 1760, "Nongshim RedForce": 1720, "Global Esports": 1680
            }
        },
        "🔫 Counter-Strike 2": {
            "Tournament": "CS2 ESL Pro League / Major 2026",
            "Teams": {
                "Team Spirit": 1910, "Team Vitality": 1880, "FaZe Clan": 1840, "Natus Vincere": 1860,
                "MOUZ": 1830, "G2 Esports": 1820, "Team Falcons": 1850, "The MongolZ": 1790,
                "Astralis": 1760, "FURIA": 1750, "FUT Esports": 1740, "PVISION": 1710
            }
        },
        "⚔️ League of Legends": {
            "Tournament": "LoL World Championship 2026",
            "Teams": {
                "Gen.G": 1920, "Bilibili Gaming": 1890, "Hanwha Life Esports": 1880, "T1": 1900,
                "Top Esports": 1840, "G2 Esports": 1810, "Dplus KIA": 1820, "Cloud9": 1770,
                "Team Liquid": 1760, "Karmine Corp": 1750, "CTBC Flying Oyster": 1720, "Movistar KOI": 1710
            }
        }
    }

    esport_data = ESPORTS_TEAMS[category]
    st.info(f"🏆 Competition: **{esport_data['Tournament']}**")

    teams_list = sorted(list(esport_data["Teams"].keys()))

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        team_a = st.selectbox("Team A", teams_list, index=0)
    with col_b:
        team_b = st.selectbox("Team B", teams_list, index=1 if len(teams_list) > 1 else 0)
    with col_c:
        series_format = st.selectbox("Series Format", ["Best of 3 (Bo3)", "Best of 5 (Bo5)"])

    if team_a == team_b:
        st.warning("Please select two distinct teams.")
    else:
        # Elo Rating Calculation to Map Win Rate (p)
        elo_a = esport_data["Teams"][team_a]
        elo_b = esport_data["Teams"][team_b]
        
        # Base single map win probability for Team A
        p = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
        q = 1 - p

        if st.button("Generate Esports Market Line Predictions", type="primary"):
            st.markdown("---")
            st.subheader(f"📊 Market Lines: {team_a} vs {team_b} ({series_format})")
            st.caption(f"Calculated Single Map Win Rate: **{team_a} ({p*100:.1f}%)** vs **{team_b} ({q*100:.1f}%)**")

            # BO3 MARKOV ENGINE
            if series_format == "Best of 3 (Bo3)":
                score_2_0 = p ** 2
                score_2_1 = 2 * (p ** 2) * q
                score_1_2 = 2 * (q ** 2) * p
                score_0_2 = q ** 2

                team_a_series_win = (score_2_0 + score_2_1) * 100
                team_b_series_win = (score_1_2 + score_0_2) * 100

                spread_a_minus15 = score_2_0 * 100
                spread_b_plus15 = (100 - spread_a_minus15)

                over_25_maps = (score_2_1 + score_1_2) * 100
                under_25_maps = (score_2_0 + score_0_2) * 100

                st.write("### 1. Moneyline (Series Winner)")
                m1, m2 = st.columns(2)
                m1.metric(f"{team_a} Win", f"{team_a_series_win:.1f}%", f"{int(team_a_series_win)}¢")
                m2.metric(f"{team_b} Win", f"{team_b_series_win:.1f}%", f"{int(team_b_series_win)}¢")

                st.write("### 2. Map Spreads (-1.5 / +1.5)")
                s1, s2 = st.columns(2)
                s1.metric(f"{team_a} -1.5 Maps (2-0)", f"{spread_a_minus15:.1f}%", f"{int(spread_a_minus15)}¢")
                s2.metric(f"{team_b} +1.5 Maps (Win ≥ 1 Map)", f"{spread_b_plus15:.1f}%", f"{int(spread_b_plus15)}¢")

                st.write("### 3. Total Maps (Over / Under 2.5)")
                t1, t2 = st.columns(2)
                t1.metric("Over 2.5 Maps (Goes to Decider)", f"{over_25_maps:.1f}%", f"{int(over_25_maps)}¢")
                t2.metric("Under 2.5 Maps (2-0 Sweep)", f"{under_25_maps:.1f}%", f"{int(under_25_maps)}¢")

                st.write("### 4. Correct Score Probabilities")
                sc1, sc2, sc3, sc4 = st.columns(4)
                sc1.metric("2 - 0", f"{score_2_0*100:.1f}%")
                sc2.metric("2 - 1", f"{score_2_1*100:.1f}%")
                sc3.metric("1 - 2", f"{score_1_2*100:.1f}%")
                sc4.metric("0 - 2", f"{score_0_2*100:.1f}%")

            # BO5 MARKOV ENGINE
            else:
                score_3_0 = p ** 3
                score_3_1 = 3 * (p ** 3) * q
                score_3_2 = 6 * (p ** 3) * (q ** 2)
                score_2_3 = 6 * (q ** 3) * (p ** 2)
                score_1_3 = 3 * (q ** 3) * p
                score_0_3 = q ** 3

                team_a_series_win = (score_3_0 + score_3_1 + score_3_2) * 100
                team_b_series_win = (score_2_3 + score_1_3 + score_0_3) * 100

                spread_a_minus15 = (score_3_0 + score_3_1) * 100
                over_35_maps = (score_3_1 + score_3_2 + score_2_3 + score_1_3) * 100
                over_45_maps = (score_3_2 + score_2_3) * 100

                st.write("### 1. Moneyline (Series Winner)")
                m1, m2 = st.columns(2)
                m1.metric(f"{team_a} Win", f"{team_a_series_win:.1f}%", f"{int(team_a_series_win)}¢")
                m2.metric(f"{team_b} Win", f"{team_b_series_win:.1f}%", f"{int(team_b_series_win)}¢")

                st.write("### 2. Map Spreads & Totals")
                s1, s2, s3 = st.columns(3)
                s1.metric(f"{team_a} -1.5 Maps", f"{spread_a_minus15:.1f}%", f"{int(spread_a_minus15)}¢")
                s2.metric("Over 3.5 Maps", f"{over_35_maps:.1f}%", f"{int(over_35_maps)}¢")
                s3.metric("Over 4.5 Maps (Full 5)", f"{over_45_maps:.1f}%", f"{int(over_45_maps)}¢")

                st.write("### 3. Correct Score Probabilities")
                sc1, sc2, sc3 = st.columns(3)
                sc1.metric("3 - 0", f"{score_3_0*100:.1f}%")
                sc2.metric("3 - 1", f"{score_3_1*100:.1f}%")
                sc3.metric("3 - 2", f"{score_3_2*100:.1f}%")

                sc4, sc5, sc6 = st.columns(3)
                sc4.metric("2 - 3", f"{score_2_3*100:.1f}%")
                sc5.metric("1 - 3", f"{score_1_3*100:.1f}%")
                sc6.metric("0 - 3", f"{score_0_3*100:.1f}%")
