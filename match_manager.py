import requests
import os
import json
from datetime import datetime
from prediction_manager import finalize_predictions

API_KEY = os.getenv("PANDASCORE_API_KEY")
BASE_URL = "https://api.pandascore.co/csgo/matches/upcoming"
RESULTS_URL = "https://api.pandascore.co/csgo/matches"  # to resolve
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

MATCH_DB = "data/matches.json"

def _load_matches():
    try:
        with open(MATCH_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return []

def _save_matches(matches):
    with open(MATCH_DB, "w") as f:
        json.dump(matches, f, indent=2)

def get_upcoming_matches():
    response = requests.get(BASE_URL, headers=HEADERS, params={"per_page": 5})
    response.raise_for_status()
    data = response.json()

    matches = []
    for match in data:
        match_id = match["id"]
        time_str = match["begin_at"]
        opponents = [o["opponent"]["name"] for o in match.get("opponents", [])]
        if not time_str or len(opponents) != 2:
            continue

        matches.append({
            "match_id": match_id,
            "time": time_str,
            "team1": opponents[0],
            "team2": opponents[1],
            "winner": None
        })

    _save_matches(matches)
    return matches

def resolve_matches():
    unresolved = _load_matches()
    resolved = []

    for match in unresolved[:]:
        match_id = match["match_id"]
        url = f"https://api.pandascore.co/csgo/matches/{match_id}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            continue

        match_data = resp.json()
        if match_data["status"] != "finished":
            continue

        winner_obj = match_data.get("winner")
        if not winner_obj:
            continue

        winner_name = winner_obj["name"]
        match["winner"] = winner_name
        resolved.append(f"{match['team1']} vs {match['team2']} — Winner: **{winner_name}**")
        finalize_predictions(str(match_id), winner_name)
        unresolved.remove(match)

    _save_matches(unresolved)
    return resolved
