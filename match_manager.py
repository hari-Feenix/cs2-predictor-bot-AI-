import os
import json
import requests
from datetime import datetime
from prediction_manager import predictions, update_leaderboard

PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")
MATCHES_FILE = "data/matches.json"
HEADERS = {
    "Authorization": f"Bearer {PANDASCORE_API_KEY}"
}
CSGO_MATCHES_ENDPOINT = "https://api.pandascore.co/csgo/matches/upcoming"


def fetch_upcoming_matches(limit=5):
    params = {"per_page": limit}
    try:
        response = requests.get(CSGO_MATCHES_ENDPOINT, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching matches: {e}")
        return []


def get_upcoming_matches():
    matches = fetch_upcoming_matches()
    if not matches:
        return []

    simplified = []
    for match in matches:
        match_id = str(match.get("id"))
        team1 = match.get("opponents", [{}])[0].get("opponent", {}).get("name", "TBD")
        team2 = match.get("opponents", [{}])[1].get("opponent", {}).get("name", "TBD")
        start_time = match.get("begin_at")
        status = match.get("status", "unknown")

        simplified.append({
            "id": match_id,
            "team1": team1,
            "team2": team2,
            "start_time": start_time,
            "status": status
        })

    try:
        os.makedirs(os.path.dirname(MATCHES_FILE), exist_ok=True)
        with open(MATCHES_FILE, "w", encoding="utf-8") as f:
            json.dump(simplified, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to save matches: {e}")

    return simplified


def resolve_matches():
    try:
        with open(MATCHES_FILE, "r", encoding="utf-8") as f:
            matches = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"⚠️ Could not load matches.json: {e}")
        return []

    unresolved = []
    resolved_msgs = []
    now = datetime.utcnow()

    for match in matches:
        # For testing, we assume the match is complete if start_time < now
        if match.get("start_time"):
            try:
                match_time = datetime.fromisoformat(match["start_time"].replace("Z", "+00:00"))
            except ValueError:
                match_time = now  # fallback
        else:
            match_time = now

        if match_time < now:
            user_prediction = predictions.get(match["id"])
            if user_prediction:
                # Mock winner for now
                winner = match["team1"]  # or use actual API if available
                update_leaderboard(user_prediction["user"], winner == user_prediction["predicted"])
                msg = f"{match['team1']} vs {match['team2']} - Winner: {winner} ✅"
                resolved_msgs.append(msg)
        else:
            unresolved.append(match)

    try:
        with open(MATCHES_FILE, "w", encoding="utf-8") as f:
            json.dump(unresolved, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to update unresolved matches: {e}")

    return resolved_msgs
