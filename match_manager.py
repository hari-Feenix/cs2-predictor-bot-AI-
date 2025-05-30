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
    except:
        return []

def _save_matches(matches):
    with open(MATCH_DB, 'w') as f:
        json.dump(matches, f, indent=2)

def get_upcoming_matches():
    print("[DEBUG] Fetching matches from PandaScore...")
    headers = {
        "Authorization": f"Bearer {PANDASCORE_API_KEY}"
    }
    url = "https://api.pandascore.co/cs2/matches/upcoming?per_page=5"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        matches = []

        for match in data:
            if not match['opponents'] or len(match['opponents']) < 2:
                continue
            team1 = match['opponents'][0]['opponent']['name']
            team2 = match['opponents'][1]['opponent']['name']
            matches.append({
                "match_id": str(match['id']),
                "time": match['begin_at'],
                "team1": team1,
                "team2": team2
            })

        _save_matches(matches)
        print(f"[DEBUG] Saved {len(matches)} matches.")
        return matches

    except Exception as e:
        print(f"[ERROR] Failed to fetch from PandaScore: {e}")
        return []

def resolve_matches():
    matches = _load_matches()
    if not matches:
        return []

    headers = {
        "Authorization": f"Bearer {PANDASCORE_API_KEY}"
    }

    resolved = []
    unresolved = []

    for match in matches:
        url = f"https://api.pandascore.co/matches/{match['match_id']}"
        try:
            response = requests.get(url, headers=headers)
            match_data = response.json()

            if match_data.get("status") == "finished":
                winner = match_data.get("winner", {}).get("name", None)
                if winner:
                    resolved.append(f"Match {match['match_id']} is over! Winner: **{winner}**")
                    finalize_predictions(match['match_id'], winner)
                else:
                    resolved.append(f"Match {match['match_id']} is over! Winner could not be determined.")
            else:
                unresolved.append(match)
        except Exception as e:
            print(f"[ERROR] Could not fetch result for match {match['match_id']}: {e}")
            unresolved.append(match)

    _save_matches(unresolved)
    return resolved
