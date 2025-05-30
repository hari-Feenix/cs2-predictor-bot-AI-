import os
import json
import requests
from datetime import datetime
from prediction_manager import predictions, update_leaderboard

PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")
MATCHES_FILE = "data/matches.json"
LOG_FILE = "data/logs.json"

HEADERS = {
    "Authorization": f"Bearer {PANDASCORE_API_KEY}"
}
CSGO_MATCHES_ENDPOINT = "https://api.pandascore.co/csgo/matches/upcoming"
CSGO_MATCH_DETAILS_ENDPOINT = "https://api.pandascore.co/csgo/matches"

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

def get_winner_from_pandascore(match_id):
    try:
        response = requests.get(
            f"{CSGO_MATCH_DETAILS_ENDPOINT}/{match_id}",
            headers=HEADERS
        )
        if response.status_code == 200:
            data = response.json()
            return data["winner"]["name"] if data.get("winner") else None
    except Exception as e:
        print(f"⚠️ Failed to fetch winner for match {match_id}: {e}")
    return None

def log_correct_prediction(user_id, match_id, team):
    log = []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    log.append({
        "user_id": user_id,
        "match_id": match_id,
        "team": team,
        "timestamp": datetime.utcnow().isoformat()
    })

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

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
        match_id = match.get("id")
        start_time = match.get("start_time")

        if start_time:
            try:
                match_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                match_time = now
        else:
            match_time = now

        if match_time < now:
            winner = get_winner_from_pandascore(match_id)
            if not winner:
                unresolved.append(match)
                continue

            predictions_for_match = predictions.get(match_id, {})
            mentions = []

            for user_id, predicted_team in predictions_for_match.items():
                correct = (predicted_team == winner)
                update_leaderboard(user_id, correct)
                if correct:
                    log_correct_prediction(user_id, match_id, winner)
                    mentions.append(f"<@{user_id}>")

            mention_text = "🎉 " + ", ".join(mentions) + " guessed correctly!" if mentions else "😢 No one got it right."
            msg = f"{match['team1']} vs {match['team2']} - Winner: **{winner}** ✅\n{mention_text}"
            resolved_msgs.append(msg)
        else:
            unresolved.append(match)

    try:
        with open(MATCHES_FILE, "w", encoding="utf-8") as f:
            json.dump(unresolved, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to update unresolved matches: {e}")

    return resolved_msgs
