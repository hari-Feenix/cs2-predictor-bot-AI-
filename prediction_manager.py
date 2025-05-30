import json
import os

PREDICTIONS_FILE = "data/predictions.json"
LEADERBOARD_FILE = "data/leaderboard.json"

os.makedirs("data", exist_ok=True)

def _load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        # corrupted or non-json file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("{}")
        return {}

def _save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

predictions = _load_json(PREDICTIONS_FILE)
leaderboard = _load_json(LEADERBOARD_FILE)

def save_prediction(match_id, user_id, team_name):
    if match_id not in predictions:
        predictions[match_id] = {}
    predictions[match_id][str(user_id)] = team_name
    _save_json(predictions, PREDICTIONS_FILE)

def update_leaderboard(user_id, correct=True):
    user_id = str(user_id)
    if user_id not in leaderboard:
        leaderboard[user_id] = 0
    if correct:
        leaderboard[user_id] += 1
    _save_json(leaderboard, LEADERBOARD_FILE)

def add_prediction(user_id, match_id, team_name):
    save_prediction(match_id, user_id, team_name)
    return f"✅ Prediction saved: `{team_name}` for match `{match_id}`"

def get_leaderboard():
    return dict(sorted(leaderboard.items(), key=lambda x: x[1], reverse=True))
