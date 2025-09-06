# AI Project Assistant 🤖

Analyze project data (tickets, backlog), summarize key points, detect risks, and visualize KPIs — with an interactive chatbot UI.

## Features
- Upload CSV/JSON/XLSX or use sample data
- KPIs (completion, blocked, overdue, velocity)
- Burndown & risk heatmap charts
- AI-style chat responses (simulated, pluggable to LLMs)
- Executive summary generation & export

## Tech
- Streamlit, Plotly
- Python (Pandas, NumPy)
- (Optional) LangChain/OpenAI for real LLMs
- Power BI/Exports via CSV/Excel/HTML

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
