import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "assignments.json")


def load():
    if not os.path.exists(DATA_FILE):
        return {"assignments": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def next_id(data):
    ids = [a["id"] for a in data["assignments"]]
    return max(ids) + 1 if ids else 1
