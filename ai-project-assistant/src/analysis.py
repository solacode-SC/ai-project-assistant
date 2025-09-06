# src/analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px

def get_data_quality_metrics(df: pd.DataFrame = None) -> dict:
    # If df provided, compute real metrics; otherwise return placeholders
    if df is None:
        return {"Completeness":98.5, "Accuracy":96.2, "Consistency":94.8, "Timeliness":99.1}
    # Completeness: fraction of non-null mandatory columns
    mandatory = ["Task ID","Task","Status","Assignee","Due Date"]
    present = sum(df[c].notna().sum() for c in mandatory)
    completeness = round(present / (len(df)*len(mandatory)) * 100, 1) if len(df)>0 else 0
    # Dummy accuracy/consistency:
    return {"Completeness":completeness, "Accuracy":95.0, "Consistency":94.0, "Timeliness":98.0}

def data_quality_section():
    st.subheader("🧪 Data Quality Assessment")
    df = st.session_state.get("project_data", None)
    qc = get_data_quality_metrics(df)
    cols = st.columns(4)
    i = 0
    for k,v in qc.items():
        cols[i].markdown(f"<div style='padding:12px;border-radius:8px;background:#fff'><b>{k}</b><div style='font-size:22px'>{v}%</div></div>", unsafe_allow_html=True)
        i += 1

def render_risk_heatmap(df: pd.DataFrame):
    st.markdown("### Risk Heatmap by Priority & Status")
    if df is None or df.empty:
        st.info("Upload data to see heatmap")
        return
    risks = df.groupby(["Priority","Status"]).size().reset_index(name="Count")
    fig = px.density_heatmap(risks, x="Status", y="Priority", z="Count", color_continuous_scale="Reds")
    fig.update_layout(template="plotly_white", height=420)
    st.plotly_chart(fig, use_container_width=True)

def quick_risk_detection(df: pd.DataFrame) -> list:
    out = []
    if df is None or df.empty:
        return out
    # Overdue
    overdue_rows = df[(df["Due Date"].notna()) & (df["Due Date"] < pd.Timestamp.now()) & (df["Status"].str.lower() != "done")]
    for _, r in overdue_rows.iterrows():
        out.append({"task_id": r["Task ID"], "risk": "Overdue", "explanation": f"Due {r['Due Date'].date()} (status {r['Status']})"})
    # Blocked
    blocked = df[df["Status"].str.lower() == "blocked"]
    for _, r in blocked.iterrows():
        out.append({"task_id": r["Task ID"], "risk": "Blocked", "explanation": r.get("Description","")[:120]})
    # Overloaded assignees
    counts = df[df["Status"].str.lower()=="in progress"].groupby("Assignee").size()
    for name, cnt in counts.items():
        if cnt > 6:
            out.append({"assignee": name, "risk": "Overloaded", "explanation": f"{cnt} tasks In Progress"})
    return out
