import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MATCH_DB = "data/matches.json"
PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")

def get_upcoming_matches():
    headers = {
        "Authorization": f"Bearer {PANDASCORE_API_KEY}",
        "Accept": "application/json"
    }

    url = "https://api.pandascore.co/csgo/matches/upcoming"
    params = {
        "per_page": 5
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        matches = []
        for match in data:
            opponents = [o["opponent"]["name"] for o in match.get("opponents", [])]
            if len(opponents) < 2:
                continue

            match_info = {
                "match_id": str(match["id"]),
                "team1": opponents[0],
                "team2": opponents[1],
                "time": match["begin_at"]
            }
            matches.append(match_info)

        # Ensure the directory exists
        os.makedirs("data", exist_ok=True)

        # Save the matches
        with open(MATCH_DB, "w") as f:
            json.dump(matches, f, indent=2)

        return matches

    except Exception as e:
        print(f"❌ Failed to fetch matches: {e}")
        return []
