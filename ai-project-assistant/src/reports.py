import streamlit as st
from src.kpi import calculate_kpis
from datetime import datetime
from src.llm_client import LLMManager as AIChatbot



# ---------- Report Section ---------- #
def reports_section():
    st.subheader("📋 Executive Reports")

    if "project_data" not in st.session_state:
        st.info("📊 Upload project data to generate reports!")
        return

    df = st.session_state.project_data
    kpis = calculate_kpis(df)
    project_name = "AI Project Assistant"

    st.markdown(f"""
    <div style="background:white; padding:1.5rem; border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
        <h2>📊 Executive Summary - {project_name}</h2>
        <p>The project is <strong>{kpis['completion_rate']:.1f}% complete</strong> 
        with {kpis['completed']} of {kpis['total']} tasks done.</p>
        <p>🚨 Blocked: {kpis['blocked']} • 📅 Overdue: {kpis['overdue']} • ⚡ Velocity: {kpis['velocity']}</p>
        <p><em>Generated on {datetime.now().strftime("%B %d, %Y %H:%M")}</em></p>
    </div>
    """, unsafe_allow_html=True)

    # Generate AI Executive Summary
    if "report_llm" not in st.session_state:
        st.session_state.report_llm = AIChatbot()

    if st.button("🧠 Generate AI Executive Summary"):
        with st.spinner("Generating executive summary..."):
            prompt = (
                "You are an AI assistant that writes concise, insightful executive summaries "
                "of project management KPIs. Based on these KPIs, provide a summary:\n\n"
                f"Completion Rate: {kpis['completion_rate']:.1f}%\n"
                f"Completed Tasks: {kpis['completed']}\n"
                f"Total Tasks: {kpis['total']}\n"
                f"Blocked Tasks: {kpis['blocked']}\n"
                f"Overdue Tasks: {kpis['overdue']}\n"
                f"Velocity: {kpis['velocity']}\n\n"
                "Write a professional executive summary highlighting progress, risks, and recommendations."
            )
            try:
                summary = st.session_state.report_llm.ask(prompt)
                st.markdown(f"### AI Executive Summary\n\n{summary}")
                # Save HTML version
                st.session_state.report_html = export_report_html(project_name, kpis, summary)
            except Exception as e:
                st.error(f"Error generating summary: {e}")

    # Download options
    if "report_html" in st.session_state:
        st.download_button(
            "📄 Download Report (HTML)",
            st.session_state.report_html,
            "executive_report.html",
            "text/html"
        )
        pdf_bytes = export_report_pdf_optional(st.session_state.report_html)
        if pdf_bytes:
            st.download_button(
                "📑 Download Report (PDF)",
                pdf_bytes,
                "executive_report.pdf",
                "application/pdf"
            )

# ---------- Export Helpers ---------- #
def export_report_html(project_name, kpis, summary):
    html = f"""
    <html>
    <head>
        <title>{project_name} - Executive Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1, h2, h3 {{ color: #333; }}
            .card {{ border: 1px solid #ddd; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>📊 Executive Report - {project_name}</h1>
        <div class="card">
            <h2>KPIs</h2>
            <p>✅ Completed: {kpis['completed']} / {kpis['total']}</p>
            <p>⚠️ Blocked: {kpis['blocked']}</p>
            <p>📅 Overdue: {kpis['overdue']}</p>
            <p>⚡ Velocity: {kpis['velocity']}</p>
            <p>Completion Rate: {kpis['completion_rate']:.1f}%</p>
        </div>
        <div class="card">
            <h2>AI Executive Summary</h2>
            <p>{summary}</p>
        </div>
        <p><em>Generated on {datetime.now().strftime("%B %d, %Y %H:%M")}</em></p>
    </body>
    </html>
    """
    return html

def export_report_pdf_optional(html_content):
    try:
        import pdfkit
        return pdfkit.from_string(html_content, False)
    except Exception:
        return None
