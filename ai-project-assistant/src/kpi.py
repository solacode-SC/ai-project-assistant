# src/kpi.py
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

@st.cache_data
def calculate_kpis(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {"total":0,"completed":0,"in_progress":0,"blocked":0,"overdue":0,"completion_rate":0.0,"velocity":0}
    total = len(df)
    completed = int((df["Status"].astype(str).str.lower() == "done").sum())
    in_progress = int((df["Status"].astype(str).str.lower() == "in progress").sum())
    blocked = int((df["Status"].astype(str).str.lower() == "blocked").sum())
    velocity = int(pd.to_numeric(df["Story Points"], errors="coerce").fillna(0).sum())
    now = pd.Timestamp.now()
    overdue = int(((df["Due Date"].notna()) & (df["Due Date"] < now) & (df["Status"].astype(str).str.lower() != "done")).sum())
    completion_rate = round((completed / total * 100), 2) if total else 0.0
    return {
        "total":total, "completed":completed, "in_progress":in_progress,
        "blocked":blocked, "overdue":overdue, "completion_rate":completion_rate, "velocity":velocity
    }

def display_kpi_dashboard():
    df = st.session_state.get("project_data", None)
    kpis = calculate_kpis(df) if df is not None else None

    if not kpis:
        st.info("Upload data to view KPIs")
        return

    # Metric cards
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("✅ Completed", kpis["completed"], f"{kpis['completion_rate']:.1f}%")
    c2.metric("🔄 In Progress", kpis["in_progress"])
    c3.metric("⚠️ Blocked", kpis["blocked"])
    c4.metric("📅 Overdue", kpis["overdue"])

    # Burndown simulation
    st.markdown("### 📈 Burndown (simulated)")
    total_points = int(df["Story Points"].sum()) if "Story Points" in df.columns else 0
    if total_points > 0:
        dates = pd.date_range(pd.Timestamp.now() - pd.Timedelta(days=30), periods=40)
        ideal = [total_points - (total_points * i / (len(dates)-1)) for i in range(len(dates))]
        actual = ideal.copy()
        fig = px.line(x=dates, y=[ideal, actual], labels={"x":"Date", "value":"Remaining SP"}, title="Burndown (ideal vs actual)")
        st.plotly_chart(fig, use_container_width=True)

def render_gantt_timeline(df: pd.DataFrame):
    # Uses Plotly timeline
    if df is None or df.empty:
        st.info("No data for timeline")
        return
    if "Due Date" not in df.columns or "Created Date" not in df.columns:
        st.warning("Missing Created Date / Due Date columns for timeline")
        return
    df_t = df.copy()
    # start = Created Date, end = Due Date
    df_t = df_t.dropna(subset=["Created Date","Due Date"])
    if df_t.empty:
        st.info("No rows with both Created Date and Due Date")
        return
    fig = px.timeline(df_t, x_start="Created Date", x_end="Due Date", y="Assignee", color="Priority", hover_data=["Task","Status"])
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=600, template="plotly_white", title="Project Timeline")
    st.plotly_chart(fig, use_container_width=True)
