import os

# Define project structure
structure = {
    "ai-project-assistant": [
        "README.md",
        "requirements.txt",
        ".env",
        "app.py",
        {"data": ["sample_tasks.csv", "processed_tasks.json"]},
        {
            "src": [
                "__init__.py",
                "data_loader.py",
                "analysis.py",
                "kpi.py",
                "chatbot.py",
                "utils.py",
            ]
        },
        {
            "prompts": [
                "summarization.txt",
                "risks.txt",
                "chatbot.txt",
                "executive_summary.txt",
            ]
        },
        {"outputs": [{"reports": []}, {"logs": []}]},
    ]
}

def create_structure(base, struct):
    for item in struct:
        if isinstance(item, str):  # Create file
            open(os.path.join(base, item), "w").close()
        elif isinstance(item, dict):  # Create directory
            for folder, contents in item.items():
                folder_path = os.path.join(base, folder)
                os.makedirs(folder_path, exist_ok=True)
                create_structure(folder_path, contents)

if __name__ == "__main__":
    for root, contents in structure.items():
        os.makedirs(root, exist_ok=True)
        create_structure(root, contents)
    print("✅ Project structure created successfully!")
