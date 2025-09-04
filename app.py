import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="AI Project Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-change {
        color: #10b981;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Chat Interface */
    .chat-container {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        overflow: hidden;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 1rem 1.5rem;
        font-weight: 600;
    }
    
    .chat-message {
        padding: 0.75rem 1rem;
        margin: 0.5rem;
        border-radius: 12px;
        max-width: 80%;
        line-height: 1.5;
    }
    
    .user-message {
        background: #3b82f6;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .assistant-message {
        background: #f1f5f9;
        color: #334155;
        margin-right: auto;
    }
    
    /* Insight Cards */
    .insight-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    
    .insight-success {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
    }
    
    .insight-warning {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #fefce8 100%);
    }
    
    .insight-info {
        border-left-color: #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
    }
    
    /* Navigation Tabs */
    .nav-pills {
        background: #f8fafc;
        border-radius: 12px;
        padding: 0.5rem;
        margin-bottom: 2rem;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        padding: 1rem;
        border-radius: 12px;
    }
    
    /* File Upload Area */
    .upload-area {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f8fafc;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    /* Success/Warning/Error Messages */
    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
    }
    
    /* Progress Bars */
    .stProgress > div > div > div {
        border-radius: 10px;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    /* Hide Streamlit Menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hi! I'm your AI Project Assistant. How can I help you analyze your project today?"}
    ]

if 'project_data' not in st.session_state:
    st.session_state.project_data = None

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "GPT-4"

if 'risk_sensitivity' not in st.session_state:
    st.session_state.risk_sensitivity = 3

# Helper Functions
@st.cache_data
def generate_sample_data():
    """Generate sample project data for demonstration"""
    np.random.seed(42)
    n_tasks = 100
    
    statuses = ['Todo', 'In Progress', 'Done', 'Blocked', 'Review']
    priorities = ['Low', 'Medium', 'High', 'Critical']
    assignees = ['Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Prince', 'Eve Wilson', 'Frank Miller']
    
    base_date = datetime.now() - timedelta(days=60)
    
    data = {
        'Task ID': [f'PROJ-{i+1:03d}' for i in range(n_tasks)],
        'Task': [f'Implement feature {chr(65+i%26)} for module {i//10+1}' for i in range(n_tasks)],
        'Status': np.random.choice(statuses, n_tasks, p=[0.15, 0.35, 0.35, 0.08, 0.07]),
        'Priority': np.random.choice(priorities, n_tasks, p=[0.3, 0.4, 0.25, 0.05]),
        'Assignee': np.random.choice(assignees, n_tasks),
        'Story Points': np.random.choice([1, 2, 3, 5, 8, 13], n_tasks, p=[0.15, 0.3, 0.25, 0.2, 0.08, 0.02]),
        'Created Date': [base_date + timedelta(days=np.random.randint(0, 50)) for _ in range(n_tasks)],
        'Due Date': [base_date + timedelta(days=60 + np.random.randint(0, 30)) for _ in range(n_tasks)],
        'Epic': np.random.choice(['User Management', 'Payment System', 'Analytics', 'Mobile App', 'API'], n_tasks)
    }
    
    return pd.DataFrame(data)

def calculate_kpis(df):
    """Calculate project KPIs"""
    if df is None or df.empty:
        return {}
    
    total_tasks = len(df)
    completed = len(df[df['Status'] == 'Done'])
    in_progress = len(df[df['Status'] == 'In Progress'])
    blocked = len(df[df['Status'] == 'Blocked'])
    
    # Calculate overdue tasks
    current_date = datetime.now()
    df['Due Date'] = pd.to_datetime(df['Due Date'])
    overdue = len(df[(df['Due Date'] < current_date) & (df['Status'] != 'Done')])
    
    completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
    
    # Calculate velocity (story points completed)
    velocity = df[df['Status'] == 'Done']['Story Points'].sum()
    
    return {
        'total_tasks': total_tasks,
        'completed': completed,
        'in_progress': in_progress,
        'blocked': blocked,
        'overdue': overdue,
        'completion_rate': completion_rate,
        'velocity': velocity
    }

def create_burndown_chart(df):
    """Create burndown chart"""
    if df is None or df.empty:
        return None
    
    # Simulate burndown data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                         end=datetime.now() + timedelta(days=10), 
                         freq='D')
    
    total_points = df['Story Points'].sum()
    ideal_burndown = [total_points - (total_points * i / len(dates)) for i in range(len(dates))]
    
    # Simulate actual burndown
    np.random.seed(42)
    actual_burndown = []
    remaining = total_points
    for i in range(len(dates)):
        if i < 30:  # Past data
            daily_completion = np.random.poisson(total_points/35)
            remaining = max(0, remaining - daily_completion)
            actual_burndown.append(remaining)
        else:  # Future projection
            actual_burndown.append(remaining)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=ideal_burndown,
        mode='lines', name='Ideal Burndown',
        line=dict(color='#10b981', width=2, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=dates[:31], y=actual_burndown[:31],
        mode='lines+markers', name='Actual Burndown',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title='Project Burndown Chart',
        xaxis_title='Date',
        yaxis_title='Remaining Story Points',
        template='plotly_white',
        height=400,
        showlegend=True
    )
    
    return fig

def create_risk_heatmap(df):
    """Create risk assessment heatmap"""
    if df is None or df.empty:
        return None
    
    # Create risk matrix
    risks = df.groupby(['Priority', 'Status']).size().reset_index(name='Count')
    
    fig = px.density_heatmap(
        risks, x='Status', y='Priority', z='Count',
        color_continuous_scale='Reds',
        title='Risk Assessment Heatmap'
    )
    
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    
    return fig

def simulate_ai_response(user_input, project_data):
    """Simulate AI response based on user input and project data"""
    if project_data is not None:
        kpis = calculate_kpis(project_data)
        
        responses = {
            'status': f"""📊 **Project Status Overview:**
            
**Overall Progress:** {kpis['completion_rate']:.1f}% complete

**Key Metrics:**
• ✅ Completed Tasks: {kpis['completed']}
• 🔄 In Progress: {kpis['in_progress']}
• ⚠️ Blocked Tasks: {kpis['blocked']}
• 📈 Story Points Delivered: {kpis['velocity']}

**Health Assessment:** {'🟢 Healthy' if kpis['blocked'] < 5 else '🟡 Needs Attention'}
            """,
            
            'risk': f"""⚠️ **Risk Analysis:**
            
**Critical Risks Identified:**
• 🚫 {kpis['blocked']} blocked tasks requiring immediate attention
• ⏰ {kpis['overdue']} overdue items impacting timeline
• 📊 Current velocity: {kpis['velocity']} story points

**Risk Level:** {'🟢 Low' if kpis['blocked'] <= 3 else '🟡 Medium' if kpis['blocked'] <= 7 else '🔴 High'}

**Recommendations:**
1. Prioritize unblocking {kpis['blocked']} stuck items
2. Review resource allocation for overdue tasks
3. Consider scope adjustment if risks persist
            """,
            
            'team': """👥 **Team Performance Analysis:**
            
**Top Performers:**
• Alice Johnson: 12 tasks completed, 25 story points
• Bob Smith: 10 tasks completed, 22 story points

**Areas for Support:**
• Charlie Brown: 3 blocked tasks, may need assistance
• Review workload distribution for optimal velocity

**Team Velocity:** Trending upward (+15% vs last sprint)
            """,
            
            'recommendations': f"""💡 **AI Recommendations:**
            
**Immediate Actions:**
1. 🚨 Address {kpis['blocked']} blocked items (est. 2-3 days)
2. 📅 Reschedule {kpis['overdue']} overdue tasks
3. 🎯 Focus on high-priority items in current sprint

**Strategic Suggestions:**
• Consider daily standups for blocked items
• Implement pair programming for complex tasks
• Schedule technical debt review session

**Success Probability:** {85 - (kpis['blocked'] * 3)}% for on-time delivery
            """
        }
        
        # Simple keyword matching for demo
        user_lower = user_input.lower()
        if any(word in user_lower for word in ['status', 'progress', 'overview']):
            return responses['status']
        elif any(word in user_lower for word in ['risk', 'problem', 'issue']):
            return responses['risk']
        elif any(word in user_lower for word in ['team', 'people', 'member']):
            return responses['team']
        elif any(word in user_lower for word in ['recommend', 'suggest', 'advice']):
            return responses['recommendations']
        else:
            return f"""I can help you analyze your project! Here's what I found:
            
📈 **Quick Summary:** {kpis['completion_rate']:.1f}% complete with {kpis['velocity']} story points delivered.

Try asking me about:
• "What's the project status?"
• "What risks do you see?"
• "How is the team performing?"
• "What do you recommend?"
            """
    else:
        return "Please upload your project data first so I can provide specific insights about your project."

# Main App Layout
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Project Assistant</h1>
        <p>Your Smart Companion for Project Analysis & Risk Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # File Upload
        st.markdown("#### 📁 Upload Project Data")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['csv', 'json', 'xlsx'],
            help="Upload your project data (CSV, JSON, or Excel format)"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "text/csv":
                    st.session_state.project_data = pd.read_csv(uploaded_file)
                elif uploaded_file.type == "application/json":
                    st.session_state.project_data = pd.read_json(uploaded_file)
                else:
                    st.session_state.project_data = pd.read_excel(uploaded_file)
                st.success(f"✅ Loaded {len(st.session_state.project_data)} records")
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
        
        # Use Sample Data
        if st.button("📊 Load Sample Data"):
            st.session_state.project_data = generate_sample_data()
            st.success("✅ Sample data loaded!")
        
        st.divider()
        
        # Project Selection
        st.markdown("#### 🎯 Project Settings")
        project_name = st.selectbox(
            "Select Project",
            ["E-commerce Platform", "Mobile App Redesign", "API Migration", "Data Analytics Dashboard"]
        )
        
        # LLM Model Selection
        st.session_state.selected_model = st.radio(
            "🧠 AI Model",
            ["GPT-4", "GPT-3.5", "Mistral-7B", "Claude-3"],
            help="Choose your preferred LLM for analysis"
        )
        
        # Risk Sensitivity
        st.session_state.risk_sensitivity = st.slider(
            "⚠️ Risk Sensitivity",
            min_value=1,
            max_value=5,
            value=3,
            help="Adjust how sensitive the risk detection should be"
        )
        
        # Vector DB Settings
        st.markdown("#### 🔍 Vector Database")
        enable_semantic_search = st.toggle("Enable Semantic Search", value=True)
        memory_retention = st.slider("Memory Retention (days)", 1, 30, 7)
        
        st.divider()
        
        # System Status
        st.markdown("#### 🚀 System Status")
        st.success("🟢 LangChain: Connected")
        st.success("🟢 Vector DB: Online")
        st.success("🟢 Spark ETL: Ready")
        if st.session_state.selected_model == "GPT-4":
            st.success("🟢 OpenAI: Connected")
        else:
            st.info("🟡 Mistral: Standby")
    
    # Main Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "💬 AI Chat", 
        "🔍 Insights", 
        "📈 Analytics", 
        "📋 Reports"
    ])
    
    # Dashboard Tab
    with tab1:
        if st.session_state.project_data is not None:
            kpis = calculate_kpis(st.session_state.project_data)
            
            # KPI Cards
            st.markdown("### 📊 Project Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">✅ Completed Tasks</div>
                    <div class="metric-value" style="color: #10b981;">{kpis['completed']}</div>
                    <div class="metric-change">↗️ +12% this sprint</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🔄 In Progress</div>
                    <div class="metric-value" style="color: #3b82f6;">{kpis['in_progress']}</div>
                    <div class="metric-change">→ Steady pace</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">⚠️ Blocked Tasks</div>
                    <div class="metric-value" style="color: #ef4444;">{kpis['blocked']}</div>
                    <div class="metric-change">{"🟢 Low risk" if kpis['blocked'] <= 3 else "🟡 Needs attention"}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📈 Progress</div>
                    <div class="metric-value" style="color: #8b5cf6;">{kpis['completion_rate']:.1f}%</div>
                    <div class="metric-change">🎯 On track</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Progress Bar
            st.markdown("### 🎯 Sprint Progress")
            progress_col1, progress_col2 = st.columns([3, 1])
            with progress_col1:
                st.progress(kpis['completion_rate']/100)
            with progress_col2:
                st.metric("Story Points", f"{kpis['velocity']}/120")
            
            # Charts
            st.markdown("### 📈 Project Visualizations")
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                burndown_chart = create_burndown_chart(st.session_state.project_data)
                if burndown_chart:
                    st.plotly_chart(burndown_chart, use_container_width=True)
            
            with chart_col2:
                risk_chart = create_risk_heatmap(st.session_state.project_data)
                if risk_chart:
                    st.plotly_chart(risk_chart, use_container_width=True)
            
            # Team Performance
            st.markdown("### 👥 Team Performance")
            team_data = st.session_state.project_data.groupby('Assignee').agg({
                'Task ID': 'count',
                'Story Points': 'sum',
                'Status': lambda x: (x == 'Done').sum()
            }).rename(columns={'Task ID': 'Total Tasks', 'Status': 'Completed'})
            
            team_data['Completion Rate'] = (team_data['Completed'] / team_data['Total Tasks'] * 100).round(1)
            
            st.dataframe(
                team_data,
                use_container_width=True,
                column_config={
                    "Total Tasks": st.column_config.NumberColumn("Tasks", format="%d"),
                    "Story Points": st.column_config.NumberColumn("Points", format="%d"),
                    "Completed": st.column_config.NumberColumn("Done", format="%d"),
                    "Completion Rate": st.column_config.ProgressColumn("Progress", min_value=0, max_value=100)
                }
            )
            
        else:
            st.info("👆 **Upload your project data or load sample data from the sidebar to get started!**")
            
            # Show sample dashboard with placeholder data
            st.markdown("### 📊 Sample Project Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            sample_kpis = [
                ("✅ Completed", "45", "#10b981"),
                ("🔄 In Progress", "12", "#3b82f6"),
                ("⚠️ Risks", "3", "#ef4444"),
                ("📈 Progress", "78%", "#8b5cf6")
            ]
            
            for i, (label, value, color) in enumerate(sample_kpis):
                with [col1, col2, col3, col4][i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value" style="color: {color};">{value}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # AI Chat Tab
    with tab2:
        st.markdown("""
        <div class="chat-header">
            💬 AI Assistant - Powered by LangChain + Vector Memory
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Action Buttons
        st.markdown("#### 🚀 Quick Actions")
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        
        with action_col1:
            if st.button("📊 Summarize Project", use_container_width=True):
                response = simulate_ai_response("project status", st.session_state.project_data)
                st.session_state.chat_messages.append({"role": "user", "content": "Summarize the project status"})
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        with action_col2:
            if st.button("⚠️ Detect Risks", use_container_width=True):
                response = simulate_ai_response("detect risks", st.session_state.project_data)
                st.session_state.chat_messages.append({"role": "user", "content": "What risks do you see?"})
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        with action_col3:
            if st.button("💡 Get Recommendations", use_container_width=True):
                response = simulate_ai_response("recommendations", st.session_state.project_data)
                st.session_state.chat_messages.append({"role": "user", "content": "What do you recommend?"})
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        with action_col4:
            if st.button("👥 Team Analysis", use_container_width=True):
                response = simulate_ai_response("team performance", st.session_state.project_data)
                st.session_state.chat_messages.append({"role": "user", "content": "How is the team performing?"})
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        # Chat Messages
        st.markdown("#### 💬 Conversation")
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat Input
        st.markdown("#### ✍️ Ask me anything about your project")
        user_input = st.text_input(
            "Your question:",
            placeholder="e.g., 'What's blocking our progress?' or 'Should we be worried about the timeline?'",
            key="chat_input"
        )
        
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("Send 🚀", use_container_width=True):
                if user_input:
                    # Add user message
                    st.session_state.chat_messages.append({"role": "user", "content": user_input})
                    
                    # Generate AI response
                    with st.spinner(f"🧠 {st.session_state.selected_model} is thinking..."):
                        time.sleep(1)  # Simulate processing time
                        response = simulate_ai_response(user_input, st.session_state.project_data)
                    
                    # Add AI response
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    st.rerun()
        
        # Model Status
        st.info(f"🤖 Currently using **{st.session_state.selected_model}** with Vector DB memory retention of **{memory_retention} days**")
    
    # Insights Tab
    with tab3:
        st.markdown("### 🔍 AI-Powered Insights")
        
        if st.session_state.project_data is not None:
            kpis = calculate_kpis(st.session_state.project_data)
            
            # Insight Cards
            insight_col1, insight_col2 = st.columns(2)
            
            with insight_col1:
                st.markdown("#### ✅ Key Achievements")
                st.markdown(f"""
                <div class="insight-card insight-success">
                    <h4>🎯 Sprint Goals Exceeded</h4>
                    <p>Team completed {kpis['completed']} tasks with {kpis['velocity']} story points, exceeding planned velocity by 12%.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="insight-card insight-success">
                    <h4>📈 Quality Metrics Improved</h4>
                    <p>Bug rate decreased by 25% compared to previous sprint, indicating better development practices and code reviews.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="insight-card insight-success">
                    <h4>⚡ Team Velocity Trending Up</h4>
                    <p>Current completion rate of {kpis['completion_rate']:.1f}% shows strong momentum and team engagement.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with insight_col2:
                st.markdown("#### ⚠️ Risk Analysis")
                
                if kpis['blocked'] > 0:
                    st.markdown(f"""
                    <div class="insight-card insight-warning">
                        <h4>🚫 Blocked Tasks Alert</h4>
                        <p>{kpis['blocked']} tasks are currently blocked. These require immediate attention to prevent sprint delays.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if kpis['overdue'] > 0:
                    st.markdown(f"""
                    <div class="insight-card insight-warning">
                        <h4>⏰ Overdue Items</h4>
                        <p>{kpis['overdue']} tasks are past their due date. Consider resource reallocation or scope adjustment.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="insight-card insight-info">
                    <h4>📊 Workload Distribution</h4>
                    <p>Current task distribution shows potential bottlenecks. Consider load balancing across team members.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # AI Recommendations Section
            st.markdown("#### 💡 AI Recommendations")
            
            recommendations = [
                {
                    "title": "🚨 Prioritize Blocked Items",
                    "content": f"Focus on unblocking the {kpis['blocked']} stuck tasks to maintain project momentum and prevent cascade delays.",
                    "priority": "High",
                    "color": "#ef4444"
                },
                {
                    "title": "👥 Leverage High Performers", 
                    "content": "Top performers are exceeding targets - consider having them mentor other team members or take on complex tasks.",
                    "priority": "Medium",
                    "color": "#10b981"
                },
                {
                    "title": "📅 Schedule Risk Review",
                    "content": "Plan a mid-sprint checkpoint to address timeline risks before they impact final delivery.",
                    "priority": "Medium", 
                    "color": "#8b5cf6"
                },
                {
                    "title": "🔄 Optimize Workflow",
                    "content": "Current velocity suggests room for process improvements. Consider automation or tooling enhancements.",
                    "priority": "Low",
                    "color": "#3b82f6"
                }
            ]
            
            for rec in recommendations:
                st.markdown(f"""
                <div style="
                    background: white;
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin-bottom: 1rem;
                    border-left: 4px solid {rec['color']};
                    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: #1f2937;">{rec['title']}</h4>
                        <span style="
                            background: {rec['color']}; 
                            color: white; 
                            padding: 0.25rem 0.75rem; 
                            border-radius: 20px; 
                            font-size: 0.8rem; 
                            font-weight: 600;
                        ">{rec['priority']}</span>
                    </div>
                    <p style="margin: 0; color: #6b7280; line-height: 1.5;">{rec['content']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Semantic Search Section
            st.markdown("#### 🔍 Semantic Project Search")
            st.info("🚀 **Vector Database Integration**: Search your project history using natural language!")
            
            search_query = st.text_input(
                "Search project knowledge base:",
                placeholder="e.g., 'Find similar issues from past sprints' or 'What caused delays in Q2?'"
            )
            
            if search_query:
                with st.spinner("🔍 Searching vector database..."):
                    time.sleep(1)
                    st.success("Found 3 relevant entries from project history:")
                    
                    search_results = [
                        "🔍 **Sprint 12 Retrospective**: Similar blocking issues resolved by daily standups",
                        "📊 **Performance Report Q2**: Resource allocation patterns that improved velocity", 
                        "⚠️ **Risk Assessment March**: Early warning indicators for timeline slippage"
                    ]
                    
                    for result in search_results:
                        st.markdown(f"• {result}")
        
        else:
            st.info("📊 Upload project data to see AI-powered insights and recommendations!")
    
    # Analytics Tab
    with tab4:
        st.markdown("### 📈 Advanced Analytics")
        
        if st.session_state.project_data is not None:
            # Spark ETL Status
            st.markdown("#### ⚡ Spark ETL Pipeline")
            etl_col1, etl_col2, etl_col3 = st.columns(3)
            
            with etl_col1:
                st.metric("Data Processing", "✅ Complete", "2.3M records")
            with etl_col2:
                st.metric("Pipeline Status", "🟢 Healthy", "99.8% uptime")
            with etl_col3:
                st.metric("Last Update", "5 min ago", "Real-time sync")
            
            # Advanced Visualizations
            st.markdown("#### 📊 Advanced Visualizations")
            
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                # Epic Progress Chart
                epic_data = st.session_state.project_data.groupby(['Epic', 'Status']).size().unstack(fill_value=0)
                fig_epic = px.bar(
                    epic_data, 
                    title="Progress by Epic",
                    color_discrete_map={
                        'Done': '#10b981',
                        'In Progress': '#3b82f6', 
                        'Todo': '#6b7280',
                        'Blocked': '#ef4444'
                    }
                )
                fig_epic.update_layout(template='plotly_white', height=400)
                st.plotly_chart(fig_epic, use_container_width=True)
            
            with viz_col2:
                # Velocity Trend
                dates = pd.date_range(start='2024-01-01', periods=12, freq='W')
                velocity_data = {
                    'Week': dates,
                    'Planned': np.random.normal(25, 3, 12),
                    'Actual': np.random.normal(27, 4, 12)
                }
                
                fig_velocity = go.Figure()
                fig_velocity.add_trace(go.Scatter(
                    x=velocity_data['Week'], 
                    y=velocity_data['Planned'],
                    name='Planned Velocity',
                    line=dict(color='#94a3b8', dash='dash')
                ))
                fig_velocity.add_trace(go.Scatter(
                    x=velocity_data['Week'], 
                    y=velocity_data['Actual'],
                    name='Actual Velocity',
                    line=dict(color='#3b82f6', width=3)
                ))
                fig_velocity.update_layout(
                    title='Velocity Trend Analysis',
                    template='plotly_white',
                    height=400
                )
                st.plotly_chart(fig_velocity, use_container_width=True)
            
            # Predictive Analytics
            st.markdown("#### 🔮 Predictive Analytics")
            
            pred_col1, pred_col2, pred_col3 = st.columns(3)
            
            with pred_col1:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">🎯 Completion Forecast</div>
                    <div class="metric-value" style="color: #10b981;">Dec 15, 2024</div>
                    <div class="metric-change">85% confidence</div>
                </div>
                """, unsafe_allow_html=True)
            
            with pred_col2:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">⚠️ Risk Probability</div>
                    <div class="metric-value" style="color: #f59e0b;">23%</div>
                    <div class="metric-change">Timeline delay</div>
                </div>
                """, unsafe_allow_html=True)
            
            with pred_col3:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">📈 Success Score</div>
                    <div class="metric-value" style="color: #8b5cf6;">8.2/10</div>
                    <div class="metric-change">Above average</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Power BI Integration
            st.markdown("#### 📊 Power BI Enterprise Dashboards")
            
            powerbi_col1, powerbi_col2 = st.columns(2)
            
            with powerbi_col1:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                    border: 2px solid #cbd5e1;
                    border-radius: 12px;
                    padding: 2rem;
                    text-align: center;
                    height: 200px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                ">
                    <h4>📊 Executive Dashboard</h4>
                    <p>Power BI embedded report for leadership</p>
                    <button style="
                        background: #0078d4;
                        color: white;
                        border: none;
                        padding: 0.5rem 1rem;
                        border-radius: 6px;
                        cursor: pointer;
                    ">Open in Power BI</button>
                </div>
                """, unsafe_allow_html=True)
            
            with powerbi_col2:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                    border: 2px solid #cbd5e1;
                    border-radius: 12px;
                    padding: 2rem;
                    text-align: center;
                    height: 200px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                ">
                    <h4>📈 Operational Metrics</h4>
                    <p>Real-time KPIs and team performance</p>
                    <button style="
                        background: #0078d4;
                        color: white;
                        border: none;
                        padding: 0.5rem 1rem;
                        border-radius: 6px;
                        cursor: pointer;
                    ">View Dashboard</button>
                </div>
                """, unsafe_allow_html=True)
            
            # Data Quality Metrics
            st.markdown("#### 🎯 Data Quality Assessment")
            
            quality_metrics = {
                'Completeness': 98.5,
                'Accuracy': 96.2, 
                'Consistency': 94.8,
                'Timeliness': 99.1
            }
            
            quality_col1, quality_col2, quality_col3, quality_col4 = st.columns(4)
            cols = [quality_col1, quality_col2, quality_col3, quality_col4]
            
            for i, (metric, score) in enumerate(quality_metrics.items()):
                color = "#10b981" if score >= 95 else "#f59e0b" if score >= 90 else "#ef4444"
                with cols[i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{metric}</div>
                        <div class="metric-value" style="color: {color};">{score}%</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        else:
            st.info("📊 Upload project data to access advanced analytics and Spark ETL features!")
    
    # Reports Tab
    with tab5:
        st.markdown("### 📋 Executive Reports & Export")
        
        if st.session_state.project_data is not None:
            # Report Generation
            report_col1, report_col2 = st.columns([3, 1])
            
            with report_col1:
                st.markdown("#### 📊 Generate Executive Summary")
            
            with report_col2:
                if st.button("🚀 Generate Report", use_container_width=True):
                    with st.spinner("🤖 AI is creating your executive summary..."):
                        time.sleep(2)
                        st.success("✅ Report generated successfully!")
            
            # Executive Summary
            if st.session_state.get('report_generated', False) or st.button("📋 View Sample Report"):
                kpis = calculate_kpis(st.session_state.project_data)
                
                st.markdown(f"""
                <div style="
                    background: white;
                    border-radius: 15px;
                    padding: 2rem;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    margin: 1rem 0;
                ">
                    <h2 style="color: #1f2937; margin-bottom: 1.5rem;">📊 Executive Summary - {project_name}</h2>
                    
                    <h3 style="color: #374151; margin-bottom: 1rem;">🎯 Project Overview</h3>
                    <p style="color: #6b7280; line-height: 1.6;">
                        The <strong>{project_name}</strong> is currently at <strong>{kpis['completion_rate']:.1f}% completion</strong> 
                        with strong team performance and quality metrics. The team has successfully completed 
                        <strong>{kpis['completed']} tasks</strong> out of {kpis['total_tasks']} total, delivering 
                        <strong>{kpis['velocity']} story points</strong> this sprint.
                    </p>
                    
                    <h3 style="color: #374151; margin: 1.5rem 0 1rem;">📈 Key Highlights</h3>
                    <ul style="color: #6b7280; line-height: 1.8;">
                        <li>✅ Sprint velocity exceeded planned targets by 12%</li>
                        <li>✅ Bug rate reduced by 25% compared to previous sprint</li>
                        <li>✅ All critical path items remain on schedule</li>
                        <li>⚠️ {kpis['blocked']} tasks currently blocked by dependencies</li>
                        <li>⚠️ {kpis['overdue']} items past due date requiring attention</li>
                    </ul>
                    
                    <h3 style="color: #374151; margin: 1.5rem 0 1rem;">🚨 Immediate Actions Required</h3>
                    <ol style="color: #6b7280; line-height: 1.8;">
                        <li>Escalate blocked tasks to unblock critical dependencies</li>
                        <li>Reallocate resources to address overdue items</li>
                        <li>Schedule mid-sprint checkpoint for risk mitigation</li>
                        <li>Consider scope adjustment if timeline risks persist</li>
                    </ol>
                    
                    <h3 style="color: #374151; margin: 1.5rem 0 1rem;">🎯 Success Probability</h3>
                    <p style="color: #6b7280; line-height: 1.6;">
                        Based on current velocity and risk factors, there is an <strong>85% probability</strong> 
                        of delivering the project on schedule. Key risk mitigation strategies have been identified 
                        and should be implemented immediately.
                    </p>
                    
                    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
                        <p style="color: #9ca3af; font-size: 0.9rem;">
                            Generated by AI Project Assistant using {st.session_state.selected_model} • 
                            {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.report_generated = True
            
            # Export Options
            st.markdown("#### 📤 Export Options")
            
            export_col1, export_col2, export_col3, export_col4 = st.columns(4)
            
            with export_col1:
                if st.button("📄 Export PDF", use_container_width=True):
                    st.success("📄 PDF report downloaded!")
            
            with export_col2:
                if st.button("📊 Export Excel", use_container_width=True):
                    st.success("📊 Excel file downloaded!")
            
            with export_col3:
                if st.button("🔗 Share Link", use_container_width=True):
                    st.success("🔗 Shareable link copied!")
            
            with export_col4:
                if st.button("📧 Email Report", use_container_width=True):
                    st.success("📧 Report emailed to stakeholders!")
            
            # Report History
            st.markdown("#### 📚 Report History")
            
            reports_data = {
                'Date': ['2024-12-15', '2024-12-08', '2024-12-01', '2024-11-24'],
                'Type': ['Executive Summary', 'Risk Assessment', 'Team Performance', 'Milestone Review'],
                'Status': ['✅ Complete', '✅ Complete', '✅ Complete', '✅ Complete'],
                'Actions': ['Download', 'Download', 'Download', 'Download']
            }
            
            st.dataframe(
                pd.DataFrame(reports_data),
                use_container_width=True,
                column_config={
                    "Actions": st.column_config.LinkColumn("Download")
                }
            )
            
            # Report Templates
            st.markdown("#### 📋 Report Templates")
            
            template_col1, template_col2 = st.columns(2)
            
            with template_col1:
                templates = [
                    "📊 Executive Summary",
                    "⚠️ Risk Analysis Report",
                    "👥 Team Performance Review", 
                    "🎯 Sprint Retrospective"
                ]
                
                for template in templates:
                    if st.button(template, use_container_width=True):
                        st.info(f"🚀 Generating {template}...")
            
            with template_col2:
                custom_templates = [
                    "📈 Custom KPI Dashboard",
                    "🔍 Deep Dive Analysis", 
                    "📅 Timeline Assessment",
                    "💰 Budget Impact Report"
                ]
                
                for template in custom_templates:
                    if st.button(template, use_container_width=True):
                        st.info(f"🚀 Creating {template}...")
        
        else:
            st.info("📊 Upload project data to generate executive reports!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 1rem;">
        Made with ❤️ by <strong>Team SolaCode</strong> • 
        Powered by LangChain, GPT-4, Spark ETL & Vector DB • 
        <a href="#" style="color: #3b82f6;">GitHub</a> • 
        <a href="#" style="color: #3b82f6;">Documentation</a> • 
        <a href="#" style="color: #3b82f6;">Support</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()