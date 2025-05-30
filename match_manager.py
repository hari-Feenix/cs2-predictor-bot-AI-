import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
API_KEY = os.getenv("PANDASCORE_API_KEY")

if not API_KEY:
    raise ValueError("❌ Missing PANDASCORE_API_KEY in environment variables.")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

MATCHES_FILE = "data/matches.json"

# Ensure the data directory exists
os.makedirs(os.path.dirname(MATCHES_FILE), exist_ok=True)


def get_upcoming_matches():
    url = "https://api.pandascore.co/csgo/matches/upcoming"
    params = {
        "per_page": 5
    }

    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    matches = response.json()

    cleaned_matches = []
    for match in matches:
        match_id = match.get("id")
        time = match.get("begin_at")
        opponents = [o['opponent']['name'] for o in match.get('opponents', [])]
        if not match_id or not time or len(opponents) != 2:
            continue

        cleaned_matches.append({
            "match_id": str(match_id),
            "time": time,
            "team1": opponents[0],
            "team2": opponents[1],
            "resolved": False,
            "winner": None
        })

    # Save matches locally
    with open(MATCHES_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_matches, f, indent=2)

    return cleaned_matches


def resolve_matches():
    try:
        with open(MATCHES_FILE, "r", encoding="utf-8") as f:
            matches = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    now = datetime.utcnow()
    resolved = []

    for match in matches:
        time_str = match.get("time")
        try:
            match_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        except Exception:
            continue

        if not match["resolved"] and now >= match_time:
            match["winner"] = match["team1"]  # Placeholder logic
            match["resolved"] = True
            resolved.append(match)

    # Save updated list
    with open(MATCHES_FILE, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2)

    return resolved
