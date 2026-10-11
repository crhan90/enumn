import streamlit as st
import pandas as pd
import numpy as np
import math
import json
import requests
from io import StringIO

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & DARK THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="APEX ANALYTICS PRO | AI Odds Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #080a0f 65%, #030712 100%);
        color: #f8fafc;
    }
    
    .stMarkdown, .stText, label, p, span {
        color: #e2e8f0 !important;
    }
    
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 24px 32px;
        backdrop-filter: blur(16px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .status-badge {
        background: rgba(34, 197, 94, 0.2);
        border: 1px solid rgba(34, 197, 94, 0.5);
        color: #4ade80 !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem !important;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 10px #22c55e;
    }

    .vs-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.8));
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5);
        margin-bottom: 24px;
    }
    .team-logo-img {
        width: 90px;
        height: 90px;
        object-fit: contain;
        filter: drop-shadow(0px 6px 15px rgba(0, 0, 0, 0.6));
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.85);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        padding: 10px 22px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0284c7, #3b82f6) !important;
        border: 1px solid #38bdf8 !important;
        color: #ffffff !important;
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #0284c7 0%, #3b82f6 50%, #6366f1 100%);
        border: none;
        border-radius: 12px;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.3);
    }

    .score-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
    }
    .score-card-top {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.25), rgba(99, 102, 241, 0.25));
        border: 1.5px solid #38bdf8;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SHORT-ID EMBLEM & LOGO MAPPER
# ---------------------------------------------------------
FOOTBALL_LOGOS = {
    "359": ["Arsenal"],
    "362": ["Aston Villa"],
    "349": ["Bournemouth", "AFC Bournemouth"],
    "337": ["Brentford"],
    "331": ["Brighton"],
    "363": ["Chelsea"],
    "378": ["Coventry", "Coventry City"],
    "384": ["Crystal Palace"],
    "368": ["Everton"],
    "370": ["Fulham"],
    "306": ["Hull", "Hull City"],
    "373": ["Ipswich", "Ipswich Town"],
    "357": ["Leeds", "Leeds United"],
    "364": ["Liverpool"],
    "382": ["Man City", "Manchester City"],
    "360": ["Man United", "Manchester United"],
    "361": ["Newcastle", "Newcastle United"],
    "393": ["Nott'm Forest", "Nottingham Forest"],
    "366": ["Sunderland"],
    "367": ["Tottenham", "Spurs"],
    "86": ["Real Madrid"],
    "83": ["Barcelona"]
}

ESPORTS_LOGOS = {
    "305": ["Gen.G"],
    "310": ["Hanwha Life Esports"],
    "300": ["T1"],
    "304": ["Dplus KIA"],
    "331": ["Bilibili Gaming (BLG)"],
    "332": ["Top Esports (TES)"],
    "325": ["Invictus Gaming (iG)"],
    "222": ["G2 Esports"],
    "209": ["Team Liquid Alienware"],
    "202": ["Cloud9"],
    "350": ["Team Spirit"],
    "255": ["Team Vitality"],
    "210": ["FaZe Clan"],
    "201": ["Natus Vincere (NAVI)"],
    "360": ["Paper Rex"],
    "203": ["Fnatic"],
    "230": ["100 Thieves"],
    "220": ["NRG"]
}

def get_team_logo(team_name):
    for id_code, aliases in FOOTBALL_LOGOS.items():
        for alias in aliases:
            if alias.lower() in team_name.lower() or team_name.lower() in alias.lower():
                return f"https://a.espncdn.com/i/teamlogos/soccer/500/{id_code}.png"
            
    for id_code, aliases in ESPORTS_LOGOS.items():
        for alias in aliases:
            if alias.lower() in team_name.lower() or team_name.lower() in alias.lower():
                return f"https://a.espncdn.com/i/teamlogos/eSports/500/{id_code}.png"

    clean_name = team_name.split('(')[0].strip().replace(" ", "+")
    return f"https://ui-avatars.com/api/?name={clean_name}&background=0f172a&color=38bdf8&size=128&bold=true"

def convert_odds(prob, format_type):
    if prob <= 0:
        return "N/A"
    if format_type == "Decimal Odds":
        return f"{1 / prob:.2f}"
    elif format_type == "American Odds":
        if prob >= 0.5:
            return f"-{int((prob / (1 - prob)) * 100)}"
        else:
            return f"+{int(((1 - prob) / prob) * 100)}"
    return f"{prob * 100:.1f}% ({int(prob * 100)}¢)"

