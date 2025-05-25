import json
import os

PREDICTION_DB = 'data/predictions.json'
LEADERBOARD_DB = 'data/leaderboard.json'

def _load(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return {}

def _save(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def add_prediction(user_id, match_id, team_name):
    predictions = _load(PREDICTION_DB)
    user_id = str(user_id)
    if user_id not in predictions:
        predictions[user_id] = []
    predictions[user_id].append({
        "match_id": match_id,
        "team": team_name,
        "result": "pending"
    })
    _save(PREDICTION_DB, predictions)
    return f"Prediction saved: {team_name} to win match {match_id}."

def finalize_predictions(match_id, winner):
    predictions = _load(PREDICTION_DB)
    leaderboard = _load(LEADERBOARD_DB)

    for user_id, preds in predictions.items():
        for p in preds:
            if p['match_id'] == match_id and p['result'] == 'pending':
                if p['team'].lower() == winner.lower():
                    p['result'] = 'correct'
                    leaderboard[user_id] = leaderboard.get(user_id, 0) + 1
                else:
                    p['result'] = 'wrong'

    _save(PREDICTION_DB, predictions)
    _save(LEADERBOARD_DB, leaderboard)
