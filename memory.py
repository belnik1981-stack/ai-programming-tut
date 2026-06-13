import json
import os
from config import HISTORY_FILE

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

import datetime

ISSUES_FILE = "data/issues.json"

def log_issue(issue_type, details):
    issues = []
    if os.path.exists(ISSUES_FILE):
        with open(ISSUES_FILE, "r", encoding="utf-8") as f:
            issues = json.load(f)
    issues.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "type": issue_type,
        "details": details
    })
    with open(ISSUES_FILE, "w", encoding="utf-8") as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)

ARCHIVE_THRESHOLD = 50
KNOWLEDGE_FILE = "data/knowledge.md"

def needs_archiving(history):
    return len(history) > ARCHIVE_THRESHOLD

def archive_old_messages(history, max_history_messages):
    """Возвращает (сообщения_для_сжатия, оставшаяся_история)"""
    to_compress = history[:-max_history_messages]
    remaining = history[-max_history_messages:]
    return to_compress, remaining

def append_knowledge(summary_text, issues_context=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## [{timestamp}]\n{summary_text}\n"
    if issues_context:
        entry += f"\n_Технические заметки: {issues_context}_\n"
    with open(KNOWLEDGE_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