# ---------------------------------------------------------
# 3. SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.markdown("### ⚙️ Engine Settings")
odds_format = st.sidebar.selectbox("Odds Format Display", ["Probabilities (%) / Polymarket (¢)", "Decimal Odds", "American Odds"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 Bankroll Calculator")
bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10, value=1000, step=50)
fractional_kelly = st.sidebar.slider("Kelly Fraction", 0.1, 1.0, 0.25)

st.sidebar.markdown("---")
st.sidebar.caption("⚡ **APEX Engine v2.6** • Powered by Poisson xG & Markov Models")

# ---------------------------------------------------------
# 4. HERO HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div>
        <h1 class="hero-title">⚡ APEX ANALYTICS PRO</h1>
        <p style="color: #cbd5e1; margin: 4px 0 0 0; font-size: 0.95rem;">
            Multi-Market Predictive AI Engine for Global Sports & Esports
        </p>
    </div>
    <div class="status-badge">
        <div class="pulse-dot"></div> LIVE AI MODELS ACTIVE
    </div>
</div>
""", unsafe_allow_html=True)

tab_foot, tab_val, tab_cs, tab_lol, tab_poly = st.tabs([
    "⚽ Football (2026/27)", "🎯 VALORANT", "🔫 Counter-Strike 2", "⚔️ LoL Worlds 2026", "🌐 Live Polymarket Markets"
])

# ---------------------------------------------------------
# 5. FOOTBALL ENGINE (2026/2027 EPL TEAMS)
# ---------------------------------------------------------
with tab_foot:
    LEAGUES = {
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League (2026/2027)": "E0",
        "🇪🇸 Spanish La Liga": "SP1",
        "🇮🇹 Italian Serie A": "I1",
        "🇩🇪 German Bundesliga": "D1",
        "🇫🇷 French Ligue 1": "F1"
    }
    selected_league = st.selectbox("Select Competition", list(LEAGUES.keys()), key="foot_league")
    league_code = LEAGUES[selected_league]

    FALLBACK_EPL = pd.DataFrame([
        {"HomeTeam": "Arsenal", "AwayTeam": "Chelsea", "FTHG": 2, "FTAG": 1},
        {"HomeTeam": "Liverpool", "AwayTeam": "Man City", "FTHG": 2, "FTAG": 2},
        {"HomeTeam": "Man United", "AwayTeam": "Tottenham", "FTHG": 1, "FTAG": 1},
        {"HomeTeam": "Aston Villa", "AwayTeam": "Newcastle", "FTHG": 2, "FTAG": 2},
        {"HomeTeam": "Hull City", "AwayTeam": "Everton", "FTHG": 1, "FTAG": 0},
        {"HomeTeam": "Coventry City", "AwayTeam": "Sunderland", "FTHG": 2, "FTAG": 1},
        {"HomeTeam": "Leeds United", "AwayTeam": "Man United", "FTHG": 1, "FTAG": 2},
        {"HomeTeam": "Ipswich Town", "AwayTeam": "Fulham", "FTHG": 2, "FTAG": 1},
        {"HomeTeam": "Bournemouth", "AwayTeam": "Brentford", "FTHG": 2, "FTAG": 1},
        {"HomeTeam": "Crystal Palace", "AwayTeam": "Brighton", "FTHG": 0, "FTAG": 0},
        {"HomeTeam": "Nott'm Forest", "AwayTeam": "Arsenal", "FTHG": 1, "FTAG": 2}
    ])

    @st.cache_data(ttl=1800)
    def load_football_data_safe(code):
        url = f"https://www.football-data.co.uk/mmz4281/2627/{code}.csv"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200:
                df = pd.read_csv(StringIO(res.text))
                if 'HomeTeam' in df.columns and len(df) > 0:
                    return df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].dropna()
        except Exception:
            pass
        return FALLBACK_EPL

    df_foot = load_football_data_safe(league_code)
    teams_foot = sorted(list(set(df_foot['HomeTeam'].unique()).union(set(df_foot['AwayTeam'].unique()))))

    c1, c2 = st.columns(2)
    with c1:
        home_t = st.selectbox("Home Team", teams_foot, index=0, key="f_home")
    with c2:
        away_t = st.selectbox("Away Team", teams_foot, index=1 if len(teams_foot) > 1 else 0, key="f_away")

    if home_t != away_t:
        logo_h = get_team_logo(home_t)
        logo_a = get_team_logo(away_t)

        st.markdown(f"""
        <div class="vs-card">
            <div style="display: flex; justify-content: space-around; align-items: center;">
                <div style="text-align: center; flex: 1;">
                    <img src="{logo_h}" class="team-logo-img"><br>
                    <strong style="font-size: 1.25rem; color: #f8fafc; display: block; margin-top: 8px;">{home_t}</strong>
                    <span style="color: #38bdf8; font-size: 0.85rem; font-weight: 700;">HOME</span>
                </div>
                <div style="flex: 0.5;">
                    <span style="font-size: 2.4rem; font-weight: 900; background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">VS</span>
                </div>
                <div style="text-align: center; flex: 1;">
                    <img src="{logo_a}" class="team-logo-img"><br>
                    <strong style="font-size: 1.25rem; color: #f8fafc; display: block; margin-top: 8px;">{away_t}</strong>
                    <span style="color: #818cf8; font-size: 0.85rem; font-weight: 700;">AWAY</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 RUN FOOTBALL AI PREDICTION ENGINE", type="primary"):
            hg = df_foot[df_foot['HomeTeam'] == home_t]
            ag = df_foot[df_foot['AwayTeam'] == away_t]
            avg_h = df_foot['FTHG'].mean() if len(df_foot) > 0 else 1.35
            avg_a = df_foot['FTAG'].mean() if len(df_foot) > 0 else 1.10

            h_goals_for = hg['FTHG'].mean() if len(hg) > 0 else avg_h
            h_goals_against = hg['FTAG'].mean() if len(hg) > 0 else avg_a
            a_goals_for = ag['FTAG'].mean() if len(ag) > 0 else avg_a
            a_goals_against = ag['FTHG'].mean() if len(ag) > 0 else avg_h

            h_att = h_goals_for / avg_h
            h_def = h_goals_against / avg_a
            a_att = a_goals_for / avg_a
            a_def = a_goals_against / avg_h

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

            p_home = np.sum(np.tril(prob_m, -1))
            p_draw = np.sum(np.diag(prob_m))
            p_away = np.sum(np.triu(prob_m, 1))

            score_list = [((i, j), prob_m[i, j]) for i in range(max_g) for j in range(max_g)]
            score_list.sort(key=lambda x: x[1], reverse=True)
            top_scores = score_list[:4]

            cover_15 = sum(prob_m[i, j] for i in range(max_g) for j in range(max_g) if i - j >= 2)
            over_25 = sum(prob_m[i, j] for i in range(max_g) for j in range(max_g) if i + j > 2.5)
            btts_yes = np.sum(prob_m[1:, 1:])

            st.markdown("### 🎯 Predicted Exact Scorelines")
            sc_cols = st.columns(4)
            for idx, ((gh, ga), prob) in enumerate(top_scores):
                badge_class = "score-card score-card-top" if idx == 0 else "score-card"
                star = "★ MOST LIKELY" if idx == 0 else f"RANK #{idx+1}"
                sc_cols[idx].markdown(f"""
                <div class="{badge_class}">
                    <div style="font-size: 0.75rem; font-weight: 800; color: #38bdf8; margin-bottom: 4px;">{star}</div>
                    <div style="font-size: 1.8rem; font-weight: 800; color: #f8fafc;">{gh} - {ga}</div>
                    <div style="color: #cbd5e1; font-size: 0.9rem;">{prob*100:.1f}% Prob</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 📊 Win Probability Distribution")
            st.write(f"**{home_t} ({p_home*100:.1f}%)** vs **Draw ({p_draw*100:.1f}%)** vs **{away_t} ({p_away*100:.1f}%)**")
            st.progress(int(p_home * 100))

            st.markdown("### 💸 Moneyline Odds")
            m1, m2, m3 = st.columns(3)
            res1 = convert_odds(p_home, odds_format)
            res2 = convert_odds(p_draw, odds_format)
            res3 = convert_odds(p_away, odds_format)
            m1.metric(f"{home_t} Win", res1)
            m2.metric("Draw", res2)
            m3.metric(f"{away_t} Win", res3)

            st.markdown("### 🎲 Game Line Markets")
            s1, s2, s3 = st.columns(3)
            c15 = convert_odds(cover_15, odds_format)
            o25 = convert_odds(over_25, odds_format)
            btts = convert_odds(btts_yes, odds_format)
            s1.metric(f"{home_t} -1.5 Spread", c15)
            s2.metric("Over 2.5 Total Goals", o25)
            s3.metric("BTTS Yes", btts)

# ---------------------------------------------------------
# 6. ESPORTS ENGINE
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

        st.markdown(f"""
        <div class="vs-card">
            <div style="display: flex; justify-content: space-around; align-items: center;">
                <div style="text-align: center; flex: 1;">
                    <img src="{logo_a}" class="team-logo-img"><br>
                    <strong style="font-size: 1.25rem; color: #f8fafc; display: block; margin-top: 8px;">{t_a}</strong>
                </div>
                <div style="flex: 0.5;">
                    <span style="font-size: 2rem; font-weight: 900; color: #38bdf8;">VS</span><br>
                    <span style="color: #cbd5e1; font-size: 0.75rem; font-weight: 700;">{fmt} SERIES</span>
                </div>
                <div style="text-align: center; flex: 1;">
                    <img src="{logo_b}" class="team-logo-img"><br>
                    <strong style="font-size: 1.25rem; color: #f8fafc; display: block; margin-top: 8px;">{t_b}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🚀 RUN {sport_name.upper()} AI MARKOV ENGINE", type="primary", key=f"{tab_key}_btn"):
            elo_a = teams_dict[t_a]
            elo_b = teams_dict[t_b]
            p = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
            q = 1 - p

            st.markdown("### 📊 Map Win Rate Probability")
            st.write(f"**{t_a} ({p*100:.1f}%)** vs **{t_b} ({q*100:.1f}%)**")
            st.progress(int(p * 100))

            st.markdown("### 🎯 Series Moneyline")
            if fmt == "Bo3":
                s_2_0 = p ** 2
                s_2_1 = 2 * (p ** 2) * q
                s_1_2 = 2 * (q ** 2) * p
                s_0_2 = q ** 2
                p_win_a = s_2_0 + s_2_1
                p_win_b = s_1_2 + s_0_2

                m1, m2 = st.columns(2)
                va = convert_odds(p_win_a, odds_format)
                vb = convert_odds(p_win_b, odds_format)
                m1.metric(f"{t_a} Win Series", va)
                m2.metric(f"{t_b} Win Series", vb)

                st.markdown("### 🎲 Exact Series Score Probability Matrix")
                sc1, sc2, sc3, sc4 = st.columns(4)
                sc1.metric("2 - 0", convert_odds(s_2_0, odds_format))
                sc2.metric("2 - 1", convert_odds(s_2_1, odds_format))
                sc3.metric("1 - 2", convert_odds(s_1_2, odds_format))
                sc4.metric("0 - 2", convert_odds(s_0_2, odds_format))

            else:
                s_3_0 = p ** 3
                s_3_1 = 3 * (p ** 3) * q
                s_3_2 = 6 * (p ** 3) * (q ** 2)
                s_2_3 = 6 * (q ** 3) * (p ** 2)
                s_1_3 = 3 * (q ** 3) * p
                s_0_3 = q ** 3
                p_win_a = s_3_0 + s_3_1 + s_3_2
                p_win_b = s_2_3 + s_1_3 + s_0_3

                m1, m2 = st.columns(2)
                va = convert_odds(p_win_a, odds_format)
                vb = convert_odds(p_win_b, odds_format)
                m1.metric(f"{t_a} Win Series", va)
                m2.metric(f"{t_b} Win Series", vb)

                st.markdown("### 🎲 Exact Series Score Matrix")
                c_a, c_b = st.columns(2)
                with c_a:
                    st.write(f"**{t_a} Scores**")
                    st.write(f"• 3 - 0: **{convert_odds(s_3_0, odds_format)}**")
                    st.write(f"• 3 - 1: **{convert_odds(s_3_1, odds_format)}**")
                    st.write(f"• 3 - 2: **{convert_odds(s_3_2, odds_format)}**")
                with c_b:
                    st.write(f"**{t_b} Scores**")
                    st.write(f"• 2 - 3: **{convert_odds(s_2_3, odds_format)}**")
                    st.write(f"• 1 - 3: **{convert_odds(s_1_3, odds_format)}**")
                    st.write(f"• 0 - 3: **{convert_odds(s_0_3, odds_format)}**")

# VALORANT TAB
with tab_val:
    val_2026_teams = {
        "100 Thieves": 1860, "NRG": 1850, "Paper Rex": 1840, "Fnatic": 1830,
        "Team Vitality": 1820, "G2 Esports": 1810, "EDward Gaming": 1800, "DRX": 1790,
        "T1": 1780, "LOUD": 1770, "Karmine Corp": 1760, "Nongshim RedForce": 1750
    }
    render_esports_tab("VALORANT", "VALORANT Champions 2026 (Shanghai)", val_2026_teams, "val")

# CS2 TAB
with tab_cs:
    cs_2026_teams = {
        "Team Spirit": 1920, "Team Vitality": 1900, "Team Falcons": 1890,
        "Natus Vincere (NAVI)": 1870, "FaZe Clan": 1850, "MOUZ": 1840,
        "G2 Esports": 1830, "The MongolZ": 1810, "FURIA Esports": 1790,
        "Aurora Gaming": 1780, "Astralis": 1770, "PARIVISION": 1750
    }
    render_esports_tab("Counter-Strike 2", "CS2 ESL Pro League Season 24 / IEM 2026", cs_2026_teams, "cs")

# LEAGUE OF LEGENDS TAB
with tab_lol:
    lol_worlds_2026_teams = {
        "Gen.G": 1930, "Hanwha Life Esports": 1900, "T1": 1890, "Dplus KIA": 1820,
        "Anyone's Legend": 1880, "Bilibili Gaming (BLG)": 1870, "Top Esports (TES)": 1840, "Invictus Gaming (iG)": 1810,
        "G2 Esports": 1830, "Movistar KOI": 1780, "Karmine Corp": 1760,
        "Team Liquid Alienware": 1770, "Cloud9": 1760, "LYON": 1720, "CTBC Flying Oyster": 1730
    }
    render_esports_tab("League of Legends", "LoL World Championship 2026 (Worlds 2026)", lol_worlds_2026_teams, "lol")

# ---------------------------------------------------------
# 7. LIVE POLYMARKET FEEDS TAB
# ---------------------------------------------------------
with tab_poly:
    st.markdown("### 🌐 Live Polymarket Prediction Markets")
    st.caption("Real-time sports and esports prediction contracts fetched from Polymarket Gamma API")

    @st.cache_data(ttl=300)
    def fetch_live_polymarket_sports():
        url = "https://gamma-api.polymarket.com/events"
        tags = ["sports", "esports", "soccer", "league-of-legends", "cs2", "valorant"]
        fetched_ids = set()
        sports_events = []

        for tag in tags:
            try:
                res = requests.get(url, params={
                    "closed": "false", "active": "true", "tag_slug": tag,
                    "limit": 6, "order": "volume24hr", "ascending": "false"
                }, timeout=3)
                if res.status_code == 200:
                    for event in res.json():
                        e_id = event.get("id")
                        if e_id not in fetched_ids:
                            fetched_ids.add(e_id)
                            sports_events.append(event)
            except Exception:
                continue
        return sports_events

    if st.button("🔄 Refresh Live Polymarket Odds", key="poly_ref"):
        st.cache_data.clear()

    live_events = fetch_live_polymarket_sports()

    if not live_events:
        st.info("No active sports markets found right now on Polymarket.")
    else:
        for event in live_events[:8]:
            title = event.get("title", "")
            vol = float(event.get("volume24hr", 0))
            slug = event.get("slug", "")
            trade_url = f"https://polymarket.com/event/{slug}"

            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.65); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 14px; padding: 18px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #38bdf8; font-weight: 700; font-size: 0.8rem;">🔴 LIVE POLYMARKET CONTRACT</span>
                    <span style="color: #cbd5e1; font-size: 0.8rem; font-weight: 600;">24h Vol: ${vol:,.0f}</span>
                </div>
                <h4 style="margin: 8px 0; color: #f8fafc;">{title}</h4>
            </div>
            """, unsafe_allow_html=True)

            for m in event.get("markets", []):
                if m.get("active") and not m.get("closed"):
                    outcomes = json.loads(m.get("outcomes", "[]"))
                    prices = [float(p) for p in json.loads(m.get("outcomePrices", "[]"))]

                    if len(outcomes) >= 2 and len(prices) >= 2:
                        col1, col2, col3 = st.columns([2, 2, 1])
                        col1.metric(outcomes[0], f"{prices[0]*100:.1f}%", f"{int(prices[0]*100)}¢")
                        col2.metric(outcomes[1], f"{prices[1]*100:.1f}%", f"{int(prices[1]*100)}¢")
                        col3.link_button("Trade on Polymarket ↗", trade_url)
