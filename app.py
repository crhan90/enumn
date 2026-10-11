import streamlit as st
import pandas as pd
import numpy as np
import math
import json
import requests

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & CLEAN DARK THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="APEX ANALYTICS PRO | AI Odds Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-Contrast Glassmorphism Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #080a0f 65%, #030712 100%);
        color: #f8fafc;
    }
    
    /* Ensure high contrast for all text elements */
    .stMarkdown, .stText, label, p, span {
        color: #e2e8f0 !important;
    }
    
    /* Hero Header */
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

    /* VS Matchup Header Card */
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

    /* Action Buttons */
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
# 2. EMBLEM & LOGO MAPPER
# ---------------------------------------------------------
def get_team_logo(team_name):
    logo_map = {
        # Premier League
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
        "Crystal Palace": "
