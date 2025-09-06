# app.py
import streamlit as st
from src.data_loader import load_and_process_data, generate_sample_data
from src.kpi import display_kpi_dashboard, render_gantt_timeline
from src.chatbot import chatbot_interface
from src.analysis import data_quality_section, render_risk_heatmap, quick_risk_detection
from src.reports import reports_section, export_report_html, export_report_pdf_optional
from src.utils import set_page_config, apply_custom_css, style_metric_card, save_df_to_excel

# -------------------------
# Page config & CSS
# -------------------------
set_page_config()
apply_custom_css()

# Sidebar global controls
with st.sidebar:
    st.title("AI Project Assistant")
    st.caption("📊 Upload data, ask the AI, export reports, and visualize KPIs.")
    uploaded_file = st.file_uploader("Upload project CSV/JSON/XLSX", type=["csv", "json", "xlsx"])
    if st.button("Load sample data"):
        st.session_state.project_data = generate_sample_data()
        st.success("Sample data loaded (100 tasks).")

    st.divider()
    st.markdown("### UI")
    dark_mode = st.checkbox("Enable dark style", value=False)
    st.session_state.dark_mode = dark_mode

    st.markdown("### AI Settings")
    model_choice = st.selectbox("Model (for LLM calls)", ["gpt-4", "gpt-4o-mini", "mistral-7b"], index=0)
    st.session_state.model_choice = model_choice

    st.markdown("### Quick Filters")
    st.session_state.filter_overdue = st.checkbox("Show only overdue tasks", value=False)
    st.session_state.filter_blocked = st.checkbox("Show only blocked tasks", value=False)

st.divider()

# Load uploaded file (if any)
if uploaded_file:
    try:
        df = load_and_process_data(uploaded_file)
        st.session_state.project_data = df
        st.success(f"Loaded {len(df)} rows.")
    except Exception as e:
        st.error(f"Error loading file: {e}")

# Grab df from session if available
df = st.session_state.get("project_data", None)

# Tabs
tabs = st.tabs(["📊 Dashboard", "🔎 Explorer", "📅 Timeline", "🔥 Risks", "💬 AI Chat", "📋 Reports"])

# ---------- Dashboard ----------
with tabs[0]:
    st.header("📊 Overview")
    display_kpi_dashboard()  # handles df None internally

# ---------- Explorer (Data table + filters) ----------
with tabs[1]:
    st.header("🔎 Data Explorer")
    if df is None:
        st.info("Upload or load sample data to explore tasks.")
    else:
        # Quick filters
        cols = st.columns([2,2,2,2])
        status_filter = cols[0].multiselect("Status", options=sorted(df["Status"].dropna().unique().tolist()), default=None)
        assignee_filter = cols[1].multiselect("Assignee", options=sorted(df["Assignee"].dropna().unique().tolist()), default=None)
        epic_filter = cols[2].multiselect("Epic", options=sorted(df["Epic"].dropna().unique().tolist()), default=None)
        search_q = cols[3].text_input("Search (title/desc)")

        # Apply filters
        df_view = df.copy()
        if status_filter:
            df_view = df_view[df_view["Status"].isin(status_filter)]
        if assignee_filter:
            df_view = df_view[df_view["Assignee"].isin(assignee_filter)]
        if epic_filter:
            df_view = df_view[df_view["Epic"].isin(epic_filter)]
        if search_q:
            df_view = df_view[df_view["Task"].str.contains(search_q, case=False, na=False) | df_view.get("Description", "").astype(str).str.contains(search_q, case=False, na=False)]

        # Quick toggles (from sidebar)
        if st.session_state.filter_overdue and "Due Date" in df_view.columns:
            df_view = df_view[df_view["Due Date"] < pd.Timestamp.now()]
        if st.session_state.filter_blocked and "Status" in df_view.columns:
            df_view = df_view[df_view["Status"].str.lower() == "blocked"]

        st.markdown(f"Showing **{len(df_view)}** rows")
        st.dataframe(df_view.reset_index(drop=True), use_container_width=True)

        # Export
        colx1, colx2 = st.columns([1,1])
        with colx1:
            if st.button("Export CSV"):
                st.download_button("Download CSV", df_view.to_csv(index=False).encode("utf-8"), "project_export.csv")
        with colx2:
            if st.button("Export Excel"):
                path = save_df_to_excel(df_view, "outputs/reports/project_export.xlsx")
                st.success(f"Saved to {path}")

# ---------- Timeline (Gantt) ----------
with tabs[2]:
    st.header("📅 Timeline / Gantt")
    if df is None:
        st.info("Upload data to see timeline.")
    else:
        render_gantt_timeline(df)

# ---------- Risks ----------
with tabs[3]:
    st.header("🔥 Risk Insights")
    if df is None:
        st.info("Upload data to detect risks.")
    else:
        render_risk_heatmap(df)
        st.markdown("### Quick risk detector")
        risks = quick_risk_detection(df)
        st.json(risks)

# ---------- Chat ----------
with tabs[4]:
    st.header("💬 AI Chat")
    chatbot_interface()

# ---------- Reports ----------
with tabs[5]:
    st.header("📋 Reports & Exports")
    reports_section()  # includes AI executive summary and downloads

# Footer
st.markdown("---")
st.caption("AI Project Assistant • Built by Team SolaCode")
