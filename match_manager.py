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
    except Exception as e:
        print(f"[DEBUG] Failed to load matches.json: {e}")
        return []

def _save_matches(matches):
    with open(MATCH_DB, 'w') as f:
        json.dump(matches, f, indent=2)

def get_upcoming_matches():
    print(f"[DEBUG] PANDASCORE_API_KEY = {PANDASCORE_API_KEY}")
    print("[DEBUG] Fetching matches from PandaScore...")
    
    headers = {
        "Authorization": f"Bearer {PANDASCORE_API_KEY}"
    }

    url = "https://api.pandascore.co/cs2/matches/upcoming?per_page=5"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        print("[DEBUG] Raw PandaScore response:")
        print(json.dumps(data, indent=2))

        matches = []
        for match in data:
            if not match.get('opponents') or len(match['opponents']) < 2:
                continue  # skip incomplete entries

            team1 = match['opponents'][0]['opponent']['name']
            team2 = match['opponents'][1]['opponent']['name']
            start_time = match.get('begin_at') or match.get('scheduled_at') or ""

            matches.append({
                "match_id": str(match['id']),
                "time": start_time,
                "team1": team1,
                "team2": team2
            })

        _save_matches(matches)
        print(f"[DEBUG] Saved {len(matches)} matches to cache.")
        return matches

    except Exception as e:
        print(f"[ERROR] Failed to fetch upcoming matches from PandaScore: {e}")
        return []

def resolve_matches():
    matches = _load_matches()
    if not matches:
        print("[DEBUG] No matches to resolve.")
        return []

    headers = {
        "Authorization": f"Bearer {PANDASCORE_API_KEY}"
    }

    resolved = []
    unresolved = []

    for match in matches:
        match_id = match['match_id']
        url = f"https://api.pandascore.co/matches/{match_id}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            match_data = response.json()

            if match_data.get("status") == "finished":
                winner_data = match_data.get("winner")
                winner = winner_data.get("name") if winner_data else None

                if winner:
                    resolved.append(f"Match {match_id} is over! Winner: **{winner}**")
                    finalize_predictions(match_id, winner)
                else:
                    resolved.append(f"Match {match_id} is over, but winner not found.")
            else:
                unresolved.append(match)

        except Exception as e:
            print(f"[ERROR] Could not resolve match {match_id}: {e}")
            unresolved.append(match)

    _save_matches(unresolved)
    return resolved
