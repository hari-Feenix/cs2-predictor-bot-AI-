import os
import json
import requests
from datetime import datetime
from prediction_manager import finalize_predictions

PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")
MATCH_DB = 'data/matches.json'

def _load_matches():
    try:
        with open(MATCH_DB, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def _save_matches(matches):
    with open(MATCH_DB, 'w') as f:
        json.dump(matches, f, indent=2)

def get_upcoming_matches():
    print(f"[DEBUG] PANDASCORE_API_KEY = {PANDASCORE_API_KEY}")
    headers = {"Authorization": f"Bearer {PANDASCORE_API_KEY}"}
    url = "https://api.pandascore.co/cs2/matches/upcoming?per_page=5"

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        print("[DEBUG] Raw API response:")
        print(json.dumps(data, indent=2))

        matches = []
        for match in data:
            opponents = match.get("opponents", [])
            if len(opponents) < 2:
                continue
            match_info = {
                "match_id": str(match["id"]),
                "time": match.get("begin_at") or match.get("scheduled_at"),
                "team1": opponents[0]["opponent"]["name"],
                "team2": opponents[1]["opponent"]["name"]
            }
            matches.append(match_info)

        _save_matches(matches)
        return matches

    except Exception as e:
        print(f"[ERROR] Failed to get matches: {e}")
        return []

def resolve_matches():
    headers = {"Authorization": f"Bearer {PANDASCORE_API_KEY}"}
    matches = _load_matches()
    resolved, unresolved = [], []

    for match in matches:
        match_id = match["match_id"]
        url = f"https://api.pandascore.co/matches/{match_id}"

        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            data = res.json()

            if data.get("status") == "finished":
                winner = data.get("winner", {}).get("name")
                if winner:
                    resolved.append(f"✅ Match {match_id} done! Winner: **{winner}**")
                    finalize_predictions(match_id, winner)
            else:
                unresolved.append(match)

        except Exception as e:
            print(f"[ERROR] Could not resolve match {match_id}: {e}")
            unresolved.append(match)

    _save_matches(unresolved)
    return resolved
