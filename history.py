import json
import os
import datetime

FILE = "history.json"


def load():
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save(label: str, percentage: int):
    data = load()
    data.append({
        "label": label,
        "percentage": percentage,
        "time": datetime.datetime.now().strftime("%d %b %H:%M"),
    })
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def clear():
    if os.path.exists(FILE):
        os.remove(FILE)