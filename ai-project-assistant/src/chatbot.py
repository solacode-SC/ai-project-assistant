# src/chatbot.py
import streamlit as st
from src.llm_client import LLMManager
from src.kpi import calculate_kpis

# caching the manager per session
def _ensure_manager():
    if "llm_manager" not in st.session_state:
        model_choice = st.session_state.get("model_choice", "gpt-4")
        try:
            st.session_state.llm_manager = LLMManager(model_choice)
        except Exception as e:
            st.session_state.llm_error = str(e)
            st.session_state.llm_manager = None
    return st.session_state.llm_manager

def chatbot_interface():
    st.subheader("💬 AI Chat")
    df = st.session_state.get("project_data", None)
    manager = _ensure_manager()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # show messages
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # input
    user_input = st.chat_input("Ask about status, risks, or recommendations...")
    if user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input})
        # build context
        context = ""
        if df is not None:
            kpis = calculate_kpis(df)
            context = (
                f"Project KPIs:\nCompletion: {kpis['completion_rate']:.1f}%\n"
                f"Completed: {kpis['completed']}\nBlocked: {kpis['blocked']}\nOverdue: {kpis['overdue']}\n"
                f"Velocity: {kpis['velocity']}\n"
            )
        prompt = f"{context}\nUser question: {user_input}\nAnswer concisely with recommendations and next actions."

        if manager:
            try:
                with st.spinner("🧠 Thinking..."):
                    ans = manager.ask(prompt)
            except Exception as e:
                ans = f"⚠️ LLM error: {e}"
        else:
            # fallback simulated
            ans = _simulated_response(user_input, df)

        st.session_state.chat_history.append({"role":"assistant","content":ans})
        st.experimental_rerun()

def _simulated_response(user_input: str, df):
    # Very simple rule-based fallback (safe)
    text = user_input.lower()
    if "status" in text:
        k = calculate_kpis(df) if df is not None else {}
        return f"Project is {k.get('completion_rate',0):.1f}% complete. {k.get('blocked',0)} blocked, {k.get('overdue',0)} overdue."
    if "risk" in text or "issue" in text:
        risks = []
        if df is not None:
            risks = [r for r in []]  # placeholder
        return "I detect some blockers and overdue items — open the Risks tab for details."
    return "I can summarize KPIs, detect risks, and generate recommendations. Try: 'Give me an executive summary'."
