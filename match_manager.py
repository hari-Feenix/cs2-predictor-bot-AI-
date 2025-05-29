from openai import OpenAI
import os
import json
from datetime import datetime
import random

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
    matches = _load_matches()
    if not matches:
        try:
            print("[DEBUG] Starting OpenAI API call")
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            prompt = (
                "Generate 5 upcoming professional Counter-Strike 2 matches. "
                "Each match should be a dictionary with match_id, time (format: YYYY-MM-DD HH:MM:SS), "
                "team1, and team2. Format the entire response as a **JSON array only** with no explanation or extra text."
            )

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.choices[0].message.content.strip()
            print("=== OpenAI Response ===")
            print(content)

            try:
                matches = json.loads(content)
                _save_matches(matches)
            except Exception as parse_err:
                print("[ERROR] JSON parsing failed.")
                print(f"Parse Exception: {parse_err}")
                print("Trying eval() fallback.")
                matches = eval(content)
                _save_matches(matches)

        except Exception as e:
            print("[ERROR] Failed to get OpenAI match data:")
            print(e)
            return []

    return matches

def resolve_matches():
    matches = _load_matches()
    now = datetime.utcnow()
    resolved = []
    unresolved = []

    for match in matches:
        match_time = datetime.strptime(match['time'], '%Y-%m-%d %H:%M:%S')
        if match_time <= now:
            winner = random.choice([match['team1'], match['team2']])
            match['winner'] = winner
            resolved.append(f"Match {match['match_id']} is over! Winner: **{winner}**")

            from prediction_manager import finalize_predictions
            finalize_predictions(match['match_id'], winner)
        else:
            unresolved.append(match)

    _save_matches(unresolved)
    return resolved
