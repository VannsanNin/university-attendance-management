import json
import os

SESSION_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "session.json")


def save_session(username, password):
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"username": username, "password": password}, f)
    except OSError:
        pass


def load_session():
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("username") and data.get("password"):
            return data
    except (OSError, ValueError):
        pass
    return None


def clear_session():
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except OSError:
        pass
