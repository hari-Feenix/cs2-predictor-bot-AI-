import json
import os

PREDICTIONS_FILE = "data/predictions.json"
LEADERBOARD_FILE = "data/leaderboard.json"

def _load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# --- Core functions ---
def save_prediction(user, match_id, team):
    predictions.setdefault(match_id, {})[user] = team
    _save_json(PREDICTIONS_FILE, predictions)

def update_leaderboard(user, correct):
    if correct:
        leaderboard[user] = leaderboard.get(user, 0) + 1
        _save_json(LEADERBOARD_FILE, leaderboard)

def get_leaderboard():
    return sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

# --- REQUIRED EXPORTS ---
predictions = _load_json(PREDICTIONS_FILE)
leaderboard = _load_json(LEADERBOARD_FILE)
