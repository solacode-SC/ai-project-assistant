# src/utils.py
import streamlit as st
from pathlib import Path

def set_page_config():
    st.set_page_config(page_title="AI Project Assistant", page_icon="🤖", layout="wide")

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; background: linear-gradient(180deg,#f8fafc,#eef2ff); }
    .metric-card { background: #fff; padding:12px; border-radius:10px; box-shadow: 0 6px 18px rgba(15,23,42,0.06); }
    .stButton>button { border-radius:8px; }
    </style>
    """, unsafe_allow_html=True)

def style_metric_card(label, value, trend=None, color="#10b981"):
    st.markdown(f"""
    <div class="metric-card">
      <div style="color:#6b7280;font-weight:600">{label}</div>
      <div style="font-size:22px;font-weight:800;color:{color}">{value}</div>
      <div style="color:#94a3b8">{trend or ''}</div>
    </div>
    """, unsafe_allow_html=True)

def save_df_to_excel(df, path: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(p, index=False)
    return p
