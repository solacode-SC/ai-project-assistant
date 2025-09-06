# src/data_loader.py
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional

# synonyms map (lowercase keys)
SYNONYMS = {
    "task id": "Task ID",
    "id": "Task ID",
    "task": "Task",
    "title": "Task",
    "summary": "Task",
    "status": "Status",
    "state": "Status",
    "assignee": "Assignee",
    "owner": "Assignee",
    "assigned_to": "Assignee",
    "priority": "Priority",
    "story points": "Story Points",
    "points": "Story Points",
    "created": "Created Date",
    "created_at": "Created Date",
    "due": "Due Date",
    "due_date": "Due Date",
    "deadline": "Due Date",
    "epic": "Epic",
    "description": "Description"
}

EXPECTED = ["Task ID","Task","Status","Priority","Assignee","Story Points","Created Date","Due Date","Epic","Description"]

def _canon(col: str) -> str:
    return col.strip().lower().replace("-", " ").replace("_", " ")

def normalize_schema(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for c in df.columns:
        k = _canon(c)
        if k in SYNONYMS:
            rename[c] = SYNONYMS[k]
        else:
            # best-effort title case
            rename[c] = " ".join(w.capitalize() for w in c.replace("_"," ").split())
    df = df.rename(columns=rename)

    # ensure expected columns
    for c in EXPECTED:
        if c not in df.columns:
            df[c] = np.nan

    # types & defaults
    df["Task ID"] = df["Task ID"].fillna([f"TASK-{i+1:05d}" for i in range(len(df))])
    df["Task"] = df["Task"].fillna("Untitled Task")
    df["Status"] = df["Status"].fillna("Todo")
    df["Priority"] = df["Priority"].fillna("Medium")
    # Story Points numeric
    df["Story Points"] = pd.to_numeric(df["Story Points"], errors="coerce").fillna(0).astype(int)
    # Dates
    for d in ["Created Date","Due Date"]:
        df[d] = pd.to_datetime(df[d], errors="coerce")
    df["Epic"] = df["Epic"].fillna("General")
    df["Description"] = df["Description"].fillna("")

    # reorder
    cols = EXPECTED + [c for c in df.columns if c not in EXPECTED]
    df = df.loc[:, cols]
    return df

@st.cache_data
def load_and_process_data(uploaded_file) -> pd.DataFrame:
    # accept file-like
    name = getattr(uploaded_file, "name", "uploaded")
    if name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif name.lower().endswith(".json"):
        df = pd.read_json(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    df = normalize_schema(df)
    return df

def generate_sample_data(n_tasks: int = 100) -> pd.DataFrame:
    import numpy as np
    base = datetime.now() - timedelta(days=60)
    np.random.seed(42)
    statuses = ["Todo","In Progress","Done","Blocked","Review"]
    priorities = ["Low","Medium","High","Critical"]
    assignees = ["Alice Johnson","Bob Smith","Charlie Brown","Diana Prince","Eve Wilson","Frank Miller"]
    data = {
        "Task ID":[f"PROJ-{i+1:03d}" for i in range(n_tasks)],
        "Task":[f"Implement feature {chr(65+i%26)}" for i in range(n_tasks)],
        "Status":np.random.choice(statuses, n_tasks, p=[0.15,0.35,0.35,0.08,0.07]),
        "Priority":np.random.choice(priorities, n_tasks, p=[0.3,0.4,0.25,0.05]),
        "Assignee":np.random.choice(assignees, n_tasks),
        "Story Points":np.random.choice([1,2,3,5,8,13], n_tasks, p=[0.15,0.3,0.25,0.2,0.08,0.02]),
        "Created Date":[base + timedelta(days=np.random.randint(0,50)) for _ in range(n_tasks)],
        "Due Date":[base + timedelta(days=60 + np.random.randint(0,30)) for _ in range(n_tasks)],
        "Epic":np.random.choice(["User Management","Payment System","Analytics","Mobile App","API"], n_tasks),
        "Description":["Auto-generated sample task" for _ in range(n_tasks)]
    }
    df = pd.DataFrame(data)
    return normalize_schema(df)
