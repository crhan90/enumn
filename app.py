import streamlit as st
import pandas as pd
import numpy as np
import math

# 1. Page Configuration & Custom CSS Injection
st.set_page_config(
    page_title="APEX Analytics | AI Sports & Esports Odds Engine",
    page_icon="⚡",
    layout="centered"
)

# Premium Dark Glassmorphism Styling
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background-color: #0b0e14;
    }
    h1, h2, h3, h4, label {
        color: #f1f5f9 !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* VS Banner Styling */
    .vs-banner {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
    }
    
    /* Team Logo Circle */
    .team-logo-img {
        width: 72px;
        height: 72px;
        object-fit: contain;
        filter: drop-shadow(0px 4px 10px rgba(0, 0, 0, 0.5));
    }
    
    /* Custom Market Metric Card */
    .market-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #38bdf8;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 12px;
    }
    
    .odd-pill {
        background: #0ea5e9;
        color: white;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    /* Progress Bar custom style */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #3b82f6 , #06b6d4);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOGO MAPPING HELPER
# ---------------------------------------------------------
def get_team_logo(team_name):
    # Reliable CDN logos with fallback to dynamic UI avatars
    logo_map = {
        # Football
        "Arsenal": "https://a.espncdn.com/i/teamlogos/soccer/500/359.png",
        "Chelsea": "https://a.espncdn.com/i/teamlogos/soccer/500/363.png",
        "Liverpool": "https://a.espncdn.com/i/teamlogos/soccer/500/364.png",
        "Manchester City": "https://a.espncdn.com/i/teamlogos/soccer/500/382.png",
        "Manchester United": "https://a.espncdn.com/i/teamlogos/soccer/500/360.png",
        "Tottenham": "https://a.espncdn.com/i/teamlogos/soccer/500/367.png",
        "Real Madrid": "https://a.espncdn.com/i/teamlogos/soccer/500/86.png",
        "Barcelona": "https://a.espncdn.com/i/teamlogos/soccer/500/83.png",
        # LoL
        "T1": "https://a.espncdn.com/i/teamlogos/eSports/500/300.png",
        "Gen.G": "https://a.espncdn.com/i/teamlogos/eSports/500/305.png",
        "Bilibili Gaming (BLG)": "https://a.espncdn.com/i/teamlogos/eSports/500/331.png",
        "Top Esports (TES)": "https://a.espncdn.com/i/teamlogos/eSports/500/332.png",
        "G2 Esports": "https://a.espncdn.com/i/teamlogos/eSports/500/222.png",
        "Fnatic": "https://a.espncdn.com/i/teamlogos/eSports/500/203.png",
        "Hanwha Life Esports": "https://a.espncdn.com/i/teamlogos/eSports/500/310.png",
        "KT Rolster": "https://a.espncdn.com/i/teamlogos/eSports/500/301.png",
        # CS2 / Valorant
        "Team Spirit": "https://a.espncdn.com/i/teamlogos/eSports/500/350.png",
        "Team Vitality": "https://a.espncdn.com/i/teamlogos/eSports/500/255.png",
        "FaZe Clan": "https://a.espncdn.com/i/teamlogos/eSports/500/210.png",
        "Natus Vincere (NAVI)": "https://a.espncdn.com/i/teamlogos/eSports/500/201.png",
        "Paper Rex": "https://a.espncdn.com/i/teamlogos/eSports/500/360.png"
    }
    
    if team_name in logo_map:
        return logo_map[team_name]
    
    # Clean fallback text badge generator
    clean_name = team_name.split('(')[0].strip().replace(" ", "+")
    return f"https://ui-avatars.com/api/?name={clean_name}&background=1e293b&color=38bdf8&size=128&bold=true"

# ---------------------------------------------------------
# HEADER & NAVIGATION
# ---------------------------------------------------------
st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>⚡ APEX ANALYTICS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.95rem; margin-bottom: 25px;'>Next-Gen Predictive Odds Engine • Sports & Esports</p>", unsafe_allow_html=True)

tab_foot, tab_val, tab_cs, tab_lol = st.tabs(["⚽ Football", "🎯 VALORANT", "🔫 Counter-Strike 2", "⚔️ League of Legends"])

# ---------------------------------------------------------
# 1. FOOTBALL ENGINE
# ---------------------------------------------------------
with tab_foot:
    LEAGUES = {
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League (2026/2027)": "E0",
        "🏆 UEFA Nations League / National Teams": "INTERNATIONAL",
        "🇪🇸 Spanish La Liga": "SP1",
        "🇮🇹 Italian Serie A": "I1",
        "🇩🇪 German Bundesliga": "D1",
        "🇫🇷 French Ligue 1": "F1"
    }

    selected_league = st.selectbox("Select Competition", list(LEAGUES.keys()), key="foot_league")
    league_code = LEAGUES[selected_league]

    @st.cache_data(ttl=3600)
    def load_football_data(code):
        if code == "INTERNATIONAL":
            url = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
            df = pd.read_csv(url)
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] >= '2022-01-01'].copy()
            df.rename(columns={'home_team': 'HomeTeam', 'away_team': 'AwayTeam', 'home_score': 'FTHG', 'away_score': 'FTAG'}, inplace=True)
            return df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].dropna()
        else:
            seasons = ['2627', '2526']
            dfs = []
            for s in seasons:
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/{s}/{code}.csv"
                    tdf = pd.read_csv(url)
                    if 'HomeTeam' in tdf.columns and len(tdf) > 0:
                        dfs.append(tdf[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']])
                except Exception:
                    continue
            if dfs:
                return pd.concat(dfs, ignore_index=True).dropna()
            raise ValueError("Match data temporarily unavailable.")

    try:
        df_foot = load_football_data(league_code)
        teams_foot = sorted(list(set(df_foot['HomeTeam'].unique()).union(set(df_foot['AwayTeam'].unique()))))

        c1, c2 = st.columns(2)
        with c1:
            home_t = st.selectbox("Home Team", teams_foot, index=0, key="f_home")
        with c2:
            away_t = st.selectbox("Away Team", teams_foot, index=1 if len(teams_foot) > 1 else 0, key="f_away")

        if home_t != away_t:
            # Render Matchup Header Card with Logos
            logo_h = get_team_logo(home_t)
            logo_a = get_team_logo(away_t)

            st.markdown(f"""
            <div class="vs-banner">
                <div style="display: flex; justify-content: space-around; align-items: center;">
                    <div style="text-align: center;">
                        <img src="{logo_h}" class="team-logo-img"><br>
                        <strong style="font-size: 1.1rem; color: #f8fafc;">{home_t}</strong><br>
                        <span style="color: #64748b; font-size: 0.8rem;">HOME</span>
                    </div>
                    <div>
                        <span style="font-size: 1.8rem; font-weight: 800; color: #38bdf8;">VS</span>
                    </div>
                    <div style="text-align: center;">
                        <img src="{logo_a}" class="team-logo-img"><br>
                        <strong style="font-size: 1.1rem; color: #f8fafc;">{away_t}</strong><br>
                        <span style="color: #64748b; font-size: 0.8rem;">AWAY</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Calculate Football Odds", type="primary", use_container_width=True):
                # Calculations
                hg = df_foot[df_foot['HomeTeam'] == home_t]
                ag = df_foot[df_foot['AwayTeam'] == away_t]
                avg_h = df_foot['FTHG'].mean() or 1.35
                avg_a = df_foot['FTAG'].mean() or 1.10

                h_att = (hg['FTHG'].mean() if len(hg) > 0 else avg_h) / avg_h
                h_def = (hg['FTAG'].mean() if len(hg) > 0 else avg_a) / avg_a
                a_att = (ag['FTAG'].mean() if len(ag) > 0 else avg_a) / avg_a
                a_def = (ag['FTHG'].mean() if len(ag) > 0 else avg_h) / avg_h

                exp_h = h_att * a_def * avg_h
                exp_a = a_att * h_def * avg_a

                max_g = 8
                prob_m = np.zeros((max_g, max_g))
                for i in range(max_g):
                    for j in range(max_g):
                        p_i = (exp_h**i * np.exp(-exp_h)) / math.factorial(i)
                        p_j = (exp_a**j * np.exp(-exp_a)) / math.factorial(j)
                        prob_m[i, j] = p_i * p_j
                prob_m /= prob_m.sum()

                home_win = np.sum(np.tril(prob_m, -1)) * 100
                draw = np.sum(np.diag(prob_m)) * 100
                away_win = np.sum(np.triu(prob_m, 1)) * 100

                cover_15 = sum(prob_m[i, j] for i in range(max_g) for j in range(max_g) if i - j >= 2) * 100
                over_25 = sum(prob_m[i, j] for i in range(max_g) for j in range(max_g) if i + j > 2.5) * 100
                btts_yes = np.sum(prob_m[1:, 1:]) * 100

                st.subheader("📊 Match Result Odds (Moneyline)")
                m1, m2, m3 = st.columns(3)
                m1.metric(f"{home_t} Win", f"{home_win:.1f}%", f"{int(home_win)}¢")
                m2.metric("Draw", f"{draw:.1f}%", f"{int(draw)}¢")
                m3.metric(f"{away_t} Win", f"{away_win:.1f}%", f"{int(away_win)}¢")

                # Visual probability bar
                st.write("**Win Probability Bar**")
                st.progress(int(home_win))

                st.subheader("🎯 Primary Betting Markets")
                s1, s2, s3 = st.columns(3)
                s1.metric(f"{home_t} -1.5 Spread", f"{cover_15:.1f}%", f"{int(cover_15)}¢")
                s2.metric("Over 2.5 Total Goals", f"{over_25:.1f}%", f"{int(over_25)}¢")
                s3.metric("Both Teams Score (BTTS)", f"{btts_yes:.1f}%", f"{int(btts_yes)}¢")

    except Exception as e:
        st.error(f"Unable to load data: {e}")

# ---------------------------------------------------------
# 2. ESPORTS ENGINE (VALORANT, CS2, LOL)
# ---------------------------------------------------------
def render_esports_tab(sport_name, tournament_name, teams_dict, tab_key):
    st.caption(f"🏆 Active Tournament: **{tournament_name}**")
    
    teams_list = sorted(list(teams_dict.keys()))
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        t_a = st.selectbox("Team A", teams_list, index=0, key=f"{tab_key}_a")
    with col2:
        t_b = st.selectbox("Team B", teams_list, index=1 if len(teams_list) > 1 else 0, key=f"{tab_key}_b")
    with col3:
        fmt = st.selectbox("Format", ["Bo3", "Bo5"], key=f"{tab_key}_fmt")

    if t_a != t_b:
        logo_a = get_team_logo(t_a)
        logo_b = get_team_logo(t_b)

        # VS Header Banner
        st.markdown(f"""
        <div class="vs-banner">
            <div style="display: flex; justify-content: space-around; align-items: center;">
                <div style="text-align: center;">
                    <img src="{logo_a}" class="team-logo-img"><br>
                    <strong style="font-size: 1.1rem; color: #f8fafc;">{t_a}</strong>
                </div>
                <div>
                    <span style="font-size: 1.8rem; font-weight: 800; color: #38bdf8;">VS</span><br>
                    <span style="color: #64748b; font-size: 0.75rem;">{fmt} MATCH</span>
                </div>
                <div style="text-align: center;">
                    <img src="{logo_b}" class="team-logo-img"><br>
                    <strong style="font-size: 1.1rem; color: #f8fafc;">{t_b}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🚀 Predict {sport_name} Series", type="primary", use_container_width=True, key=f"{tab_key}_btn"):
            elo_a = teams_dict[t_a]
            elo_b = teams_dict[t_b]
            
            p = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
            q = 1 - p

            st.write(f"**Single Map Win Rate:** `{t_a}` **{p*100:.1f}%** vs **{q*100:.1f}%** `{t_b}`")
            st.progress(int(p * 100))

            st.markdown("---")

            if fmt == "Bo3":
                s_2_0 = p ** 2
                s_2_1 = 2 * (p ** 2) * q
                s_1_2 = 2 * (q ** 2) * p
                s_0_2 = q ** 2

                win_a = (s_2_0 + s_2_1) * 100
                win_b = (s_1_2 + s_0_2) * 100
                over_25 = (s_2_1 + s_1_2) * 100

                st.subheader("📊 Match Winner (Moneyline)")
                m1, m2 = st.columns(2)
                m1.metric(f"{t_a} Series Win", f"{win_a:.1f}%", f"{int(win_a)}¢")
                m2.metric(f"{t_b} Series Win", f"{win_b:.1f}%", f"{int(win_b)}¢")

                st.subheader("🎯 Spreads & Total Maps")
                p1, p2 = st.columns(2)
                p1.metric(f"{t_a} -1.5 Map Sweep (2-0)", f"{s_2_0*100:.1f}%", f"{int(s_2_0*100)}¢")
                p2.metric("Over 2.5 Maps (Goes to Map 3)", f"{over_25:.1f}%", f"{int(over_25)}¢")

                st.subheader("🎲 Exact Series Score")
                sc1, sc2, sc3, sc4 = st.columns(4)
                sc1.metric("2 - 0", f"{s_2_0*100:.1f}%")
                sc2.metric("2 - 1", f"{s_2_1*100:.1f}%")
                sc3.metric("1 - 2", f"{s_1_2*100:.1f}%")
                sc4.metric("0 - 2", f"{s_0_2*100:.1f}%")

            else:
                s_3_0 = p ** 3
                s_3_1 = 3 * (p ** 3) * q
                s_3_2 = 6 * (p ** 3) * (q ** 2)
                s_2_3 = 6 * (q ** 3) * (p ** 2)
                s_1_3 = 3 * (q ** 3) * p
                s_0_3 = q ** 3

                win_a = (s_3_0 + s_3_1 + s_3_2) * 100
                win_b = (s_2_3 + s_1_3 + s_0_3) * 100
                over_35 = (s_3_1 + s_3_2 + s_2_3 + s_1_3) * 100

                st.subheader("📊 Match Winner (Moneyline)")
                m1, m2 = st.columns(2)
                m1.metric(f"{t_a} Series Win", f"{win_a:.1f}%", f"{int(win_a)}¢")
                m2.metric(f"{t_b} Series Win", f"{win_b:.1f}%", f"{int(win_b)}¢")

                st.subheader("🎯 Spreads & Totals")
                p1, p2 = st.columns(2)
                p1.metric(f"{t_a} -1.5 Map Spread", f"{(s_3_0+s_3_1)*100:.1f}%")
                p2.metric("Over 3.5 Total Maps", f"{over_35:.1f}%")

                st.subheader("🎲 Exact Series Score")
                c_a, c_b = st.columns(2)
                with c_a:
                    st.write(f"**{t_a} Wins**")
                    st.write(f"• 3 - 0: **{s_3_0*100:.1f}%**")
                    st.write(f"• 3 - 1: **{s_3_1*100:.1f}%**")
                    st.write(f"• 3 - 2: **{s_3_2*100:.1f}%**")
                with c_b:
                    st.write(f"**{t_b} Wins**")
                    st.write(f"• 2 - 3: **{s_2_3*100:.1f}%**")
                    st.write(f"• 1 - 3: **{s_1_3*100:.1f}%**")
                    st.write(f"• 0 - 3: **{s_0_3*100:.1f}%**")

# VALORANT TAB
with tab_val:
    val_teams = {
        "Paper Rex": 1850, "G2 Esports": 1820, "100 Thieves": 1780, "Team Vitality": 1810,
        "NRG": 1790, "FUT Esports": 1750, "Fnatic": 1830, "LOUD": 1770,
        "EDward Gaming": 1800, "T1": 1760, "Nongshim RedForce": 1720, "Global Esports": 1680
    }
    render_esports_tab("VALORANT", "VALORANT Champions 2026", val_teams, "val")

# CS2 TAB
with tab_cs:
    cs_teams = {
        "Team Spirit": 1910, "Team Vitality": 1880, "FaZe Clan": 1840, "Natus Vincere (NAVI)": 1860,
        "MOUZ": 1830, "G2 Esports": 1820, "Team Falcons": 1850, "The MongolZ": 1790,
        "Astralis": 1760, "FURIA": 1750, "FUT Esports": 1740
    }
    render_esports_tab("Counter-Strike 2", "CS2 ESL Pro League / Major 2026", cs_teams, "cs")

# LEAGUE OF LEGENDS TAB
with tab_lol:
    lol_teams = {
        "Gen.G": 1920, "T1": 1900, "Hanwha Life Esports": 1880, "KT Rolster": 1800,
        "Bilibili Gaming (BLG)": 1890, "Top Esports (TES)": 1840, "JD Gaming (JDG)": 1830,
        "Weibo Gaming (WBG)": 1820, "LNG Esports": 1790, "Anyone's Legend (AL)": 1780,
        "Invictus Gaming (iG)": 1770, "Team WE": 1750, "FunPlus Phoenix (FPX)": 1740,
        "Natus Vincere (NAVI)": 1750, "Team Vitality": 1740, "G2 Esports": 1810,
        "FlyQuest": 1760, "Cloud9": 1770, "Team Liquid": 1760, "GAM Esports": 1720,
        "ZSM (Ale, Ning, FoFo, Lwx)": 1660, "FRK (fearness, Cryin, Smlz)": 1650
    }
    render_esports_tab("League of Legends", "Demacia Cup & Global Invitational (DCGI)", lol_teams, "lol")
