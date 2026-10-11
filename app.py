import streamlit as st
import pandas as pd
import numpy as np
import math
import json
import requests

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & HIGH-CONTRAST DARK THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="APEX ANALYTICS PRO | AI Odds Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast Glassmorphism CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #080a0f 60%, #030712 100%);
    }
    
    /* High-Contrast Readability Rules */
    p, span, label, [data-testid="stWidgetLabel"] p {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 24px 32px;
        backdrop-filter: blur(16px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        margin-bottom: 28px;
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
        letter-spacing: -0.5px;
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

    /* VS Matchup Header Card */
    .vs-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.75));
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 20px;
        padding: 28px;
        text-align: center;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
    }
    .team-logo-img {
        width: 90px;
        height: 90px;
        object-fit: contain;
        filter: drop-shadow(0px 6px 15px rgba(0, 0, 0, 0.6));
    }

    /* Tabs Styling */
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

    /* Primary Action Buttons */
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
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(56, 189, 248, 0.5);
    }

    /* Exact Score Cards */
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
# 2. LOGO MAPPING & HELPER UTILITIES
# ---------------------------------------------------------
def get_team_logo(team_name):
    logo_map = {
        # Football (Premier League & Top Europe)
        "Man City": "https://a.espncdn.com/i/teamlogos/soccer/500/382.png",
        "Manchester City": "https://a.espncdn.com/i/teamlogos/soccer/500/382.png",
        "Man United": "https://a.espncdn.com/i/teamlogos/soccer/500/360.png",
        "Manchester United": "https://a.espncdn.com/i/teamlogos/soccer/500/360.png",
        "Arsenal": "https://a.espncdn.com/i/teamlogos/soccer/500/359.png",
        "Liverpool": "https://a.espncdn.com/i/teamlogos/soccer/500/364.png",
        "Chelsea": "https://a.espncdn.com/i/teamlogos/soccer/500/363.png",
        "Tottenham": "https://a.espncdn.com/i/teamlogos/soccer/500/367.png",
        "Spurs": "https://a.espncdn.com/i/teamlogos/soccer/500/367.png",
        "Aston Villa": "https://a.espncdn.com/i/teamlogos/soccer/500/362.png",
        "Newcastle": "https://a.espncdn.com/i/teamlogos/soccer/500/361.png",
        "Brighton": "https://a.espncdn.com/i/teamlogos/soccer/500/331.png",
        "West Ham": "https://a.espncdn.com/i/teamlogos/soccer/500/371.png",
        "Everton": "https://a.espncdn.com/i/teamlogos/soccer/500/368.png",
        "Fulham": "https://a.espncdn.com/i/teamlogos/soccer/500/370.png",
        "Brentford": "https://a.espncdn.com/i/teamlogos/soccer/500/337.png",
        "Bournemouth": "https://a.espncdn.com/i/teamlogos/soccer/500/349.png",
        "Crystal Palace": "https://a.espncdn.com/i/teamlogos/soccer/500/384.png",
        "Wolves": "https://a.espncdn.com/i/teamlogos/soccer/500/380.png",
        "Nott'm Forest": "https://a.espncdn.com/i/teamlogos/soccer/500/393.png",
        "Real Madrid": "https://a.espncdn.com/i/teamlogos/soccer/500/86.png",
        "Barcelona": "https://a.espncdn.com/i/teamlogos/soccer/500/83.png",

        # LoL Worlds 2026 Qualified Teams
        "Gen.G": "https://a.espncdn.com/i/teamlogos/eSports/500/305.png",
        "Hanwha Life Esports": "https://a.espncdn.com/i/teamlogos/eSports/500/310.png",
        "T1": "https://a.espncdn.com/i/teamlogos/eSports/500/300.png",
        "Dplus KIA": "https://a.espncdn.com/i/teamlogos/eSports/500/304.png",
        "Bilibili Gaming (BLG)": "https://a.espncdn.com/i/teamlogos/eSports/500/331.png",
        "Top Esports (TES)": "https://a.espncdn.com/i/teamlogos/eSports/500/332.png",
        "Invictus Gaming (iG)": "https://a.espncdn.com/i/teamlogos/eSports/500/325.png",
        "G2 Esports": "https://a.espncdn.com/i/teamlogos/eSports/500/222.png",
        "Team Liquid Alienware": "https://a.espncdn.com/i/teamlogos/eSports/500/209.png",
        "Cloud9": "https://a.espncdn.com/i/teamlogos/eSports/500/202.png",

        # CS2 & Valorant
        "Team Spirit": "https://a.espncdn.com/i/teamlogos/eSports/500/350.png",
        "Team Vitality": "https://a.espncdn.com/i/teamlogos/eSports/500/255.png",
        "FaZe Clan": "https://a.espncdn.com/i/teamlogos/eSports/500/210.png",
        "Natus Vincere (NAVI)": "https://a.espncdn.com/i/teamlogos/eSports/500/201.png",
        "Paper Rex": "https://a.espncdn.com/i/teamlogos/eSports/500/360.png",
        "Fnatic": "https://a.espncdn.com/i/teamlogos/eSports/500/203.png",
        "100 Thieves": "https://a.espncdn.com/i/teamlogos/eSports/500/230.png",
        "NRG": "https://a.espncdn.com/i/teamlogos/eSports/500/220.png"
    }

    if team_name in logo_map:
        return logo_map[team_name]
    
    for key, url in logo_map.items():
        if key.lower() in team_name.lower() or team_name.lower() in key.lower():
            return url

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

#
