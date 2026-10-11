import streamlit as st
import pandas as pd
import numpy as np
import math
import json
import requests
from io import StringIO

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & HIGH-CONTRAST DARK THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="APEX ANALYTICS PRO | AI Odds Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast CSS
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
    "382": ["Man City", "Manchester City"],
    "360": ["Man United", "Manchester United"],
    "359": ["Arsenal"],
    "364": ["Liverpool"],
    "363": ["Chelsea"],
    "367": ["Tottenham", "Spurs"],
    "362": ["Aston Villa"],
    "361": ["Newcastle"],
    "331": ["Brighton"],
    "371": ["West Ham"],
    "368": ["Everton"],
    "370": ["Fulham"],
    "337": ["Brentford"],
    "349": ["Bournemouth"],
    "384": ["Crystal Palace"],
    "380": ["Wolves", "Wolverhampton"],
    "393": ["Nott'm Forest", "Nottingham"],
    "375": ["Leicester"],
    "373": ["Ipswich"],
    "376": ["Southampton"],
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
    # Search Football Teams
    for id_code, aliases in FOOTBALL_LOGOS.items():
        if any(alias.lower() in team_name.lower() or team_name.lower() in alias.lower() for alias in aliases):
            return f"https://a.espncdn.com/i/teamlogos/soccer/500/{id_code}.png"
            
    # Search Esports Teams
    for id_code, aliases in ESPORTS_LOGOS.items():
        if any(alias.lower() in team_name.lower() or team_name.lower() in alias.lower() for alias in aliases):
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
# 5. FOOTBALL ENGINE
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
        {"HomeTeam": "Man United", "AwayTeam": "Spurs", "FTHG": 1, "FTAG": 0},
        {"HomeTeam": "Aston Villa", "AwayTeam": "Newcastle", "FTHG": 3, "FTAG": 1},
        {"HomeTeam": "Arsenal", "AwayTeam": "Liverpool", "FTHG": 1, "FTAG": 1},
        {"HomeTeam": "Man City", "AwayTeam": "Chelsea", "FTHG": 3, "FTAG": 0},
        {"HomeTeam": "Brighton", "AwayTeam": "West Ham", "FTHG": 2, "FTAG": 0},
        {"HomeTeam": "Everton", "AwayTeam": "Fulham", "FTHG": 1, "FTAG": 1},
        {"HomeTeam": "Bournemouth", "AwayTeam": "Brentford", "FTHG": 2, "FTAG": 1},
        {"HomeTeam": "Crystal Palace", "AwayTeam": "Wolves", "FTHG": 0, "FTAG": 0},
        {"HomeTeam": "Nott'm Forest", "AwayTeam": "Leicester", "FTHG": 2, "FTAG": 1}
    ])

    @st.cache_data(ttl=1800)
    def load_football_data_safe(code):
        url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
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
        home_t =
